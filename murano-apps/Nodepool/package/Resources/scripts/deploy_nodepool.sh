#!/bin/bash

logger Deploying Nodepool...

/bin/bash ./gen_rsa_key.sh

mkdir /etc/puppet/modules/nodepool_configure
mkdir /etc/puppet/modules/nodepool_configure/manifests
mkdir /etc/puppet/modules/nodepool_configure/templates

cp nodepool_configure/manifests/init.pp /etc/puppet/modules/nodepool_configure/manifests/
cp nodepool_configure/templates/nodepool.yaml.erb /etc/puppet/modules/nodepool_configure/templates/

puppet apply site.pp

exit
