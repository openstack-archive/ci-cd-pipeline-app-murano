# Copyright 2016 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json

from f5 import bigip
from oslo_config import cfg
from oslo_log import log as logging
import requests

from lbaas import config
from lbaas.drivers import base

bigip_opts = [
    cfg.StrOpt('host', help='BIG IP host.'),
    cfg.StrOpt('username', help='BIG IP username'),
    cfg.StrOpt('password', help='BIG IP password')
]
CONF = cfg.CONF
CONF.register_opts(bigip_opts, group='lbaas_f5')
LOG = logging.getLogger(__name__)

config.read_config()


class F5Driver(base.LoadBalancerDriver):
    def __init__(self):
        self.bigip = bigip.BigIP(
            CONF.lbaas_f5.host,
            CONF.lbaas_f5.username,
            CONF.lbaas_f5.password
        ).ltm

    @staticmethod
    def _install_cert(path, name):
        requests.post(
            url='https://%s/mgmt/tm/sys/crypto/cert' % CONF.lbaas_f5.host,
            data=json.dumps(
                {
                    "fromLocalFile": path,
                    "name": name,
                    "command": "install"
                }
            ),
            verify=False,
            auth=(CONF.lbaas_f5.username, CONF.lbaas_f5.password),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

    @staticmethod
    def _install_key(path, name):
        requests.post(
            url='https://%s/mgmt/tm/sys/crypto/key'
                % CONF.lbaas_f5.host,
            data=json.dumps(
                {
                    "fromLocalFile": path,
                    "name": name,
                    "command": "install"
                }
            ),
            verify=False,
            auth=(CONF.lbaas_f5.username, CONF.lbaas_f5.password),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

    def _create_or_update_ssl_profile(self, name, key_name, cert_name,
                                      options, ciphers):
        profile_resp = requests.get(
            url='https://%s/mgmt/tm/ltm/profile/client-ssl/%s'
                % (CONF.lbaas_f5.host, name),
            auth=(CONF.lbaas_f5.username, CONF.lbaas_f5.password),
            verify=False
        )

        if profile_resp.status_code == 404:
            return self._create_ssl_profile(
                name,
                key_name,
                cert_name,
                options,
                ciphers
            )
        else:
            return self._update_ssl_profile(
                name,
                key_name,
                cert_name,
                options,
                ciphers
            )

    @staticmethod
    def _create_ssl_profile(name, key_name, cert_name,
                            options=None, ciphers=None):
        url = (
            'https://%s/mgmt/tm/ltm/profile/client-ssl' % CONF.lbaas_f5.host
        )

        data = {
            "name": name,
            "cert": cert_name,
            "key": key_name
        }

        if options:
            data['options'] = options

        if ciphers:
            data['ciphers'] = ciphers

        resp = requests.post(
            url=url,
            data=json.dumps(data),
            verify=False,
            auth=(CONF.lbaas_f5.username, CONF.lbaas_f5.password),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        return resp.json()

    @staticmethod
    def _update_ssl_profile(name, key_name, cert_name,
                            options=None, ciphers=None):
        url = (
            'https://%s/mgmt/tm/ltm/profile/client-ssl/%s'
            % (CONF.lbaas_f5.host, name)
        )

        data = {
            "cert": cert_name,
            "key": key_name
        }

        if options:
            data['options'] = options

        if ciphers:
            data['ciphers'] = ciphers

        resp = requests.put(
            url=url,
            data=json.dumps(data),
            verify=False,
            auth=(CONF.lbaas_f5.username, CONF.lbaas_f5.password),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        return resp.json()

    def _assign_ssl_profile(self, ssl_info):
        if not ssl_info:
            return

        # In this case, need to install the cert,
        # the key and the new SSL profile.
        path = ssl_info['path']
        options = ssl_info.get('options', '')
        ciphers = ssl_info.get('ciphers', '')

        name = path.split('/')[-1].split('.')[0]

        # Install the cert and the key.
        self._install_cert(path, name)
        self._install_key(path, name)

        # Create a client SSL profile.
        return self._create_or_update_ssl_profile(
            name,
            "%s.key" % name,
            "%s.crt" % name,
            options,
            ciphers
        )

    @staticmethod
    def _find_member_by_description(pool, mem_description):
        all_members = pool.members_s.get_collection()

        for mem in all_members:
            # Search by name.
            if mem.description == mem_description:
                return mem

    def create_listener(self, listener):
        ssl_profile = self._assign_ssl_profile(listener.ssl_info)

        if not listener.algorithm:
            listener.algorithm = 'round-robin'

        if not listener.address:
            listener.address = '0.0.0.0'

        # Create a new pool associated with current virtual server.
        # Assign default ICMP monitor.
        self.bigip.pools.pool.create(
            name='pool-%s' % listener.name,
            loadBalancingMode=listener.algorithm,
            monitor='gateway_icmp'
        )

        kwargs = {
            'name': 'virtual-%s' % listener.name,
            'pool': 'pool-%s' % listener.name,
            'destination': '%s:%s' % (
                listener.address,
                listener.protocol_port
            ),
            'ipProtocol': listener.protocol
        }

        if ssl_profile:
            kwargs['profiles'] = [{
                'context': 'clientside',
                'name': ssl_profile['name']
            }]

        # Create a new virtual server.
        self.bigip.virtuals.virtual.create(**kwargs)

        return listener

    def delete_listener(self, listener):
        pool = self.bigip.pools.pool.load(name='pool-%s' % listener.name)
        virtual = self.bigip.virtuals.virtual.load(
            name='virtual-%s' % listener.name
        )

        virtual.delete()
        pool.delete()

    def apply_changes(self):
        pass

    def delete_member(self, member):
        # Delete pool member.
        pool = self.bigip.pools.pool.load(
            name='pool-%s' % member.listener.name,
        )

        # Get parent node.
        node = self._get_node_by_address(member.address)

        # Find given member in current pool.
        mem = self._find_member_by_description(
            pool,
            '%s' % member.name
        )

        mem.delete()

        # Try to delete parent node.
        try:
            node.delete()
        except Exception as e:
            # In case if parent node is still used by any other pool member.
            LOG.warning(e)

    def _get_node_by_address(self, address):
        nodes = self.bigip.nodes.get_collection()

        filtered = list(filter(lambda x: x.address == address, nodes))

        return None if not filtered else filtered[0]

    def create_member(self, member):
        # Try to get parent node if it already exists.
        node = self._get_node_by_address(member.address)

        if not node:
            # Create a new node.
            node = self.bigip.nodes.node.create(
                # params
                name='%s' % member.address,
                address=member.address,
                monitor="default",
                partition='Common'
            )

        pool = self.bigip.pools.pool.load(
            name='pool-%s' % member.listener.name,
        )

        # Create a new member in current pool.
        pool.members_s.members.create(
            name='%s:%s' % (node.name, member.protocol_port),
            partition='Common',
            description=member.name
        )

        return member

    def update_listener(self, listener):
        ssl_profile = self._assign_ssl_profile(listener.ssl_info)

        if not listener.algorithm:
            listener.algorithm = 'round-robin'

        # Get the pool associated with current virtual server.
        pool = self.bigip.pools.pool.load(
            name='pool-%s' % listener.name,
        )

        virtual = self.bigip.virtuals.virtual.load(
            name='virtual-%s' % listener.name
        )

        # potential values that could be changed:
        # pool: algorithm,
        # virtual: address, protocol_port, protocol,
        # address, protocol, protocol_port, algorithm, options, ssl_info.

        destination = '%s:%s' % (listener.address, listener.protocol_port)
        update_virtual = (
            destination not in virtual.destination or
            virtual.ipProtocol != listener.protocol or
            ssl_profile
        )
        update_pool = pool.loadBalancingMode != listener.algorithm

        if update_virtual:
            # Update the virtual server.
            kwargs = {
                'destination': '%s:%s' % (
                    listener.address,
                    listener.protocol_port
                ),
                'ipProtocol': listener.protocol
            }

            if ssl_profile:
                kwargs['profiles'] = [{
                    'context': 'clientside',
                    'name': ssl_profile['name']
                }]

            virtual.update(**kwargs)

        if update_pool:
            # Update the pool.
            pool.update(
                loadBalancingMode=listener.algorithm
            )

        return listener

    def update_member(self, member):
        # Replace member on another one.
        self.delete_member(member)

        self.create_member(member)

        return member
