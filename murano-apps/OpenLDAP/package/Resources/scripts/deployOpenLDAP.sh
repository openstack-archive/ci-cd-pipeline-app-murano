#!/bin/bash

apt-get update
apt-get install -y debconf

echo "slapd slapd/root_password password openstack"       |  debconf-set-selections
echo "slapd slapd/root_password_again password openstack" |  debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get install -y slapd ldap-utils

# Open firewall for ldap/ldaps
iptables -I INPUT 1 -p tcp -m tcp --dport 389 -j ACCEPT -m comment --comment "by murano, OpenLDAP server access on port 389"
iptables -I INPUT 1 -p tcp -m tcp --dport 636 -j ACCEPT -m comment --comment "by murano, OpenLDAP server access on port 636"
