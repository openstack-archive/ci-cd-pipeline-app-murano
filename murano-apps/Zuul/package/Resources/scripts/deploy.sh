#!/bin/bash

logger Deploy Zuul

logger Generate rsa keys
/bin/bash ./gen_rsa_key.sh

logger Zuul puppet
puppet apply site.pp