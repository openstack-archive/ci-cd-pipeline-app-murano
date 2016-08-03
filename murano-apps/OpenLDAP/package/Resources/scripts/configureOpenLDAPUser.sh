#!/bin/bash
DOMAIN="$1"
ADMIN_USERNAME="$2"
ADMIN_PASSWORD="$3"
USERNAME="$4"
PASSWORD="$5"
EMAIL="$6"

DOMAIN_PASSWORD="$ADMIN_PASSWORD"

NAME="$(echo "$DOMAIN" | cut -d. -f1)"
TLD="$(echo "$DOMAIN" | cut -d. -f2)"

# If user doesn't specify non-admin username/password then
# script will create just admin user

if [ -z "$USERNAME" ];
  then
    USERNAME="$ADMIN_USERNAME";
    PASSWORD="$ADMIN_PASSWORD";
fi


ldapadd -x -w "$DOMAIN_PASSWORD" -D "cn=${ADMIN_USERNAME},dc=${NAME},dc=${TLD}" << USER
dn: uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}
objectClass: top
objectClass: posixAccount
objectClass: shadowAccount
objectclass: iNetOrgPerson
cn: ${USERNAME}
uid: ${USERNAME}
sn: ${USERNAME}
uidNumber: 1001
gidNumber: 1001
homeDirectory: /home/${USERNAME}
loginShell: /bin/bash
gecos: ${USERNAME}@${DOMAIN}
userPassword: {crypt}x
shadowLastChange: 0
shadowMax: 0
shadowWarning: 0
mail: ${EMAIL}
USER

ldappasswd -w "$DOMAIN_PASSWORD" -s "${PASSWORD}" -D "cn=${ADMIN_USERNAME},dc=${NAME},dc=${TLD}" -x "uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}"

# check if user been created
ldapwhoami -x -w "${PASSWORD}" -D "uid=${USERNAME},ou=users,dc=${NAME},dc=${TLD}" -hlocalhost -p389
