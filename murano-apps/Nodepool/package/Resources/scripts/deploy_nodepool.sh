#!/bin/bash

logger Deploying Nodepool...

mkdir -p /etc/puppet/modules/nodepool_configure
mkdir -p /etc/puppet/modules/nodepool_configure/manifests
mkdir -p /etc/puppet/modules/nodepool_configure/templates

cp nodepool_configure/manifests/init.pp /etc/puppet/modules/nodepool_configure/manifests/
cp nodepool_configure/templates/nodepool.yaml.erb /etc/puppet/modules/nodepool_configure/templates/

puppet apply site.pp

exit
