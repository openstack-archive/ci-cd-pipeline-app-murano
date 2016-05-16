#!/bin/bash

CONF_DIR="/etc/ci-cd"

rm -rf /etc/project-config
GIT_SSL_NO_VERIFY=true /usr/bin/puppet apply ${CONF_DIR}/gerrit.pp

/usr/local/bin/manage-projects
