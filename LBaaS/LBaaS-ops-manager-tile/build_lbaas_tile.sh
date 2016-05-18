# Stop the script if an error occurs.
set -e

# Pack jobs and packages.
cd releases/jobs;

pushd lbaas-config
  tar zcvf lbaas-config.tgz *;
  mv lbaas-config.tgz ../
popd

pushd delete-lbaas
  tar zcvf delete-lbaas.tgz *;
  mv delete-lbaas.tgz ../
popd

cd ../packages;

pushd python/python
  aptitude download binutils build-essential cpp cpp-4.8 dpkg-dev fakeroot g++-4.8 gcc gcc-4.8 libalgorithm-diff-perl \
  libalgorithm-diff-xs-perl libalgorithm-merge-perl libasan0 libatomic1 libc6-dev libc-dev-bin libcloog-isl4 \
  libdpkg-perl libfakeroot libffi6 libffi-dev libfile-fcntllock-perl libgcc-4.8-dev libgmp10 libgomp1 libisl10 \
  libitm1 libmpc3 libmpfr4 libquadmath0 libssl-dev libssl-doc libstdc++-4.8-dev libtsan0 linux-libc-dev make \
  manpages-dev manpages zlib1g-dev

  wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
popd

pushd python
  tar zcvf python.tgz *;
  mv python.tgz ../
popd

cd ../..

mkdir tmp

cp -r metadata tmp/

mkdir tmp/releases
mkdir tmp/releases/jobs
mkdir tmp/releases/packages

mv releases/jobs/lbaas-config.tgz tmp/releases/jobs/
mv releases/jobs/delete-lbaas.tgz tmp/releases/jobs/
mv releases/packages/python.tgz tmp/releases/packages/

# In this case cp returns exit code 1 (it copies only files without nested directories).
set +e
cp releases/* tmp/releases/
set -e

# Put correct sha1 to release.MF
if [ "$(uname -s)" == "Darwin" ]; then
    # Mac OS X.
    sha1_lbaas_job=$(openssl sha1 tmp/releases/jobs/lbaas-config.tgz | cut -d '=' -f 2)
    sha1_delete_lbaas_job=$(openssl sha1 tmp/releases/jobs/delete-lbaas.tgz | cut -d '=' -f 2)
    sha1_python_package=$(openssl sha1 tmp/releases/packages/python.tgz | cut -d '=' -f 2)
else
    # Works for Linux.
    sha1_lbaas_job=$(sha1sum tmp/releases/jobs/lbaas-config.tgz | cut -d ' ' -f 1)
    sha1_delete_lbaas_job=$(sha1sum tmp/releases/jobs/delete-lbaas.tgz | cut -d ' ' -f 1)
    sha1_python_package=$(sha1sum tmp/releases/packages/python.tgz | cut -d ' ' -f 1)
fi

sed -i -e "s/%sha1_python_package%/${sha1_python_package}/g" tmp/releases/release.MF
sed -i -e "s/%sha1_lbaas_job%/${sha1_lbaas_job}/g" tmp/releases/release.MF
sed -i -e "s/%sha1_delete_lbaas_job%/${sha1_delete_lbaas_job}/g" tmp/releases/release.MF

# Pack the release.
cd tmp/releases;
tar zcvf example-release-10.tgz *;
cd ../..

# Enable option 'extended globbing' for easy deletion.
shopt -s extglob

# Delete all files except the release archive.
rm -rf tmp/releases/!(example-release-10.tgz)

# Pack tile.
cd tmp;
zip -r lbaas-tile.zip *;
cd ..
mv tmp/lbaas-tile.zip .

# Delete temp directory.
rm -rf tmp

# Delete downloaded debs and Python.
set +e
rm releases/packages/python/python/*.deb
rm releases/packages/python/python/Python-3.5.0.tgz
