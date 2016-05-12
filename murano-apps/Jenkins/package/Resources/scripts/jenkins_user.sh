#!/usr/bin/env bash

puppet apply jenkins_user.pp

su jenkins -c "cp /var/lib/jenkins/.ssh/id_rsa /home/jenkins/.ssh/ && chmod 0700 /home/jenkins/.ssh"
