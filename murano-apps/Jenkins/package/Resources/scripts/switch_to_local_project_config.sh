#!/bin/bash

# Cloning 'project-config' from deployed Gerrit

GERRIT_URL=$(hiera -c /etc/puppet/hiera.yaml gerrit_host)
su jenkins -c "git clone ssh://jenkins@$GERRIT_URL:29418/open-paas/project-config /tmp/project-config/"

# Removing old project-config

rm -rf /etc/project-config

# Creating of new /etc/project-config folder and changing its owner
# to 'jenkins' to have an ability to pull new changes under 'jenkins'

cp -R /tmp/project-config/ /etc/
chown -R jenkins:jenkins /etc/project-config
cp -R /etc/project-config/jenkins/jobs/* /etc/jenkins_jobs/config

# Updating jobs' config

/usr/local/bin/jenkins-jobs update --delete-old /etc/jenkins_jobs/config

# Removing temporary folder

rm -rf /tmp/project-config
