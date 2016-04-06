# Stop the script if an error occurs.
set -e

function cleanup {
  cd $SCRIPTPATH
  rm -rf tmp
}

# In case if script is running not where it is located.
cd $(dirname $0)
SCRIPTPATH=`pwd`

# Cleanup tmp dir on script exit.
trap 'cleanup' EXIT

mkdir tmp

cp -v -r Classes Resources manifest.yaml tmp/

archive_name=lbaas.tar.gz
lbaas_directory_name=lbaas_api-0.1

# Pack python tarball.
pushd tmp/Resources/scripts
  tar -czvf $archive_name $lbaas_directory_name/*
  base64 $archive_name > $archive_name.bs64
  rm -rf $lbaas_directory_name
  rm -rf $archive_name
popd

# Make murano package.
pushd tmp
  zip -r ../LBaaS_Library.zip .
popd
