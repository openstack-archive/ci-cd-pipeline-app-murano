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

import copy
import datetime
import uuid

import mock

from lbaas.db.v1 import api as db_api
from lbaas.db.v1.sqlalchemy import models as db
from lbaas.drivers import driver
from lbaas import exceptions as exc
from lbaas.tests.unit.api import base


LISTENER_FOR_UPDATE = {
    'name': 'test',
    'description': 'my test settings2',
}


LISTENER = {
    'id': str(uuid.uuid4()),
    'name': 'test',
    'description': 'my test settings',
    'protocol': 'HTTP',
    'protocol_port': 80,
    'algorithm': 'ROUND_ROBIN',
    'created_at': '1970-01-01 00:00:00',
    'updated_at': '1970-01-01 00:00:00'
}

LISTENER_DB = db.Listener(
    id=LISTENER['id'],
    name=LISTENER['name'],
    description=LISTENER['description'],
    protocol=LISTENER['protocol'],
    protocol_port=LISTENER['protocol_port'],
    algorithm=LISTENER['algorithm'],
    created_at=datetime.datetime(1970, 1, 1),
    updated_at=datetime.datetime(1970, 1, 1)
)

LISTENER_DB_DICT = LISTENER_DB.to_dict()

FOR_UPDATED_LISTENER = copy.deepcopy(LISTENER_FOR_UPDATE)
UPDATED_LISTENER = copy.deepcopy(LISTENER)
UPDATED_LISTENER_DB = db.Listener(**LISTENER_DB_DICT)

MOCK_LISTENER = mock.MagicMock(return_value=LISTENER_DB)
MOCK_LISTENERS = mock.MagicMock(return_value=[LISTENER_DB])
MOCK_UPDATED_LISTENER = mock.MagicMock(return_value=UPDATED_LISTENER_DB)
MOCK_EMPTY = mock.MagicMock(return_value=[])
MOCK_NOT_FOUND = mock.MagicMock(side_effect=exc.NotFoundException())
MOCK_DUPLICATE = mock.MagicMock(side_effect=exc.DBDuplicateEntryException())
MOCK_DELETE = mock.MagicMock(return_value=None)


class TestListenerController(base.FunctionalTest):
    def setUp(self):
        super(TestListenerController, self).setUp()

        self.driver_origin = driver.LB_DRIVER
        driver.LB_DRIVER = mock.Mock()

    def tearDown(self):
        driver.LB_DRIVER = self.driver_origin

        super(TestListenerController, self).tearDown()

    @mock.patch.object(db_api, 'get_listeners', MOCK_LISTENERS)
    def test_get_all(self):
        resp = self.app.get('/v1/listeners')

        self.assertEqual(200, resp.status_int)
        self.assertEqual(1, len(resp.json['listeners']))

    def test_get_all_empty(self):
        resp = self.app.get('/v1/listeners')

        self.assertEqual(200, resp.status_int)
        self.assertEqual(0, len(resp.json['listeners']))

    @mock.patch.object(db_api, 'get_listener', MOCK_LISTENER)
    def test_get(self):
        resp = self.app.get('/v1/listeners/123')

        self.assertEqual(200, resp.status_int)
        self.assertDictEqual(LISTENER, resp.json)

    @mock.patch.object(db_api, "get_listener", MOCK_NOT_FOUND)
    def test_get_not_found(self):
        resp = self.app.get('/v1/listeners/123', expect_errors=True)

        self.assertEqual(404, resp.status_int)

    @mock.patch.object(db_api, "create_listener", MOCK_LISTENER)
    def test_post(self):
        driver.LB_DRIVER().create_listener = MOCK_LISTENER

        resp = self.app.post_json(
            '/v1/listeners',
            LISTENER
        )

        self.assertEqual(201, resp.status_int)

        self.assertDictEqual(LISTENER, resp.json)

    @mock.patch.object(db_api, "create_listener", MOCK_DUPLICATE)
    def test_post_dup(self):
        driver.LB_DRIVER().create_listener = MOCK_DUPLICATE

        resp = self.app.post_json(
            '/v1/listeners',
            LISTENER,
            expect_errors=True
        )

        self.assertEqual(409, resp.status_int)

    @mock.patch.object(db_api, "update_listener", MOCK_UPDATED_LISTENER)
    def test_put(self):
        driver.LB_DRIVER().update_listener = MOCK_UPDATED_LISTENER

        resp = self.app.put_json(
            '/v1/listeners/test',
            FOR_UPDATED_LISTENER
        )

        self.assertEqual(200, resp.status_int)

        self.assertDictEqual(UPDATED_LISTENER, resp.json)

    @mock.patch.object(db_api, "update_listener", MOCK_NOT_FOUND)
    def test_put_not_found(self):
        driver.LB_DRIVER().update_listener = MOCK_NOT_FOUND

        listener = FOR_UPDATED_LISTENER

        resp = self.app.put_json(
            '/v1/listeners/test',
            listener,
            expect_errors=True
        )

        self.assertEqual(404, resp.status_int)

    @mock.patch.object(db_api, "get_listener", MOCK_LISTENER)
    @mock.patch.object(
        db_api,
        "delete_listener",
        mock.Mock(return_value=None)
    )
    def test_delete(self):
        driver.LB_DRIVER().delete_listener = MOCK_DELETE

        resp = self.app.delete('/v1/listeners/123')

        self.assertEqual(204, resp.status_int)

    @mock.patch.object(db_api, "delete_listener", MOCK_NOT_FOUND)
    def test_delete_not_found(self):
        driver.LB_DRIVER().delete_listener = MOCK_NOT_FOUND

        resp = self.app.delete('/v1/listeners/123', expect_errors=True)

        self.assertEqual(404, resp.status_int)
