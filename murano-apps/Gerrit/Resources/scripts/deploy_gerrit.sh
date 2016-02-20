#!/bin/bash

logger Deploy Gerrit

logger Generate ssl certificates
/bin/bash ./gen_ssl_cert.sh

logger Generate rsa keys
/bin/bash ./gen_rsa_key.sh

logger Database puppet
puppet apply database.pp

logger Gerrit puppet
puppet apply site.pp

exit
