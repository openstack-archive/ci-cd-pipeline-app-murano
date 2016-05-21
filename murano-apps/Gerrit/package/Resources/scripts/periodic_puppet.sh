#!/bin/bash

CONF_DIR="/etc/ci-cd"

#
# We are using self signed certificate for https local repo
# so GIT_SSL_NO_VERIFY should be set.
# TODO: https for a local repo should be replaced by SSH url
GIT_SSL_NO_VERIFY=true /usr/bin/puppet apply ${CONF_DIR}/gerrit.pp

#
# Log rotation is turned on in create_projects.pp
#
# TODO: Should be replaced by git hook
/usr/local/bin/manage-projects -v -d -l /var/log/manage_projects.log
