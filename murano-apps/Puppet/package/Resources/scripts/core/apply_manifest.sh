#!/usr/bin/env bash

set +e

puppet apply --detailed-exitcodes --color=false "../site.pp"

PUPPET_RETURN=$?
if [ "${PUPPET_RETURN}" -eq 4 ] || [ "${PUPPET_RETURN}" -eq 6 ] ; then
    exit ${PUPPET_RETURN}
fi

set -e