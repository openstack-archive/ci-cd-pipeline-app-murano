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

import itertools

from oslo_concurrency import processutils

from lbaas.db.v1 import api as db_api
from lbaas.drivers import base
from lbaas.utils import file_utils


class HAProxyDriver(base.LoadBalancerDriver):
    config_file = "/etc/haproxy/haproxy.cfg"
    config = []

    def __init__(self):
        self._sync_configuration()

    def _sync_configuration(self):
        pass

    def create_listener(self, listener):
        # For HAProxy, default listener address is 0.0.0.0.
        if not listener.address:
            listener.address = '0.0.0.0'

        if not listener.algorithm:
            listener.algorithm = 'roundrobin'

        self._save_config()

        return listener

    def update_listener(self, listener):
        self._save_config()

        return listener

    def delete_listener(self, listener):
        self._save_config()

    def delete_member(self, member):
        self._save_config()

    def update_member(self, member):
        self._save_config()

        return member

    def create_member(self, member):
        self._save_config()

        return member

    def _save_config(self):
        conf = []
        conf.extend(_build_global())
        conf.extend(_build_defaults())

        for l in db_api.get_listeners():
            conf.extend(_build_frontend(l))
            conf.extend(_build_backend(l))

        file_utils.replace_file(self.config_file, '\n'.join(conf))

    def apply_changes(self):
        if db_api.get_listeners():
            cmd = 'sudo service haproxy restart'.split()
        else:
            # There is no listeners at all.
            cmd = 'sudo service haproxy stop'.split()
        return processutils.execute(*cmd)


def _build_global(user_group='nogroup'):
    opts = [
        'log 127.0.0.1   syslog info',
        'daemon',
        'user nobody',
        'group %s' % user_group,
    ]

    return itertools.chain(['global'], ('\t' + o for o in opts))


def _build_defaults():
    opts = [
        'log global',
        'retries 3',
        'option redispatch',
        'maxconn 64000',
        'timeout connect 30000ms',
        'timeout client 50000',
        'timeout server 50000',
    ]

    return itertools.chain(['defaults'], ('\t' + o for o in opts))


def _build_frontend(listener):
    bind_str = 'bind %s:%s' % (
        listener.address,
        listener.protocol_port
    )

    if listener.ssl_info:
        path = listener.ssl_info['path']
        options = listener.ssl_info.get('options', '')
        ciphers = listener.ssl_info.get('ciphers', '')

        bind_str = "%s ssl crt %s" % (
            bind_str,
            ' '.join([path, ' '.join(options), ciphers])
        )

    opts = [
        'mode %s' % listener.protocol,
        'default_backend %s' % listener.name,
        bind_str
    ]

    listener_options = ['%s %s' % (k, v) for k, v in listener.options.items()]

    frontend_line = 'frontend %s' % listener.name

    return itertools.chain(
        [frontend_line],
        ('\t' + o for o in opts),
        ('\t' + o for o in listener_options),
    )


def _build_backend(listener):
    opts = [
        'mode %s' % listener.protocol,
        'balance %s' % listener.algorithm,
    ]

    for mem in listener.members:
        opts += [
            'server %s %s:%s'
            % (mem.name, mem.address, mem.protocol_port)
        ]

    listener_line = 'backend %s' % listener.name

    return itertools.chain([listener_line], ('\t' + o for o in opts))
