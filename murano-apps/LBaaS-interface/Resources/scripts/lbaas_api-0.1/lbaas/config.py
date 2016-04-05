# -*- coding: utf-8 -*-
#
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

"""
Configuration options registration and useful routines.
"""

from oslo_config import cfg
from oslo_log import log

from lbaas import version


api_opts = [
    cfg.StrOpt('host', default='0.0.0.0', help='LBaaS API server host'),
    cfg.PortOpt('port', default=8993, help='LBaaS API server port'),
]

pecan_opts = [
    cfg.StrOpt(
        'root',
        default='lbaas.api.controllers.root.RootController',
        help='Pecan root controller'
    ),
    cfg.ListOpt(
        'modules',
        default=["lbaas.api"],
        help='A list of modules where pecan will search for '
        'applications.'
    ),
    cfg.BoolOpt(
        'debug',
        default=False,
        help='Enables the ability to display tracebacks in the '
             'browser and interactively debug during development.'
    ),
]


lbaas_opts = [
    cfg.StrOpt(
        'impl',
        default='haproxy',
        help='Implementation driver for LBaaS'
    ),
]


CONF = cfg.CONF

API_GROUP = 'api'
LBAAS_GROUP = 'lbaas'
PECAN_GROUP = 'pecan'

CONF.register_opts(api_opts, group=API_GROUP)
CONF.register_opts(lbaas_opts, group=LBAAS_GROUP)
CONF.register_opts(pecan_opts, group=PECAN_GROUP)


_DEFAULT_LOG_LEVELS = [
    'sqlalchemy=WARN',
    'eventlet.wsgi.server=WARN',
    'stevedore=INFO',
]


def list_opts():
    return [
        (API_GROUP, api_opts),
        (LBAAS_GROUP, lbaas_opts),
        (PECAN_GROUP, pecan_opts),
    ]


def parse_args(args=None, usage=None, default_config_files=None):
    log.set_defaults(default_log_levels=_DEFAULT_LOG_LEVELS)
    log.register_options(CONF)
    CONF(
        args=args,
        project='lbaas',
        version=version,
        usage=usage,
        default_config_files=default_config_files
    )


def read_config():
    CONF(project='lbaas')
