#!/bin/bash

URL="$1"
STABLE_FLAG=$2

logger Cloning openstack-ci system-config

if $STABLE_FLAG ; then
   git clone $URL --branch "stable"
else
  git clone $URL
fi

logger Installing openstack-ci system-config

cd system-config
./install_modules.sh

cp -r modules/ /etc/puppet/

# Should be installed on the each node to use
# domain2dn function
puppet module install datacentred-ldap
