Setup
-------
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
