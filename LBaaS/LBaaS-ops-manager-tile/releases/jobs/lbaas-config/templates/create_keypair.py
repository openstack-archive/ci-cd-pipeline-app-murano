import sys

from keystoneclient.v3 import client as keystoneclient
from novaclient import client as novaclient
from novaclient import exceptions


if len(sys.argv) < 7:
    print(
        "Usage: {0} <auth_url> <username> <tenant> <password> <keypair-name>"
        "<public key str>".format(
            __file__
        )
    )
    exit(1)

auth_url = sys.argv[1]
username = sys.argv[2]
tenant = sys.argv[3]
password = sys.argv[4]
key_name = sys.argv[5]
public_key = sys.argv[6]

keystone = keystoneclient.Client(
    username=username,
    tenant_name=tenant,
    password=password,
    auth_url=auth_url
)

nova_url = keystone.service_catalog.url_for(service_type='compute')

nova = novaclient.Client(
    2,
    username=None,
    api_key=None,
    endpoint_type='publicURL',
    service_type='compute',
    auth_token=keystone.auth_token,
    tenant_id=keystone.project_id,
    auth_url=auth_url
)
nova.client.management_url = nova_url

try:
    nova.keypairs.get(key_name)
except exceptions.NotFound:
    pass
else:
    nova.keypairs.delete(key_name)

nova.keypairs.create(key_name, public_key)
