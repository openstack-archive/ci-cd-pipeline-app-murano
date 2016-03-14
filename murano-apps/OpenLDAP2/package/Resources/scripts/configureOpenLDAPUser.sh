#!/bin/bash
DOMAIN="$1"
USERNAME="$2"
PASSWORD="$3"

DOMAIN_PASSWORD=$PASSWORD

NAME="`echo "$DOMAIN" | cut -d. -f1`"
TLD="`echo "$DOMAIN" | cut -d. -f2`"


ldapadd -x -w $DOMAIN_PASSWORD -D "cn=${USERNAME},dc=${NAME},dc=${TLD}" << USER
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

ldappasswd -w $DOMAIN_PASSWORD -s ${PASSWORD} -D "cn=${USERNAME},dc=${NAME},dc=${TLD}" -x uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}

# check if user been created
ldapwhoami -x -w ${PASSWORD} -D uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD} -hlocalhost -p389