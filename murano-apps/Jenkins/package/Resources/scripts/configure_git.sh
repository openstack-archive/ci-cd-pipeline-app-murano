#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_git
mkdir -p /etc/puppet/modules/configure_git/manifests/
mkdir -p /etc/puppet/modules/configure_git/templates/

cp configure_git/manifests/init.pp /etc/puppet/modules/configure_git/manifests/
cp configure_git/templates/hudson.plugins.git.GitSCM.xml.erb /etc/puppet/modules/configure_git/templates/

puppet apply configure_git.pp
