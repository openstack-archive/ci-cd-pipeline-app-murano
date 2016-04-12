#!/bin/bash

# No error if already exists.
mkdir -p /etc/puppet/modules/configure_zmq
mkdir -p /etc/puppet/modules/configure_zmq/manifests/
mkdir -p /etc/puppet/modules/configure_zmq/templates/

cp configure_zmq/manifests/init.pp /etc/puppet/modules/configure_zmq/manifests/
cp configure_zmq/templates/org.jenkinsci.plugins.ZMQEventPublisher.HudsonNotificationProperty.xml.erb /etc/puppet/modules/configure_zmq/templates/

puppet apply configure_zmq.pp