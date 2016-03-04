#!/bin/bash

impl=$1

sudo apt-get update

sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'

sudo apt-get install -y python-dev python-pip git;

sudo apt-get install -y -q mysql-server libmysqlclient-dev

# Installing LBaaS API.
git clone https://github.com/nmakhotkin/lbaas_api.git

cd lbaas_api

sudo pip install .
sudo pip install mysql-python

# Configure LBaaS.
cp etc/lbaas.conf.sample etc/lbaas.conf

sudo chmod -R a+rw /var/log

# Configure lbaas logging.
sed -i 's/#verbose = false/verbose = true/g' etc/lbaas.conf
sed -i 's/#default_log_levels/default_log_levels/g' etc/lbaas.conf
sed -i 's/#log_file = <None>/log_file = \/var\/log\/lbaas.log/g' etc/lbaas.conf

# Configure lbaas impl.
sed -i "s/#impl = haproxy/impl = $impl/g" etc/lbaas.conf

# Configure database connection.
mysql --user=root --password=root -e "CREATE DATABASE lbaas;"
mysql --user=root --password=root -e "GRANT ALL ON lbaas.* TO 'root'@'localhost';"

sed -i 's/#connection = <None>/connection = mysql:\/\/root:root@localhost:3306\/lbaas/g' etc/lbaas.conf
sed -i 's/#max_overflow = <None>/max_overflow = -1/g' etc/lbaas.conf
sed -i 's/#max_pool_size = <None>/max_pool_size = 1000/g' etc/lbaas.conf

# Upgrade database.
lbaas-db-manage --config-file etc/lbaas.conf upgrade head

# Moving config to another place.
sudo mkdir /etc/lbaas
sudo chown -R $USER:$USER /etc/lbaas
sudo chown /var/log/lbaas.log

mv etc/lbaas.conf /etc/lbaas/lbaas.conf

cd ~

# Start lbaas.
lbaas-server --config-file /etc/lbaas/lbaas.conf >> lbaas.log 2>&1 &
