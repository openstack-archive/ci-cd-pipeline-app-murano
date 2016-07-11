#!/bin/bash

URL="$1"
BRANCH="$2"
PATCH_ID="$3"

logger Cloning openstack-ci system-config

gclonecd() {
    git clone "$1" && cd "$(basename "$1")"
}

if [ -n $PATCH_ID ] ; then
   gclonecd $URL
   patch_ref=`git ls-remote | grep $PATCH_ID | tail -1 | awk '{print $2}'`
   git fetch $URL $patch_ref && git checkout "FETCH_HEAD"
elif [-n $BRANCH ] ; then
  git clone $URL --branch $BRANCH
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
