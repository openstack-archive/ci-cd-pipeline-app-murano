#!/usr/bin/env bash

REPO_URL=$(hiera -c /etc/puppet/hiera.yaml project_config_repo)

cp /var/lib/zuul/ssh/id_rsa /home/zuul/.ssh/id_rsa && chown zuul:zuul /home/zuul/.ssh/id_rsa

cd /etc/project-config
git remote set-url origin "$REPO_URL"
git config --global user.email "zuul@example.com"
git config --global user.name "Zuul"

chown -R zuul:zuul /etc/project-config
