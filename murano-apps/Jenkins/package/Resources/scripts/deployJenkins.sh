#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Install prerequisites
wget -q -O - https://jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
apt-get update

# Jenkins
apt-get -y install jenkins

# Open firewall for jenkins
iptables -I INPUT 1 -p tcp -m tcp --dport 8080 -j ACCEPT -m comment --comment "by Murano, Jenkins"
service jenkins restart

# Create an ssh-key that can be used between Gerrit and Jenkins
sudo -u jenkins ssh-keygen -t rsa -N "" -f /var/lib/jenkins/.ssh/jenkins-id_rsa
chmod 400 /var/lib/jenkins/.ssh/jenkins-id_rsa
chmod 600 /var/lib/jenkins/.ssh/jenkins-id_rsa.pub

