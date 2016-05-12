#!/bin/bash

#
# jenkins rsa key
#
ssh-keygen -t rsa -N "" -f jenkins.key -q

datafile='/etc/puppet/hieradata/murano.yaml'

content=`cat jenkins.key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'jenkins_ssh_private_key_contents', value=>'$content', }"

content=`cat jenkins.key.pub`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'jenkins_ssh_pubkey_contents', value=>'$content', }"
