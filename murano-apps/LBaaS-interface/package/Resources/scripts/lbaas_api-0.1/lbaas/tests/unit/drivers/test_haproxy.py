# Copyright 2015 - Mirantis, Inc.
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

import mock

from lbaas.db.v1.sqlalchemy import api as db_api
from lbaas.drivers import haproxy as driver
from lbaas import exceptions as exc
from lbaas.tests.unit import base as test_base
from lbaas.utils import file_utils


class HAProxyDriverTest(test_base.DbTestCase):
    def setUp(self):
        super(HAProxyDriverTest, self).setUp()

        self.haproxy = driver.HAProxyDriver()

    @mock.patch.object(file_utils, 'replace_file')
    def test_create_listener(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin'
        })

        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        self.assertEqual('roundrobin', listener.algorithm)

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            'frontend %s' % listener.name,
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_create_listener_with_options(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin',
            'options': {
                'option': 'forwardfor',
                'reqadd': 'X-Forwarded-Proto:\ https'
            }
        })

        self.haproxy.create_listener(listener)

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            '\toption forwardfor',
            config_data
        )

        self.assertIn(
            '\treqadd X-Forwarded-Proto:\ https',
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_create_listener_with_ssl(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'address': '',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin',
            'ssl_info': {'path': '/config/cert.pem', 'options': ['no-sslv3']}
        })

        self.haproxy.create_listener(listener)

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            '\tbind :80 ssl crt /config/cert.pem no-sslv3',
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_create_member(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin'
        })

        # Create a listener first.
        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        member = db_api.create_member({
            'listener_id': listener.id,
            'name': 'member1',
            'address': '10.0.0.1',
            'protocol_port': 80,
        })

        self.haproxy.create_member(member)

        member = db_api.get_member('member1')

        self.assertEqual('10.0.0.1', member.address)

        self.assertEqual(2, replace_file.call_count)

        config_data = replace_file.call_args[0][1]
        self.assertIn(
            '\tserver %s %s:%s' %
            (member.name, member.address, member.protocol_port),
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_update_listener(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin',
            'address': ''
        })

        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        db_api.update_listener(listener.name, {'protocol_port': 8080})

        self.haproxy.update_listener(listener)

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            'frontend %s' % listener.name,
            config_data
        )

        self.assertIn(
            'bind :%s' % 8080,
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_update_member(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin'
        })

        # Create a listener first.
        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        member = db_api.create_member({
            'listener_id': listener.id,
            'name': 'member1',
            'address': '10.0.0.1',
            'protocol_port': 80,
        })

        member = self.haproxy.create_member(member)

        self.assertEqual(80, member.protocol_port)

        member = db_api.update_member(member.name, {'protocol_port': 8080})

        self.haproxy.update_member(member)

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            '\tserver %s %s:%s' % (member.name, member.address, 8080),
            config_data
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_delete_listener(self, replace_file):
        # Create a listener first.
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin'
        })

        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            'frontend %s' % listener.name,
            config_data
        )

        db_api.delete_listener(listener.name)

        self.haproxy.delete_listener(listener.name)

        config_data = replace_file.call_args[0][1]

        self.assertNotIn(
            'frontend %s' % listener.name,
            config_data
        )
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_listener,
            listener.name
        )

    @mock.patch.object(file_utils, 'replace_file')
    def test_delete_member(self, replace_file):
        listener = db_api.create_listener({
            'name': 'test_listener',
            'description': 'my test settings',
            'protocol': 'http',
            'protocol_port': 80,
            'algorithm': 'roundrobin'
        })

        # Create a listener first.
        self.haproxy.create_listener(listener)

        listener = db_api.get_listener('test_listener')

        member = db_api.create_member({
            'listener_id': listener.id,
            'name': 'member1',
            'address': '10.0.0.1',
            'protocol_port': 80,
        })

        self.haproxy.create_member(member)

        member = db_api.get_member('member1')

        config_data = replace_file.call_args[0][1]

        self.assertIn(
            '\tserver %s %s:%s' %
            (member.name, member.address, member.protocol_port),
            config_data
        )

        db_api.delete_member(member.name)

        self.haproxy.delete_member(member)

        config_data = replace_file.call_args[0][1]

        self.assertNotIn(
            '\tserver %s %s:%s' %
            (member.name, member.address, member.protocol_port),
            config_data
        )
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_member,
            member.name
        )
