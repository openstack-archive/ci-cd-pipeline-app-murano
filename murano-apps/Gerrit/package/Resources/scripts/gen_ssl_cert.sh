#!/bin/bash
logger Generate SSL certificate for Gerrit

datafile='/etc/puppet/hieradata/murano.yaml'

fqdn=$(hostname)

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=$fqdn" \
    -keyout server.key -out server.cert

cp server.key server.key.org
openssl rsa -in server.key.org -out server.key

content=$(cat server.key)
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssl_key_file_contents', value=>'$content', }"

content=$(cat server.cert)
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssl_cert_file_contents', value=>'$content', }"

content=''
puppet apply --execute "yaml_setting { 'example': target=>'$datafile', key=>'gerrit_ssl_chain_file_contents', value=>'$content', }"

# create
getent group ssl-cert || addgroup --system 'ssl-cert'

exit
