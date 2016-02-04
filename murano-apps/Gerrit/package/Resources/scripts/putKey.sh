#!/bin/bash
SSHKEY="$1 $2"

mkdir /home/gerrit/.ssh
echo $SSHKEY > /home/gerrit/.ssh/authorized_keys
echo $SSHKEY > /home/gerrit/.ssh/jenkins-id_rsa.pub
chmod 700 /home/gerrit/.ssh
chmod 600 /home/gerrit/.ssh/authorized_keys /home/gerrit/.ssh/jenkins-id_rsa.pub
chown -R gerrit:gerrit /home/gerrit/.ssh
