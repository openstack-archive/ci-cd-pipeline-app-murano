#!/bin/bash

datafile='/etc/puppet/hieradata/murano.yaml'

ssh-keygen -t rsa -P '' -f zuul_ssh_key -q

content=`cat zuul_ssh_key`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'zuul_ssh_private_key_contents', value=>'$content', }"

content=`cat zuul_ssh_key.pub`
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'zuul_ssh_pubkey_contents', value=>'$content', }"