#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_credentials
mkdir -p /etc/puppet/modules/configure_credentials/manifests/
mkdir -p /etc/puppet/modules/configure_credentials/files/

cp configure_credentials/manifests/init.pp /etc/puppet/modules/configure_credentials/manifests/
cp configure_credentials/files/credentials.xml /etc/puppet/modules/configure_credentials/files/

puppet apply configure_credentials.pp
