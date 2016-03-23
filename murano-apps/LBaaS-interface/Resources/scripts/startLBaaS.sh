#!/bin/bash

cd ~

# Start lbaas.
lbaas-server --config-file /etc/lbaas/lbaas.conf >> lbaas.log 2>&1 &