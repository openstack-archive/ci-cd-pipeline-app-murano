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

default_packages="CiCdEnvironment Gerrit Jenkins Nodepool OpenLDAP Puppet SystemConfig Zuul"
source_dir="murano-apps"
destination_dir="."
update_existing_packages=false

help_string="$(basename "$0") [-h] [-s source_dir] [-d destination_dir] [-p package_name] -- script to build packages for downloading to Murano

where:
    -h  show this help message.
    -U  flag to update existing packages, if these files are already in the destination directory. Without this flag old packages will be removed.
    -s  set the path to directory with list of source packages. (default is: $source_dir)
    -d  set the path to output directory, where zipped packages should be placed. (default is: $destination_dir)
    -p  set package name, which need to archive. (default is: $default_packages)

Examples
--------

Build Gerrit and Jenkins:
./tools/build_packages.sh -s $source_dir -d $destination_dir -p Gerrit -p Jenkins

Build all packages with default settings:
./tools/build_packages.sh -s $source_dir -d $destination_dir
    "


while getopts ':hNs:d:p:' option; do
  case "$option" in
    h) echo "$help_string"
       exit
       ;;
    U) update_existing_packages=true
       ;;
    s) source_dir=$OPTARG
       ;;
    d) destination_dir=$OPTARG
       ;;
    p) packages+=("$OPTARG")
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$help_string" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$help_string" >&2
       exit 1
       ;;
  esac
done

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

# zip necessary apps
pushd $source_dir
    for d in $packages; do
        filename="$destination_dir/io.murano.opaas.$d.zip"
        pushd $d/package
        # check that file exist and remove it or create new version
        if [ -f $filename ] ; then
            if ! $update_existing_packages ; then
                rm $filename
            fi
        fi
        zip -r $filename *
        popd
    done

popd

