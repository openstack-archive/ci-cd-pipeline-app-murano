#!/bin/bash
WAR="$1"

# Update the packages and install git and java
apt-get update
apt-get install -y git openjdk-7-jdk git-review

# Create a user, gerrit2, to run gerrit
useradd -d/home/gerrit gerrit
mkdir /home/gerrit
chown -R gerrit:gerrit /home/gerrit

# Allow firewall holes for Gerrit
iptables -I INPUT 1 -p tcp -m tcp --dport 8080 -j ACCEPT -m comment --comment "by murano, Gerrit server access on HTTP on port 8080"
iptables -I INPUT 1 -p tcp -m tcp --dport 29418 -j ACCEPT -m comment --comment "by murano,  server Apache server access via sshd on port 29418"

# Download latest stable code, install and remove war file.
cd /tmp
wget ${WAR}
filename=$(basename ${WAR})
sudo -u gerrit java -jar /tmp/$filename init --batch -d /home/gerrit/gerrit_testsite
rm /tmp/$filename
