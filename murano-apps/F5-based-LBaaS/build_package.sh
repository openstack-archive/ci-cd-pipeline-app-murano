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

pushd package
  cp -v -r Classes Resources UI manifest.yaml logo.png ../tmp/
popd

archive_name=f5-lbaas-driver.tar.gz
f5_directory_name=f5_lbaas_driver-0.0.1

# Pack python tarball.
pushd tmp/Resources/scripts
  tar -czvf $archive_name $f5_directory_name/*
  base64 $archive_name > $archive_name.bs64
  rm -rf $f5_directory_name
  rm -rf $archive_name
popd

# Make murano package.
pushd tmp
  zip -r ../F5_based_LBaaS.zip .
popd
