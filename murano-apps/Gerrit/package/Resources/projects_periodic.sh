#!/usr/bin/env bash

cd /tmp

if [ ! -d project-config ]; then
  git clone http://$(hostname -f):8081/open-paas/project-config
else
  pushd project-config
    git fetch origin
    git rebase origin/master
  popd
fi

pushd project-config/gerrit
  cp -r acls projects.yaml /home/gerrit2/
  chown -R gerrit2:gerrit2 /home/gerrit2/acls /home/gerrit2/projects.yaml
popd

su gerrit2 -c "/usr/local/bin/manage-projects -v -d -l /var/log/manage_projects.log"
