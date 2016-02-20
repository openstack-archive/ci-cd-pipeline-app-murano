#!/usr/bin/env bash

key=$1
value=$2
logger Put value to Hiera $key=$value

puppet apply --execute "yaml_setting { 'example': target=>'/etc/puppet/hieradata/murano.yaml', key=>'$key', value=>'$value', }"
