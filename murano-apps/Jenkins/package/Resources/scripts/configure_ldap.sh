#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_ldap
mkdir -p /etc/puppet/modules/configure_ldap/manifests/
mkdir -p /etc/puppet/modules/configure_ldap/templates/

cp configure_ldap/manifests/init.pp /etc/puppet/modules/configure_ldap/manifests/
cp configure_ldap/templates/config.erb /etc/puppet/modules/configure_ldap/templates/

puppet apply configure_ldap.pp