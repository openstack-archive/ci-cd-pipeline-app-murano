#!/bin/bash

DEBIAN_FRONTEND=noninteractive apt-get install -y slapd ldap-utils

# needed to use ldap puppet module
# https://forge.puppetlabs.com/datacentred/ldap
apt-get install ruby-net-ldap

puppet apply site.pp

# Open firewall for ldap/ldaps
iptables -I INPUT 1 -p tcp -m tcp --dport 389 -j ACCEPT -m comment --comment "by murano, OpenLDAP server access on port 389"
iptables -I INPUT 1 -p tcp -m tcp --dport 636 -j ACCEPT -m comment --comment "by murano, OpenLDAP server access on port 636"
