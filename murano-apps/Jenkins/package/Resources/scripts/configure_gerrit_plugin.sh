#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_gerrit_plugin
mkdir -p /etc/puppet/modules/configure_gerrit_plugin/manifests/
mkdir -p /etc/puppet/modules/configure_gerrit_plugin/templates/

cp configure_gerrit_plugin/manifests/init.pp /etc/puppet/modules/configure_gerrit_plugin/manifests/
cp configure_gerrit_plugin/templates/gerrit-trigger.xml.erb /etc/puppet/modules/configure_gerrit_plugin/templates/

puppet apply configure_gerrit_plugin.pp
