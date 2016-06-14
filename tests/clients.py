import os

from heatclient import client as heatclient
from keystoneclient.v2_0 import client as keystoneclient
from muranoclient import client as muranoclient


class ClientsBase(object):

    @staticmethod
    def initialize_keystone_client():

        username = os.environ.get('OS_USERNAME')
        password = os.environ.get('OS_PASSWORD')
        tenant_name = os.environ.get('OS_TENANT_NAME')
        uri = os.environ.get('OS_AUTH_URL')

        keystone = keystoneclient.Client(
            username=username,
            password=password,
            tenant_name=tenant_name,
            auth_url=uri
        )

        return keystone

    @classmethod
    def get_endpoint(cls, service_type, endpoint_type):
        ks_client = cls.initialize_keystone_client()

        return ks_client.service_catalog.url_for(
            service_type=service_type,
            endpoint_type=endpoint_type
        )

    @classmethod
    def initialize_murano_client(cls, auth_client=None):
        ks_client = (auth_client if auth_client
                     else cls.initialize_keystone_client())

        murano_endpoint = cls.get_endpoint(
            service_type='application-catalog',
            endpoint_type='publicURL'
        )

        murano = muranoclient.Client(
            '1',
            endpoint=murano_endpoint,
            token=ks_client.auth_token
        )

        return murano

    @classmethod
    def initialize_heat_client(cls, auth_client=None):
        ks_client = (auth_client if auth_client
                     else cls.initialize_keystone_client())

        heat_endpoint = cls.get_endpoint(
            service_type='orchestration',
            endpoint_type='publicURL'
        )

        heat = heatclient.Client(
            '1',
            endpoint=heat_endpoint,
            token=ks_client.auth_token
        )

        return heat

