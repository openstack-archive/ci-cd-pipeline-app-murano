#!/bin/bash
DOMAIN="$1"

echo "slapd slapd/no_configuration boolean false"   |  debconf-set-selections
echo "slapd slapd/domain string ${DOMAIN}"          |  debconf-set-selections
echo "slapd shared/organization string '${DOMAIN}'" |  debconf-set-selections
echo "slapd slapd/password1 password openstack"     |  debconf-set-selections
echo "slapd slapd/password2 password openstack"     |  debconf-set-selections
echo "slapd slapd/backend select HDB"               |  debconf-set-selections
echo "slapd slapd/purge_database boolean true"      |  debconf-set-selections
echo "slapd slapd/allow_ldap_v2 boolean false"      |  debconf-set-selections
echo "slapd slapd/move_old_database boolean true"   |  debconf-set-selections
dpkg-reconfigure -f noninteractive slapd
