#!/bin/bash
JENKINS_IP="$1"
USER="$2"
PASSWORD="$3"

cd ~/jenkins-job-builder
cp etc/jenkins_jobs.ini-sample etc/jenkins_jobs.ini

sed -i "s/https:\/\/jenkins.example.com/http:\/\/$JENKINS_IP:8080\//g" etc/jenkins_jobs.ini

if [ -n "$USER" ];
  then
    sed -i "s/user=jenkins/user=$USER/g" etc/jenkins_jobs.ini;
    sed -i "s/password=1234567890abcdef1234567890abcdef/password=$PASSWORD/g" etc/jenkins_jobs.ini;
fi



