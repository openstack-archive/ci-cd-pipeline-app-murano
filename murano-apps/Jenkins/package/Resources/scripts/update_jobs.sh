#!/bin/bash

cd /etc/project-config

# Check whether we have local Gerrit installed or not.
# If yes, then 'git pull' should be executed under 'jenkins' user

GERRIT_URL=$(hiera -c /etc/puppet/hiera.yaml gerrit_host)

if [ "$GERRIT_URL" != "nil" ]; then
  echo "Pulling changes from installed Gerrit"
  su jenkins -c "git pull"
else
  echo "Pulling changes from upsteam Gerrit"
  git pull
fi

cp -R /etc/project-config/jenkins/jobs/* /etc/jenkins_jobs/config
/usr/local/bin/jenkins-jobs update --delete-old /etc/jenkins_jobs/config
