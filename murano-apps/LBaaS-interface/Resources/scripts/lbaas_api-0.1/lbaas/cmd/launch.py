#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import sys

import eventlet

eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=False if '--use-debugger' in sys.argv else True,
    time=True)

import os

# If ../lbaas/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'lbaas', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from oslo_config import cfg
from oslo_log import log as logging
from wsgiref import simple_server

from lbaas.api import app
from lbaas import config
from lbaas.drivers import driver


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


def launch_api():
    host = cfg.CONF.api.host
    port = cfg.CONF.api.port

    server = simple_server.make_server(
        host,
        port,
        app.setup_app()
    )

    LOG.info("LBaaS API is serving on http://%s:%s (PID=%s)" %
             (host, port, os.getpid()))

    server.serve_forever()


def get_properly_ordered_parameters():
    """Orders launch parameters in the right order.

    In oslo it's important the order of the launch parameters.
    if --config-file came after the command line parameters the command
    line parameters are ignored.
    So to make user command line parameters are never ignored this method
    moves --config-file to be always first.
    """
    args = sys.argv[1:]

    for arg in sys.argv[1:]:
        if arg == '--config-file' or arg.startswith('--config-file='):
            conf_file_value = args[args.index(arg) + 1]
            args.remove(conf_file_value)
            args.remove(arg)
            args.insert(0, arg)
            args.insert(1, conf_file_value)

    return args


def main():
    try:
        config.parse_args(get_properly_ordered_parameters())

        logging.setup(CONF, 'Lbaas')

        driver.load_lb_drivers()

        launch_api()

    except RuntimeError as excp:
        sys.stderr.write("ERROR: %s\n" % excp)
        sys.exit(1)


if __name__ == '__main__':
    main()
