#!/usr/bin/env bash


ENV_NAME="$1"
PUPPETFILE_LINK="$2"
ENV_DIR="/etc/puppet/environments/${ENV_NAME}"

cd "${ENV_DIR}"
wget --quiet -c "${PUPPETFILE_LINK}" -O Puppetfile

librarian-puppet install
