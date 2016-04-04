#!/bin/bash
logger Generate SSL certificate for Gerrit

datafile='/etc/puppet/hieradata/murano.yaml'

#
# gerrit rsa key
#
ssh-keygen -t rsa -N "" -f gerrit-rsa.key -q

content=`cat gerrit-rsa.key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_rsa_key_contents', value=>'$content', }"

content=`cat gerrit-rsa.key.pub`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_rsa_pubkey_contents', value=>'$content', }"

#
# gerrit dsa key
#
ssh-keygen -t rsa -N "" -f gerrit-dsa.key -q

content=`cat gerrit-dsa.key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_dsa_key_contents', value=>'$content', }"

content=`cat gerrit-dsa.key.pub`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_dsa_pubkey_contents', value=>'$content', }"

#
# project key
#
ssh-keygen -t rsa -N "" -f project-rsa.key -q

content=`cat project-rsa.key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_project_rsa_key_contents', value=>'$content', }"

content=`cat project-rsa.key.pub`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssh_project_rsa_pubkey_contents', value=>'$content', }"

exit