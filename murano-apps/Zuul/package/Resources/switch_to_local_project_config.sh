#!/usr/bin/env bash

GERRIT_HOST=$(hiera -c /etc/puppet/hiera.yaml gerrit_host)

cp /var/lib/zuul/ssh/id_rsa /home/zuul/.ssh/id_rsa && chown zuul:zuul /home/zuul/.ssh/id_rsa

cd /etc/project-config
git remote set-url origin ssh://zuul@${GERRIT_HOST}:29418/open-paas/project-config

chown -R zuul:zuul /etc/project-config
