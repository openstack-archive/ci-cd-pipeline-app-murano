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

default_packages="Puppet SystemConfig OpenLDAP Gerrit Jenkins Zuul Nodepool CiCdEnvironment"
source_dir="murano-apps"
destination_dir="."
refresh_existing_packages=false
upload=false
upload_without_build=false

help_string="$(basename "$0") [-h] [-s source_dir] [-d destination_dir] [-p package_name] -- script to build packages for downloading to Murano

where:
    -h  show this help message.

  build packages options:
    -r  flag to update existing packages, if these files are already in the destination directory. Without this flag old packages will be removed.
    -s  set the path to directory with list of source packages. (default is: $source_dir)
    -d  set the path to output directory, where zipped packages should be placed. (default is: $destination_dir)
    -p  set package name, which need to archive. (default is: $default_packages)

  upload packages options:
    -u  upload new packages to specified tenant from directory specified with -d option
        !!!  with building them  !!! (it requires muranoclient installation)
        if this option is set, old packages will be removed from tenant and new will be imported instead.
    -U  upload new packages to specified tenant from directory specified with -d option
        !!!  without building them  !!! (it requires muranoclient installation)
        if this option is set, old packages will be removed from tenant and new will be imported instead.
    -e  name of environmanet, which will be created

For using muranoclient please also specify necessary credentials in environment:
    export OS_USERNAME=user
    export OS_PASSWORD=password
    export OS_TENANT_NAME=tenant
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0
    export MURANO_URL=http://murano.example.com:8082/

Examples
--------

Build Gerrit and Jenkins:
./tools/build_packages.sh -s $source_dir -d $destination_dir -p Gerrit -p Jenkins

Build all packages with default settings:
./tools/build_packages.sh -s $source_dir -d $destination_dir
    "


while getopts ':huUs:d:p:e:' option; do
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
    u) upload=true
       ;;
    U) upload_without_build=true
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       exit 1
       ;;
  esac
done

# check that both upload options are not used in the same time
if $upload && $upload_without_build ; then
    echo "Options -U and -u can not be used in the same time. Please choose only one."
    exit 1
fi

# set default value for packages
if [ ${#packages[@]} -eq 0 ]; then
    packages=$default_packages
fi

# check both directories
for d in $source_dir $destination_dir; do
    check_dir $d
done

# set distination dir
# if it's absolute - it will not be changed, otherwise
# will be used: current_user_rdir+destination_dir

if [[ "$destination_dir" = /* ]] ; then
    destination_dir=$destination_dir
else
    destination_dir="`pwd`/$destination_dir"
fi

# skip bilding packages if it's necessary
if ! $upload_without_build ; then
    # zip necessary apps
    pushd $source_dir
        for d in $packages; do
            filename="$destination_dir/io.murano.opaas.$d.zip"
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

# upload packages
if $upload || $upload_without_build ; then
    # check, that muranoclient is available
    if ! hash murano 2>/dev/null; then
        echo "Murano client is not available, please install it if you want to use it."
        exit 1
    fi
    # upload files in correct order as described in default_packages
    for d in $default_packages; do
        filename="$destination_dir/io.murano.opaas.$d.zip"
        murano package-import $filename --exists-action u
    done
    # if env name is specified, then create environment
    if [ ! -z $env_name ] ; then
        murano environment-create $env_name
    fi
fi
