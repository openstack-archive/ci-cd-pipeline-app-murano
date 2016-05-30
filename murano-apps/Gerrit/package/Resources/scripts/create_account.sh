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

create_args=
set_args=

# check group
if [ ! -z ${GROUP} ] ; then
    create_args+="--group \'${GROUP}\' "
fi

# check full name
if [ ! -z ${FULL_NAME} ] ; then
    create_args+="--full-name \'${FULL_NAME}\' "
    set_args+="--full-name \'${FULL_NAME}\' "
fi

# check email
if [ ! -z ${EMAIL} ] ; then
    create_args+="--email $EMAIL "
    set_args+="--add-email $EMAIL "
fi

# check ssh
if [ ! -z ${SSHKEY} ] ; then
    create_args+="--ssh-key \'${SSHKEY}\' "
    set_args+="--add-ssh-key \'${SSHKEY}\' "
fi

echo "create ---  ${create_args[@]}" >> /tmp/fff
echo "set -----  ${set_args[@]}" >> /tmp/fff

set +e
su gerrit2 -c "ssh -p 29418 -i /home/gerrit2/review_site/etc/ssh_project_rsa_key project-creator@$HOSTNAME \
gerrit create-account ${create_args[@]} $NAME"

code=$?

if [ $code -ne 0 ]; then
  # Do not create account but set related properties.
  su gerrit2 -c "ssh -p 29418 -i /home/gerrit2/review_site/etc/ssh_project_rsa_key project-creator@$HOSTNAME \
  gerrit set-account ${set_args[@]} $NAME"
fi
