#!/bin/bash

logger Cloning openstack-ci system-config

git clone https://review.fuel-infra.org/open-paas/system-config

logger Installing openstack-ci system-config

cd system-config
./install_modules.sh

cp -r modules/ /etc/puppet/


git clone https://review.fuel-infra.org/open-paas/project-config
cp -r project-config/ /etc/
