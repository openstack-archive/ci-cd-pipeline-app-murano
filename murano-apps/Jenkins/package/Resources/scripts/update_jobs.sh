#!/bin/bash

cd /etc/project-config

# Check whether we have local Gerrit installed or not.
# If yes, then 'git pull' should be executed unde 'jenkins' user

GERRIT_URL=`hiera -c /etc/puppet/hiera.yaml gerrit_bbb`

if ! [ $GERRIT_URL="nil" ]; then
  su jenkins -c "git pull"
else
  git pull
fi

cp -R /etc/project-config/jenkins/jobs/* /etc/jenkins_jobs/config
/usr/local/bin/jenkins-jobs update --delete-old /etc/jenkins_jobs/config