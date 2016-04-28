#!/bin/bash

GERRIT_USER="$1"
GROUP="$2"
FULL_NAME="$3"
EMAIL="$4"
SSHKEY="$5"
NAME="$6"

#TODO(akuznetsova): Uncomment this code when separate method addKey in Gerrit.yaml is implemented
# so account will be created under 'Gerrit Admin User' and not under 'project-creator'
# ssh -p 29418 $GERRIT_USER@localhost -i /home/gerrit2/review_site/etc/ssh_host_rsa_key gerrit create-account \
#   --group "'$GROUP'" --full-name "'$FULL_NAME'" --email $EMAIL --ssh-key "'$SSHKEY'" $NAME

HOSTNAME="`hostname -f`"

su gerrit2 -c "ssh -p 29418 -i /home/gerrit2/review_site/etc/ssh_project_rsa_key project-creator@$HOSTNAME "`
 `"gerrit create-account --group \'${GROUP}\' --full-name \'${FULL_NAME}\' --email $EMAIL --ssh-key \'${SSHKEY}\' $NAME"