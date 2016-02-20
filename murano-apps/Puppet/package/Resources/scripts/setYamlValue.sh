#!/usr/bin/env bash

path=$1
key=$2
value=$3

logger Put value to $path $key=$value

puppet apply --execute "yaml_setting { 'example': target=>'$path', key=>'$key', value=>'$value', }"
