#!/usr/bin/env bash

cd /etc/project-config

# Check for new changes.
su - zuul -c "git pull"

sha_from_repo=$(sha1sum zuul/layout.yaml | awk '{print $1}')
sha_local=$(sha1sum /etc/zuul/layout/layout.yaml | awk '{print $1}')

# Determine whether a change is made.
if [ "$sha_local" != "$sha_from_repo" ]; then
  cp zuul/layout.yaml /etc/zuul/layout/layout.yaml
  service zuul force-reload
fi
