#!/bin/bash

mkdir /etc/puppet/modules/configure_ldap
mkdir /etc/puppet/modules/configure_ldap/manifests/
mkdir /etc/puppet/modules/configure_ldap/templates/

cp configure_ldap/manifests/init.pp /etc/puppet/modules/configure_ldap/manifests/
cp configure_ldap/templates/config.erb /etc/puppet/modules/configure_ldap/templates/

puppet apply ldap_init.pp