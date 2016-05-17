#!/usr/bin/env bash

PUPPET_CODE=`echo -n $1 | base64 -d`

puppet apply --execute "${PUPPET_CODE}"

exit $?