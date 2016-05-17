#!/usr/bin/env bash

set +e

PUPPET_CODE=`echo -n $1 | base64 -d`

puppet apply --detailed-exitcodes --color=false --execute "${PUPPET_CODE}"

PUPPET_RETURN=$?
if [ "${PUPPET_RETURN}" -eq 4 ] || [ "${PUPPET_RETURN}" -eq 6 ] ; then
    exit ${PUPPET_RETURN}
fi

set -e