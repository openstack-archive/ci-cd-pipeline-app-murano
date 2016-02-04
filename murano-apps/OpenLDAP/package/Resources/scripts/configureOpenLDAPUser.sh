#!/bin/bash
DOMAIN="$1"
USERNAME="$2"
PASSWORD="$3"

NAME="`echo "$DOMAIN" | cut -d. -f1`"
TLD="`echo "$DOMAIN" | cut -d. -f2`"


# Create group.ldif and user.ldif
cat << GROUP > /tmp/group.ldif
dn: ou=users,dc=${NAME},dc=${TLD}
objectClass: top
objectClass: organizationalUnit
GROUP

cat << USER > /tmp/user.ldif
dn: uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}
objectClass: top
objectClass: account
objectClass: posixAccount
objectClass: shadowAccount
cn: ${USERNAME}
uid: ${USERNAME}
uidNumber: 1001
gidNumber: 1001
homeDirectory: /home/${USERNAME}
loginShell: /bin/bash
gecos: ${USERNAME}@${DOMAIN}
userPassword: {crypt}x
shadowLastChange: 0
shadowMax: 0
shadowWarning: 0
USER

ldapadd -x -w openstack -D "cn=admin,dc=${NAME},dc=${TLD}" -f /tmp/group.ldif
ldapadd -x -w openstack -D "cn=admin,dc=${NAME},dc=${TLD}" -f /tmp/user.ldif
ldappasswd -s ${PASSWORD} -D "cn=admin,dc=${NAME},dc=${TLD}" -w openstack -x uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}
