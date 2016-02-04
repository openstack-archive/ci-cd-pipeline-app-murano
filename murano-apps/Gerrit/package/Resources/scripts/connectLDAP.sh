#!/bin/bash
OPENLDAP_IP="$1"
HOST="$2"
DOMAIN="$3"

# parse tld
NAME="`echo "$DOMAIN" | cut -d. -f1`"
TLD="`echo "$DOMAIN" | cut -d. -f2`"


# setup gerrit to authenticate from OpenLDAP
sed -e "s/type = OPENID/type = ldap/" -i /home/gerrit/gerrit_testsite/etc/gerrit.config
sed -e "s,canonicalWebUrl.*,canonicalWebUrl = http://${HOST}:8080," -i /home/gerrit/gerrit_testsite/etc/gerrit.config

cat << EOF >> /home/gerrit/gerrit_testsite/etc/gerrit.config
[ldap]
        server = ldap://${OPENLDAP_IP}
        accountBase = OU=users,DC=${NAME},DC=${TLD}
        username =  CN=admin,DC=${NAME},DC=${TLD}
        password = openstack
        accountFullName = cn
EOF

# restart gerrit
sudo -u gerrit /home/gerrit/gerrit_testsite/bin/gerrit.sh restart
