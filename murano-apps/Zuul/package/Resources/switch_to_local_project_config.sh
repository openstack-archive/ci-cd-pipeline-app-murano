#!/usr/bin/env bash

REPO_URL=$(hiera -c /etc/puppet/hiera.yaml project_config_repo)

cp /var/lib/zuul/ssh/id_rsa /home/zuul/.ssh/id_rsa && chown zuul:zuul /home/zuul/.ssh/id_rsa

cd /etc/project-config
git remote set-url origin "$REPO_URL"

chown -R zuul:zuul /etc/project-config
