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

from oslo_config import cfg
import pecan
import pecan.testing
from webtest import app as webtest_app

from lbaas.tests.unit import base


__all__ = ['FunctionalTest']


class FunctionalTest(base.DbTestCase):

    def setUp(self):
        super(FunctionalTest, self).setUp()

        pecan_opts = cfg.CONF.pecan

        self.app = pecan.testing.load_test_app({
            'app': {
                'root': pecan_opts.root,
                'modules': pecan_opts.modules,
                'debug': pecan_opts.debug,
                'auth_enable': False
            }
        })
        self.addCleanup(pecan.set_config, {}, overwrite=True)

    def assertNotFound(self, url):
        try:
            self.app.get(url, headers={'Accept': 'application/json'})
        except webtest_app.AppError as error:
            self.assertIn('Bad response: 404 Not Found', str(error))

            return

        self.fail('Expected 404 Not found but got OK')
