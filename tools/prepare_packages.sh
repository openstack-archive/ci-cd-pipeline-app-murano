#!/bin/bash

# function for checking directories
function check_dir () {
    if [[ -z "$1" ]]; then
        echo "No directory name provided."
        exit
    fi

    if [[ ! -d "${1}" ]]; then
        echo "Folder '${1}' doesn't exist."
        exit
    fi
}

default_packages="Puppet SystemConfig CiCdUtils OpenLDAP Gerrit Jenkins Zuul Nodepool CiCdEnvironment"
source_dir="murano-apps"
destination_dir="."
refresh_existing_packages=false
upload=false
build_packages=true

help_string="$(basename "$0") [-h] [-s source_dir] [-d destination_dir] [-p package_name] -- script to build packages for downloading to Murano

where:
    -h  show this help message.

  build packages options:
    -S  flag to skip building of packages.  if it's specified - script will not build new packages.
    -r  flag to update existing packages, if these files are already in the destination directory. Without this flag old packages will be removed.
    -s  set the path to directory with list of source packages. (default is: $source_dir)
    -d  set the path to output directory, where zipped packages should be placed. (default is: $destination_dir)
    -p  set package name, which need to archive. (default is: $default_packages)

  upload packages options (they require muranoclient installation):
    -U  upload new packages to specified tenant from directory specified with -d option
        if this option is set, old packages will be removed from tenant and new will be imported instead.
    -e  name of environment, which will be created

For using muranoclient please also specify necessary credentials in environment:
    export OS_USERNAME=user
    export OS_PASSWORD=password
    export OS_TENANT_NAME=tenant
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0
    export MURANO_URL=http://murano.example.com:8082/

Examples
--------

Build Gerrit and Jenkins:
./tools/prepare_packages.sh -s $source_dir -d $destination_dir -p Gerrit -p Jenkins

Build all packages with default settings:
./tools/prepare_packages.sh -s $source_dir -d $destination_dir
or
./tools/prepare_packages.sh

Upload existing packages without building them:
./tools/prepare_packages.sh -S -U -d $destination_dir
"

while getopts ':hUSs:d:p:e:' option; do
  case "$option" in
    h) echo "$help_string"
       exit
       ;;
    e) env_name=$OPTARG
       ;;
    r) refresh_existing_packages=true
       ;;
    s) source_dir=$OPTARG
       ;;
    d) destination_dir=$OPTARG
       ;;
    p) packages+=("$OPTARG")
       ;;
    U) upload=true
       ;;
    S) build_packages=false
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       exit 1
       ;;
  esac
done


# set default value for packages
if [ ${#packages[@]} -eq 0 ]; then
    packages=$default_packages
fi

# make sure, that we need upload or build packages
# if - yes, then define destination dir
if $build_packages || $upload ; then
    # check destination dir
    check_dir $destination_dir

    # set distination dir
    # if it's absolute - it will not be changed, otherwise
    # will be used: current_user_rdir+destination_dir
    if [[ "$destination_dir" = /* ]] ; then
        destination_dir=$destination_dir
    else
        destination_dir="`pwd`/$destination_dir"
    fi
else
    echo "NOTE: Packages will not be built or uploaded. Use options -S or -U to change it."
fi


### BUILDING PACKAGES ###
if $build_packages ; then
    # check source dir
    check_dir $source_dir

    # zip necessary apps
    pushd $source_dir
        for d in ${packages[@]}; do
            filename="$destination_dir/org.openstack.ci_cd_pipeline_murano_app.$d.zip"
            pushd $d/package
            # check that file exist and remove it or create new version
            if [ -f $filename ] ; then
                if ! $refresh_existing_packages ; then
                    rm $filename
                fi
            fi
            zip -r $filename *
            popd
        done
    popd
fi

### UPLOADING PACKAGES ###
# Follow part uses Murano client, so let's
# check, that muranoclient is available
if ! hash murano 2>/dev/null; then
    echo "Murano client is not available, please install it if you want to use it."
    exit 1
fi

# upload packages
if $upload ; then
    # to have ability upload one package independently we need to remove it
    # via client and then upload it without updating its dependencies
    for d in ${packages[@]}; do
        filename="$destination_dir/org.openstack.ci_cd_pipeline_murano_app.$d.zip"
        pkg_id=`murano package-list --owned | grep $d | awk '{print $2}'`
        murano package-delete $pkg_id
        murano package-import $filename --exists-action s
    done
fi

# if env name is specified, then create environment
if [ ! -z $env_name ] ; then
    murano environment-create $env_name
fi
