#!/bin/bash

section=$1
key=$2
value=$3

# Set value in lbaas config file.
sudo sed -i "/^\[$section\]$/,/^\[/ s/^#*$key.*=.*/$key = $value/" /etc/lbaas/lbaas.conf
