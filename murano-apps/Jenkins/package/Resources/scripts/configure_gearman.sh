#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_gearman
mkdir -p /etc/puppet/modules/configure_gearman/manifests/
mkdir -p /etc/puppet/modules/configure_gearman/templates/

cp configure_gearman/manifests/init.pp /etc/puppet/modules/configure_gearman/manifests/
cp configure_gearman/templates/hudson.plugins.gearman.GearmanPluginConfig.xml.erb /etc/puppet/modules/configure_gearman/templates/

puppet apply configure_gearman.pp