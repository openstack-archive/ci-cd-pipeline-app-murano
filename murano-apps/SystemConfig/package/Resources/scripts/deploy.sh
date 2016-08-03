#!/bin/bash

URL="$1"
BRANCH="$2"
PATCH_ID="$3"

logger Cloning openstack-ci system-config

repository_name="$(basename "$URL")"

if [ -n "$PATCH_ID" ] ; then
   git clone "$URL"
   pushd "$repository_name"
       patch_ref=$(git ls-remote | grep "$PATCH_ID" | tail -1 | awk '{print $2}')
       if [ -z "$patch_ref" ] ; then
           echo "Patch id $PATCH_ID is not correct."
           exit 1
       fi
       git fetch "$URL" "$patch_ref" && git checkout "FETCH_HEAD"
   popd
elif [ -n "$BRANCH" ] ; then
  git clone "$URL" --branch "$BRANCH"
else
  git clone "$URL"
fi

logger Installing openstack-ci system-config

pushd "$repository_name"
    ./install_modules.sh

    cp -r modules/ /etc/puppet/

    # Should be installed on the each node to use
    # domain2dn function
    puppet module install datacentred-ldap
popd
