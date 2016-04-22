#!/bin/bash

sudo apt-get update

sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'

sudo apt-get install -y python-dev python-pip git;

sudo apt-get install -y -q mysql-server libmysqlclient-dev

# TODO(nmakhotkin): It should be removed in the future after fixing the bug:
# TODO(nmakhotkin): https://bugs.launchpad.net/murano/+bug/1561522
# TODO(nmakhotkin): Here should be used pure tar.gz archive instead of base64-encoded.
base64 --decode lbaas.tar.gz.bs64 > lbaas.tar.gz

# Installing LBaaS API.
sudo pip install lbaas.tar.gz

sudo pip install mysql-python

sudo mkdir /etc/lbaas
sudo chown -R $USER:$USER /etc/lbaas
sudo chown -R $USER:$USER /var/log/lbaas.log

# Moving config to another place.
cp lbaas.conf.sample /etc/lbaas/lbaas.conf

# Configure lbaas logging.
sudo chmod -R a+rw /var/log
sed -i 's/#verbose = false/verbose = true/g' /etc/lbaas/lbaas.conf
sed -i 's/#default_log_levels/default_log_levels/g' /etc/lbaas/lbaas.conf
sed -i 's/#log_file = <None>/log_file = \/var\/log\/lbaas.log/g' /etc/lbaas/lbaas.conf

# Configure database connection.
mysql --user=root --password=root -e "CREATE DATABASE lbaas;"
mysql --user=root --password=root -e "GRANT ALL ON lbaas.* TO 'root'@'localhost';"

sed -i 's/#connection = <None>/connection = mysql:\/\/root:root@localhost:3306\/lbaas/g' /etc/lbaas/lbaas.conf
sed -i 's/#max_overflow = <None>/max_overflow = -1/g' /etc/lbaas/lbaas.conf
sed -i 's/#max_pool_size = <None>/max_pool_size = 1000/g' /etc/lbaas/lbaas.conf

# Upgrade database.
lbaas-db-manage --config-file /etc/lbaas/lbaas.conf upgrade head
