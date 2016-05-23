#!/usr/bin/env bash

su gerrit2 -c bash << "EOF"

cd /tmp
rm -rf All_Projects
mkdir All_Projects
cd All_Projects

# Add project-creator key to ssh-agent.
eval $(ssh-agent -s)
ssh-add /home/gerrit2/review_site/etc/ssh_project_rsa_key

git init
git remote add origin ssh://project-creator@$(hostname -f):29418/All-Projects
git fetch origin refs/meta/config:refs/remotes/origin/meta/config
git checkout meta/config

already_exists=$(grep 'label "Verified"' project.config)

# Skip if the label already exists.
if [ ! -z "$already_exists" ]; then
  exit 0
fi

cat >> project.config << CONFIG
[label "Verified"]
       function = MaxWithBlock
       value = -1 Fails
       value =  0 No score
       value = +1 Verified
CONFIG

git commit -am "Adding label 'Verified' to All-projects"
git push origin meta/config:meta/config
EOF
