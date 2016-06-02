#!/bin/bash

cd /etc/project-config
su jenkins -c "git pull"
cp -R /etc/project-config/jenkins/jobs/* /etc/jenkins_jobs/config
/usr/local/bin/jenkins-jobs update --delete-old /etc/jenkins_jobs/config