#!/bin/bash

logger Installing Hiera

sudo puppet resource package hiera ensure=installed

mkdir /etc/puppet/hieradata/

# hiera config
cp hiera.yaml /etc/puppet/hiera.yaml

# data file
cp murano.yaml /etc/puppet/hieradata/murano.yaml


mkdir /etc/system-config/

puppet config set environment production

exit