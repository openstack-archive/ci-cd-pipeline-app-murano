#!/bin/bash

username="%USERNAME%"
password="%PASSWORD%"
jenkins_host="%JENKINS_HOST%"
cmd="curl --user '$username:$password' http://${jenkins_host}:8080/me/configure | grep apiToken | grep -o '\"[0-9a-f]\{32\}\"' | cut -d '\"' -f 2"

# Jenkins might not be ready at this point.
# Retry logic is used here.
token=$(eval "$cmd")
tries=10

while [ -z "$token" ]; do
  sleep 20
  token=$(eval "$cmd")

  tries=$((tries-1))

  if [ $tries -lt 1 ]; then
    break
  fi
done

echo "$token"
