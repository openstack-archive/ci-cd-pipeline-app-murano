#!/bin/bash

logger Cloning openstack-ci system-config

git clone https://review.fuel-infra.org/open-paas/system-config

logger Installing openstack-ci system-config

cd system-config
./install_modules.sh

cp -r modules/ /etc/puppet/

# Should be installed on the each node to use
# domain2dn function
puppet module install datacentred-ldap