#!/usr/bin/env bash

set -e

if [ $# -eq 0 ]; then
  echo "USAGE: $0 plugin1 plugin2 ..."
  exit 1
fi

plugin_dir=/var/lib/jenkins/plugins
owner=jenkins:jenkins

mkdir -p ${plugin_dir}

installPlugin() {
  plugin_name=$1
  if [ -f ${plugin_dir}/${plugin_name}.hpi -o -f ${plugin_dir}/${plugin_name}.jpi ]; then
    if [ "$2" == "1" ]; then
      return 1
    fi
  fi
  echo "Installing: $plugin_name"
  curl -L --silent --output ${plugin_dir}/${plugin_name}.hpi  https://updates.jenkins-ci.org/latest/${plugin_name}.hpi
  return 0
}

# Install plugin.
for plugin in $*
do
    installPlugin "$plugin"
done

changed=1
maxloops=20

# Install all dependencies.
while [ "$changed"  == "1" ]; do
  echo "Check for missing dependecies ..."
  if  [ $maxloops -lt 1 ] ; then
    echo "Max loop count reached - probably a bug in this script: $0"
    exit 1
  fi
  ((maxloops--))
  changed=0
  for f in ${plugin_dir}/*.hpi ; do
    # Without optionals.
    # deps=$( unzip -p ${f} META-INF/MANIFEST.MF | tr -d '\r' | sed -e ':a;N;$!ba;s/\n //g' | grep -e "^Plugin-Dependencies: " | awk '{ print $2 }' | tr ',' '\n' | grep -v "resolution:=optional" | awk -F ':' '{ print $1 }' | tr '\n' ' ' )
    # With optionals.
    deps=$( unzip -p ${f} META-INF/MANIFEST.MF | tr -d '\r' | sed -e ':a;N;$!ba;s/\n //g' | grep -e "^Plugin-Dependencies: " | awk '{ print $2 }' | tr ',' '\n' | awk -F ':' '{ print $1 }' | tr '\n' ' ' )
    for plugin in $deps; do
      # if installPlugin returns 1 then 'changed' stays as is. (it means that the whole jenkins plugins state is not changed and in fact, nothing installed)
      # if installPlugin returns 0 then changed=1
      installPlugin "$plugin" 1 && changed=1
    done
  done
done

# Fixing permissions.
chown -R ${owner} ${plugin_dir}

# Restart Jenkins.
service jenkins restart
