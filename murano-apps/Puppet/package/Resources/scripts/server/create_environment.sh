#!/usr/bin/env bash


ENV_NAME="$1"
PUPPETFILE_LINK="$2"
ENV_DIR="/etc/puppet/environments/${ENV_NAME}"

rm -rf ${ENV_DIR}

mkdir ${ENV_DIR}
mkdir ${ENV_DIR}/modules
mkdir ${ENV_DIR}/manifests

cd ${ENV_DIR}
wget --quiet -c ${PUPPETFILE_LINK} -O Puppetfile

librarian-puppet install




