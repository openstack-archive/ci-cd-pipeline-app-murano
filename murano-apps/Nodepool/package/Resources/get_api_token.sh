#!/bin/bash

username="%USERNAME%"
password="%PASSWORD%"
jenkins_host="%JENKINS_HOST%"

# Jenkins might not be ready at this point.
# Retry logic is used here.
token=$(curl --user "$username:$password" http://${jenkins_host}:8080/me/configure | grep -o '"[0-9a-f]\{32\}"' | cut -d '"' -f 2)
tries=10

while [ -z $token ]; do
  sleep 20
  token=$(curl --user "$username:$password" http://${jenkins_host}:8080/me/configure | grep -o '"[0-9a-f]\{32\}"' | cut -d '"' -f 2)

  tries=$((tries-1))

  if [ $tries -lt 1 ]; then
    break
  fi
done

echo $token
