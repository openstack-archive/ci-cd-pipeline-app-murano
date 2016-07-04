#!/usr/bin/env bash

# As described in https://bugs.launchpad.net/murano/+bug/1598232
# murano-agent set the working directory depending on where the script
# is located. Check and set working directory to the root of the
# temporary folder which created by murano for the current execution plan
# This code must work even if LP1598232 will be fixed

if [ -d ../core ]
then
    cd ..
fi

set +e

puppet apply --detailed-exitcodes --color=false "site.pp"

PUPPET_RETURN=$?
if [ "${PUPPET_RETURN}" -eq 4 ] || [ "${PUPPET_RETURN}" -eq 6 ] ; then
    exit ${PUPPET_RETURN}
fi

set -e