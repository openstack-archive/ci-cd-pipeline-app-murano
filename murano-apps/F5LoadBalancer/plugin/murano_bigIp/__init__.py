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


from f5 import bigip
from murano.dsl import dsl
from oslo_log import log as logging
from yaql.language import specs
from yaql.language import yaqltypes


LOG = logging.getLogger(__name__)


class BigIpClient(object):
    @specs.parameter('user', yaqltypes.String())
    @specs.parameter('password', yaqltypes.String())
    @specs.parameter('host', yaqltypes.String())
    def __init__(self, user, password, host):
        self._host = host
        self._user = user
        self._password = password
        self._client = bigip.BigIP(
            self._host,
            self._user,
            self._password
        ).ltm

    @staticmethod
    def _find_member_by_description(pool, mem_description):
        all_members = pool.members_s.get_collection()

        for mem in all_members:
            # Search by name.
            if mem.description == mem_description:
                return mem

    @specs.parameter('listener', dsl.MuranoObjectParameter('org.openstack.murano.lbaas.Listener'))
    def create_listener(self, listener):

        if not listener.algorithm:
            listener.algorithm = 'round-robin'

        if not listener.address:
            listener.address = '0.0.0.0'

        # Create a new pool associated with current virtual server.
        # Assign default ICMP monitor.
        self._client.pools.pool.create(
            name='pool-%s' % listener.name,
            loadBalancingMode=listener.algorithm,
            monitor='gateway_icmp'
        )

        kwargs = {
            'name': 'virtual-%s' % listener.name,
            'pool': 'pool-%s' % listener.name,
            'destination': '%s:%s' % (
                listener.address,
                listener.port
            ),
            'ipProtocol': listener.protocol
        }

        # Create a new virtual server.
        self._client.virtuals.virtual.create(**kwargs)

        return listener

    @specs.parameter('listener', dsl.MuranoObjectParameter('org.openstack.murano.lbaas.Listener'))
    def delete_listener(self, listener):
        pool = self._client.pools.pool.load(name='pool-%s' % listener.name)
        virtual = self._client.virtuals.virtual.load(
            name='virtual-%s' % listener.name
        )

        virtual.delete()
        pool.delete()

    @specs.parameter('member', dict)
    def delete_member(self, member):
        # Delete pool member.
        pool = self._client.pools.pool.load(
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
        nodes = self._client.nodes.get_collection()

        filtered = list(filter(lambda x: x.address == address, nodes))

        return None if not filtered else filtered[0]

    @specs.parameter('name', yaqltypes.String())
    @specs.parameter('algorithm', yaqltypes.String())
    @specs.parameter('listener', yaqltypes.String())
    def create_pool(self, name, algorithm, listener):
        if not algorithm:
            algorithm = 'round-robin'

        pool = self._client.pools.pool.create(
            name='pool-%s' % name,
            loadBalancingMode=algorithm,
            monitor='gateway_icmp'
        )

        virtual = self._client.virtuals.virtual.load(
            name='virtual-%s' % listener
        )

        kwargs = {'pool': pool.name}
        virtual.update(**kwargs)

        return pool

    @specs.parameter('pname', yaqltypes.String())
    @specs.parameter('member', dict)
    def create_member(self, member, pname):
        # Try to get parent node if it already exists.
        node = self._get_node_by_address(member.address)

        if not node:
            # Create a new node.
            node = self._client.nodes.node.create(
                # params
                name='%s' % member["host"],
                address=member["address"],
                monitor="default",
                partition='Common'
            )

        pool = self._client.pools.pool.load(
            name='pool-%s' % pname,
        )

        # Create a new member in current pool.
        pool.members_s.members.create(
            name='%s:%s' % (node.name, member["port"]),
            partition='Common',
            description=member["host"]
        )

        return member

    @specs.parameter('listener', dsl.MuranoObjectParameter('org.openstack.murano.lbaas.Listener'))
    def update_listener(self, listener):

        if not listener.algorithm:
            listener.algorithm = 'round-robin'

        # Get the pool associated with current virtual server.
        pool = self._client.pools.pool.load(
            name='pool-%s' % listener.name,
        )

        virtual = self._client.virtuals.virtual.load(
            name='virtual-%s' % listener.name
        )

        # potential values that could be changed:
        # pool: algorithm,
        # virtual: address, port, protocol,
        # address, protocol, port, algorithm, options, ssl_info.

        destination = '%s:%s' % (listener.address, listener.port)
        update_virtual = (
            destination not in virtual.destination or
            virtual.ipProtocol != listener.protocol
        )
        update_pool = pool.loadBalancingMode != listener.algorithm

        if update_virtual:
            # Update the virtual server.
            kwargs = {
                'destination': '%s:%s' % (
                    listener.address,
                    listener.port
                ),
                'ipProtocol': listener.protocol
            }

            virtual.update(**kwargs)

        if update_pool:
            # Update the pool.
            pool.update(
                loadBalancingMode=listener.algorithm
            )

        return listener

    @specs.parameter('member', dict)
    def update_member(self, member):
        # Replace member on another one.
        self.delete_member(member)

        self.create_member(member)

        return member

