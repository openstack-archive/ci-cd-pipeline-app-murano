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
cp releases/* tmp/releases/

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
