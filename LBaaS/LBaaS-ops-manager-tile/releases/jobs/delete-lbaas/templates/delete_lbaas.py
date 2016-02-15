import sys

from keystoneclient.v3 import client as keystoneclient
from muranoclient.v1 import client as muranoclient


if len(sys.argv) < 5:
    print(
        "Usage: {0} <auth_url> <username> <tenant> <password>".format(
            __file__
        )
    )
    exit(1)


def get_env_by_prefix(murano, prefix):
    envs = list(
        filter(
            lambda e: e.name.startswith(prefix),
            murano.environments.list()
        )
    )

    if not envs:
        return None

    return envs[0]


auth_url = sys.argv[1]
username = sys.argv[2]
tenant = sys.argv[3]
password = sys.argv[4]

keystone = keystoneclient.Client(
    username=username,
    tenant_name=tenant,
    password=password,
    auth_url=auth_url
)

murano_url = keystone.service_catalog.url_for(
    service_type='application_catalog'
)

murano = muranoclient.Client(
    murano_url,
    auth_url=auth_url,
    tenant=keystone.project_id,
    token=keystone.auth_token
)

env = get_env_by_prefix(murano, "CF-LBaaS-")

if not env:
    print ("Env already deleted.")
    exit(0)

murano.environments.delete(env.id)
