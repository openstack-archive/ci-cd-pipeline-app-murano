#!/bin/bash

bash gen_rsa_key.sh

puppet apply site.pp

sudo apt-get install default-jdk -y

