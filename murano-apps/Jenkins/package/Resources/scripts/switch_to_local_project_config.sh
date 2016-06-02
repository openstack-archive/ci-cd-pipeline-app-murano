#!/bin/bash

# Cloning 'project-config' from deployed Gerrit

GERRIT_URL=`hiera -c /etc/puppet/hiera.yaml gerrit_host`
su jenkins -c "git clone ssh://jenkins@$GERRIT_URL:29418/open-paas/project-config /tmp/project-config/"

# Updating jobs' configs

cp -R /tmp/project-config/ /etc/
chown -R jenkins:jenkins /etc/project-config
cp -R /etc/project-config/jenkins/jobs/* /etc/jenkins_jobs/config
/usr/local/bin/jenkins-jobs update --delete-old /etc/jenkins_jobs/config
rm -rf /tmp/project-config