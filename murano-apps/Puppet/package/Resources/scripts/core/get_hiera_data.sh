#!/bin/bash

KEY="$1"

hiera -c /etc/puppet/hiera.yaml "$KEY"
