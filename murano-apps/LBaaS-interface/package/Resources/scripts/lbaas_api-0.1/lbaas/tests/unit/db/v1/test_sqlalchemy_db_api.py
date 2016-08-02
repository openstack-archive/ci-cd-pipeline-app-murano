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

from lbaas.db.v1.sqlalchemy import api as db_api
from lbaas import exceptions as exc
from lbaas.tests.unit import base as test_base


MEMBERS = [
    {
        'name': 'my_member1',
        'description': 'empty',
        'tags': ['mc'],
        'updated_at': None,
        'address': '10.0.0.1',
        'protocol_port': 80,
    },
    {
        'name': 'my_member2',
        'description': 'my description',
        'tags': ['mc'],
        'updated_at': None,
        'address': '10.0.0.2',
        'protocol_port': 80,
    },
]


class MemberTest(test_base.DbTestCase):
    def test_create_and_get_and_load_member(self):
        created = db_api.create_member(MEMBERS[0])

        fetched = db_api.get_member(created['name'])

        self.assertEqual(created, fetched)

        fetched = db_api.load_member(created.name)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_member("not-existing-wb"))

    def test_update_member(self):
        created = db_api.create_member(MEMBERS[0])

        self.assertIsNone(created.updated_at)

        updated = db_api.update_member(
            created.name,
            {'description': 'my new description'}
        )

        self.assertEqual('my new description', updated.description)

        fetched = db_api.get_member(created['name'])

        self.assertEqual(updated, fetched)
        self.assertIsNotNone(fetched.updated_at)

    def test_create_or_update_member(self):
        name = MEMBERS[0]['name']

        self.assertIsNone(db_api.load_member(name))

        created = db_api.create_or_update_member(
            name,
            MEMBERS[0]
        )

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.name)

        updated = db_api.create_or_update_member(
            created.name,
            {'description': 'my new description'}
        )

        self.assertEqual('my new description', updated.description)
        self.assertEqual(
            'my new description',
            db_api.load_member(updated.name).description
        )

        fetched = db_api.get_member(created.name)

        self.assertEqual(updated, fetched)

    def test_get_members(self):
        created0 = db_api.create_member(MEMBERS[0])
        created1 = db_api.create_member(MEMBERS[1])

        fetched = db_api.get_members()

        self.assertEqual(2, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual(created1, fetched[1])

    def test_delete_member(self):
        created = db_api.create_member(MEMBERS[0])

        fetched = db_api.get_member(created.name)

        self.assertEqual(created, fetched)

        db_api.delete_member(created.name)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_member,
            created.name
        )

    def test_member_repr(self):
        s = db_api.create_member(MEMBERS[0]).__repr__()

        self.assertIn('Member ', s)
        self.assertIn("'name': 'my_member1'", s)


LISTENERS = [
    {
        'name': 'listener1',
        'description': 'Test Listener #1',
        'protocol': 'HTTP',
        'protocol_port': 80,
        'algorithm': 'ROUND_ROBIN',
    },
    {
        'name': 'listener2',
        'description': 'Test Listener #2',
        'protocol': 'HTTP',
        'protocol_port': 80,
        'algorithm': 'SOURCE',
    }
]


class ListenerTest(test_base.DbTestCase):
    def setUp(self):
        super(ListenerTest, self).setUp()

        db_api.delete_listeners()

    def test_create_and_get_and_load_listener(self):
        created = db_api.create_listener(LISTENERS[0])

        fetched = db_api.get_listener(created.name)

        self.assertEqual(created, fetched)

        fetched = db_api.load_listener(created.name)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_listener("not-existing-id"))

    def test_update_listener(self):
        created = db_api.create_listener(LISTENERS[0])

        self.assertIsNone(created.updated_at)

        updated = db_api.update_listener(
            created.name,
            {'description': 'my new desc'}
        )

        self.assertEqual('my new desc', updated.description)

        fetched = db_api.get_listener(created.name)

        self.assertEqual(updated, fetched)
        self.assertIsNotNone(fetched.updated_at)

    def test_create_or_update_listener(self):
        name = 'not-existing-id'

        self.assertIsNone(db_api.load_listener(name))

        created = db_api.create_or_update_listener(name, LISTENERS[0])

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.name)

        updated = db_api.create_or_update_listener(
            created.name,
            {'description': 'my new desc'}
        )

        self.assertEqual('my new desc', updated.description)
        self.assertEqual(
            'my new desc',
            db_api.load_listener(updated.name).description
        )

        fetched = db_api.get_listener(created.name)

        self.assertEqual(updated, fetched)

    def test_get_listeners(self):
        created0 = db_api.create_listener(LISTENERS[0])
        created1 = db_api.create_listener(LISTENERS[1])

        fetched = db_api.get_listeners()

        self.assertEqual(2, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual(created1, fetched[1])

    def test_delete_listener(self):
        created = db_api.create_listener(LISTENERS[0])

        fetched = db_api.get_listener(created.name)

        self.assertEqual(created, fetched)

        db_api.delete_listener(created.name)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_listener,
            created.name
        )

    def test_listener_repr(self):
        s = db_api.create_listener(LISTENERS[0]).__repr__()

        self.assertIn('Listener ', s)
        self.assertIn("'description': 'Test Listener #1'", s)
        self.assertIn("'name': 'listener1'", s)


class TXTest(test_base.DbTestCase):
    def test_rollback(self):
        db_api.start_tx()

        try:
            created = db_api.create_member(MEMBERS[0])
            fetched = db_api.get_member(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

            db_api.rollback_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_member,
            created['id']
        )
        self.assertFalse(self.is_db_session_open())

    def test_commit(self):
        db_api.start_tx()

        try:
            created = db_api.create_member(MEMBERS[0])
            fetched = db_api.get_member(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

            db_api.commit_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_member(created.name)

        self.assertEqual(created, fetched)
        self.assertFalse(self.is_db_session_open())

    def test_commit_transaction(self):
        with db_api.transaction():
            created = db_api.create_member(MEMBERS[0])
            fetched = db_api.get_member(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_member(created.name)

        self.assertEqual(created, fetched)
        self.assertFalse(self.is_db_session_open())

    def test_rollback_multiple_objects(self):
        db_api.start_tx()

        try:
            created = db_api.create_listener(LISTENERS[0])
            fetched = db_api.get_listener(created['name'])

            self.assertEqual(created, fetched)

            created_wb = db_api.create_member(MEMBERS[0])
            fetched_wb = db_api.get_member(created_wb.name)

            self.assertEqual(created_wb, fetched_wb)
            self.assertTrue(self.is_db_session_open())

            db_api.rollback_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_listener,
            created.name
        )
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_member,
            created_wb.name
        )

        self.assertFalse(self.is_db_session_open())

    def test_rollback_transaction(self):
        try:
            with db_api.transaction():
                created = db_api.create_member(MEMBERS[0])
                fetched = db_api.get_member(created.name)

                self.assertEqual(created, fetched)
                self.assertTrue(self.is_db_session_open())

                db_api.create_member(MEMBERS[0])

        except exc.DBDuplicateEntryException:
            pass

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_member,
            created.name
        )

    def test_commit_multiple_objects(self):
        db_api.start_tx()

        try:
            created = db_api.create_listener(LISTENERS[0])
            fetched = db_api.get_listener(created.name)

            self.assertEqual(created, fetched)

            created_wb = db_api.create_member(MEMBERS[0])
            fetched_wb = db_api.get_member(created_wb.name)

            self.assertEqual(created_wb, fetched_wb)
            self.assertTrue(self.is_db_session_open())

            db_api.commit_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_listener(created.name)

        self.assertEqual(created, fetched)

        fetched_wb = db_api.get_member(created_wb.name)

        self.assertEqual(created_wb, fetched_wb)
        self.assertFalse(self.is_db_session_open())
