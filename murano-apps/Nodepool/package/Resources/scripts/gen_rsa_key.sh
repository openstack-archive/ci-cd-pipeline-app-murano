#!/bin/bash
logger Generate SSH Private key for nodepool

datafile='/etc/puppet/hieradata/murano.yaml'

#
# nodepool ssh key
#
ssh-keygen -t rsa -N "" -f nodepool_ssh.key -q

content=`cat nodepool_ssh.key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'nodepool_ssh_private_key', value=>'$content', }"

exit