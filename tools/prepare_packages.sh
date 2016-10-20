#!/bin/bash

# function for checking directories
function check_dir () {
    if [[ -z "$1" ]]; then
        echo "ERROR: No directory name provided."
        exit
    fi

    if [[ ! -d "${1}" ]]; then
        echo "ERROR: Folder '${1}' doesn't exist."
        exit
    fi
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source_dir="murano-apps"
destination_dir="."
refresh_existing_packages=false
upload=false
build_packages=true
action_for_dependency='s'

HOST='example.com'
DEP_OPTS='s a u'

help_string="$(basename "$0") [-h] [-s source_dir] [-d destination_dir] [-p package_name] -- script to build packages for downloading to Murano

where:
    -h  show this help message.

  build packages options:
    -S  flag to skip building of packages.  if it's specified - script will not build new packages.
    -r  flag to update existing packages, if these files are already in the destination directory. Without this flag old packages will be removed.
    -s  set the path to directory with list of source packages. (default is: $source_dir)
    -d  set the path to output directory, where zipped packages should be placed. (default is: $destination_dir)
    -p  set package name, which need to archive. (default is: $DEFAULT_PACKAGES_LIST)
    -H  Ip address of the Openstack used in endpoints

  upload packages options (they require muranoclient installation):
    -U  upload new packages to specified tenant from directory specified with -d option
        if this option is set, old packages will be removed from tenant and new will be imported instead.
    -a  Default action when a dependency package already
        exists: (s)kip, (u)pdate, (a)bort. Default value is: (s)kip.
    -e  name of environment, which will be created

For using muranoclient please also specify necessary credentials in environment:
    export OS_USERNAME=user
    export OS_PASSWORD=password
    export OS_TENANT_NAME=tenant

    To use non default backend please export follow option.
    Default value is defined in /etc/murano/murano.conf

    export MURANO_PACKAGES_SERVICE=glare

    Follow endpoints will be set automatially, with provided $HOST (variable mentioned with -H option),
    if they are not exported already:

    export GLARE_URL=http://$HOST:9494/
    export OS_AUTH_URL=http://$HOST:5000/v2.0
    export MURANO_URL=http://$HOST:8082/

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

while getopts ':hUSs:d:p:e:a:H:' option; do
  case "$option" in
    h) echo "$help_string"
       exit
       ;;
    H) HOST=$OPTARG
       ;;
    e) env_name=$OPTARG
       ;;
    a) action_for_dependency=$OPTARG
       if ! [[ $DEP_OPTS =~ $OPTARG ]] ; then
           echo "ERROR: action should be one of the '$DEP_OPTS'."
           exit 1
       fi
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

if [ "$HOST" = 'example.com' ] ; then
    echo "ERROR: please specify correct HOST (option -H) to get access to Openstack APIs"
    exit 1
fi

# check and define endpoints

: "${MURANO_URL:?MURANO_URL is not set. Try to execute command: export MURANO_URL=http://$HOST:8082/}"
: "${GLARE_URL:?GLARE_URL is not set. Try to execute command: export GLARE_URL=http=http://$HOST:9494/}"
: "${OS_AUTH_URL:?OS_AUTH_URL is not set. Try to execute command: export OS_AUTH_URL=http=http://$HOST:5000/v2.0}"

# import default packages_list, if exist
if [ -f "${DIR}/default_packages_list.sh" ]; then
    if [ -z "${DEFAULT_PACKAGES_LIST}" ]; then
      source "${DIR}/default_packages_list.sh"
      echo "INFO: Packages list has been imported from default_packages_list.sh file"
   fi
fi

# set default value for packages
if [ ${#packages[@]} -eq 0 ]; then
    if [ ${#DEFAULT_PACKAGES_LIST[@]} -eq 0 ]; then
      echo -e "ERROR: No Packages list has been passed!Please check help\n${help_string}"
      exit 1
    fi
    packages="${DEFAULT_PACKAGES_LIST}"
fi

# make sure, that we need upload or build packages
# if - yes, then define destination dir
if $build_packages || $upload ; then
    # check destination dir
    check_dir "$destination_dir"

    # set distination dir
    # if it's absolute - it will not be changed, otherwise
    # will be used: current_user_rdir+destination_dir
    if [[ "$destination_dir" = /* ]] ; then
        destination_dir=$destination_dir
    else
        destination_dir="$(pwd)/$destination_dir"
    fi
else
    echo "INFO: Packages will not be built or uploaded. So remove -S or use -U to make any action."
fi


### BUILDING PACKAGES ###
if $build_packages ; then
    # check source dir
    check_dir "$source_dir"

    # zip necessary apps
    pushd "$source_dir"
        for d in ${packages[*]}; do
            # check that package is realy existed
            check_dir "$d"
            # get FQN for creating package
            package_name="$(grep FullName "$d/package/manifest.yaml" | awk '{print $2}')"
            filename="$destination_dir/$package_name.zip"
            pushd "$d/package"
            # check that file exist and remove it or create new version
            if [ -f "$filename" ] ; then
                if ! $refresh_existing_packages ; then
                    rm "$filename"
                fi
            fi
            zip -r "$filename" ./*
            popd
        done
    popd
fi

### UPLOADING PACKAGES ###
# Follow part uses Murano client, so let's
# check, that muranoclient is available
if ! hash murano 2>/dev/null; then
    echo "INFO: Murano client is not available, please install it if you want to use it."
    exit 1
fi

# upload packages
if $upload ; then
    # to have ability upload one package independently we need to remove it
    # via client and then upload it without updating its dependencies
    val="${packages[@]}"
    for d in $val; do
        filename="$(find "$destination_dir" -maxdepth 1 -name "*$d*")"
        pkg_id=$(murano package-list --owned | grep "$d" | awk '{print $2}')
        murano package-delete "$pkg_id"
        murano package-import "$filename" --exists-action s --dep-exists-action "$action_for_dependency"
    done
fi

# if env name is specified, then create environment
if [ ! -z "$env_name" ] ; then
    murano environment-create "$env_name"
fi
