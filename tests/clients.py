# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from heatclient import client as heatclient
from keystoneclient.v2_0 import client as keystoneclient
from muranoclient import client as muranoclient
from novaclient import client as novaclient


class ClientsBase(object):

    @staticmethod
    def initialize_keystone_client():
        username = os.environ.get('OS_USERNAME')
        password = os.environ.get('OS_PASSWORD')
        tenant_name = os.environ.get('OS_TENANT_NAME')
        auth_url = os.environ.get('OS_AUTH_URL')

        keystone = keystoneclient.Client(
            username=username,
            password=password,
            tenant_name=tenant_name,
            auth_url=auth_url
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

    @classmethod
    def initialize_nova_client(cls, auth_client=None):
        ks_client = (auth_client if auth_client
                     else cls.initialize_keystone_client())

        nova = novaclient.Client(
            '2',
            username=None,
            service_type='compute',
            endpoint_type='publicURL',
            auth_token=ks_client.auth_token,
            auth_url=ks_client.auth_url
        )
        nova.client.management_url = cls.get_endpoint('compute', 'publicURL')

        return nova