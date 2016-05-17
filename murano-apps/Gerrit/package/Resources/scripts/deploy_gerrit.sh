#!/bin/bash

CONF_DIR="/etc/ci-cd"
EXECUTABLES_DIR="/usr/local/bin"

logger Install dev packages
apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python-dev

logger Deploy Gerrit

#TODO add this template to system-config
cp gerrit_gitconfig.erb /etc/puppet/modules/openstack_project/templates/

logger Generate ssl certificates
/bin/bash ./gen_ssl_cert.sh

logger Generate rsa keys
/bin/bash ./gen_rsa_key.sh

logger Database puppet
puppet apply database.pp

logger Gerrit puppet
# store to add cron task later
mkdir -p ${CONF_DIR}
cp site.pp ${CONF_DIR}/gerrit.pp
cp create_projects_periodic.sh ${EXECUTABLES_DIR}/create_projects_periodic.sh
chmod +x ${EXECUTABLES_DIR}/create_projects_periodic.sh

puppet apply site.pp

logger Projects puppet
puppet apply create_projects.pp

exit
