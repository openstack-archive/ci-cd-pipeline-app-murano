#!/bin/bash

rm -rf /etc/project-config
GIT_SSL_NO_VERIFY=true /usr/bin/puppet apply /etc/open-paas/gerrit.pp

/usr/local/bin/manage-projects -v -l /var/log/manage_projects.log
