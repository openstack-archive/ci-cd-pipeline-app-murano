#!/bin/bash

# Fail script if an error occurs.
set -e
# TODO(nmakhotkin): It should be removed in the future after fixing the bug:
# TODO(nmakhotkin): https://bugs.launchpad.net/murano/+bug/1561522
# TODO(nmakhotkin): Here should be used pure tar.gz archive instead of base64-encoded.
base64 --decode f5-lbaas-driver.tar.gz.bs64 > f5-lbaas-driver.tar.gz

# Installing LBaaS API.
sudo pip install f5-lbaas-driver.tar.gz

# Adding a new config section to main config.
cat f5-lbaas-append.conf.sample >> /etc/lbaas/lbaas.conf

