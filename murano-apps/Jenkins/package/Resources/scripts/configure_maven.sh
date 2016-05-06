#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_maven
mkdir -p /etc/puppet/modules/configure_maven/manifests/
mkdir -p /etc/puppet/modules/configure_maven/templates/

cp configure_maven/manifests/init.pp /etc/puppet/modules/configure_maven/manifests/
cp configure_maven/templates/hudson.tasks.Maven.xml.erb /etc/puppet/modules/configure_maven/templates/

puppet apply configure_maven.pp