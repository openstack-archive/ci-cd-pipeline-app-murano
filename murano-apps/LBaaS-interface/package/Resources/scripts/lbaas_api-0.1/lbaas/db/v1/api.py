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

import contextlib

from oslo_db import api as db_api
from oslo_log import log as logging

_BACKEND_MAPPING = {
    'sqlalchemy': 'lbaas.db.v1.sqlalchemy.api',
}

IMPL = db_api.DBAPI('sqlalchemy', backend_mapping=_BACKEND_MAPPING)
LOG = logging.getLogger(__name__)


def setup_db():
    IMPL.setup_db()


def drop_db():
    IMPL.drop_db()


# Transaction control.


def start_tx():
    IMPL.start_tx()


def commit_tx():
    IMPL.commit_tx()


def rollback_tx():
    IMPL.rollback_tx()


def end_tx():
    IMPL.end_tx()


@contextlib.contextmanager
def transaction():
    with IMPL.transaction():
        yield


# Members.

def get_member(name):
    return IMPL.get_member(name)


def load_member(name):
    """Unlike get_member this method is allowed to return None."""
    return IMPL.load_member(name)


def get_members():
    return IMPL.get_members()


def create_member(values):
    return IMPL.create_member(values)


def update_member(name, values):
    return IMPL.update_member(name, values)


def create_or_update_member(name, values):
    return IMPL.create_or_update_member(name, values)


def delete_member(name):
    IMPL.delete_member(name)


def delete_members(**kwargs):
    IMPL.delete_members(**kwargs)


# Listeners.

def get_listener(name):
    return IMPL.get_listener(name)


def load_listener(name):
    """Unlike get_listener this method is allowed to return None."""
    return IMPL.load_listener(name)


def get_listeners():
    return IMPL.get_listeners()


def create_listener(values):
    return IMPL.create_listener(values)


def update_listener(name, values):
    return IMPL.update_listener(name, values)


def create_or_update_listener(name, values):
    return IMPL.create_or_update_listener(name, values)


def delete_listener(name):
    IMPL.delete_listener(name)


def delete_listeners(**kwargs):
    IMPL.delete_listeners(**kwargs)
