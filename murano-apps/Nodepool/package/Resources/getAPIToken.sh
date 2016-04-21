#!/bin/bash

username="%USERNAME%"
password="%PASSWORD%"
jenkins_host="%JENKINS_HOST%"

curl --user "$username:$password" http://${jenkins_host}:8080/me/configure | grep -o '"[0-9a-f]\{32\}"' | cut -d '"' -f 2
