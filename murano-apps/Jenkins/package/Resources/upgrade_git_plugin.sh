#!/usr/bin/env bash

plugin_list="icon-shim mailer scm-api token-macro parameterized-trigger junit script-security credentials ssh-credentials git-client matrix-project git"

for plugin in $plugin_list
do
  curl -L https://updates.jenkins-ci.org/latest/$plugin.hpi > /var/lib/jenkins/plugins/$plugin.hpi
  chown jenkins:jenkins /var/lib/jenkins/plugins/$plugin.hpi
  chmod 0644 /var/lib/jenkins/plugins/$plugin.hpi
done

service jenkins restart
