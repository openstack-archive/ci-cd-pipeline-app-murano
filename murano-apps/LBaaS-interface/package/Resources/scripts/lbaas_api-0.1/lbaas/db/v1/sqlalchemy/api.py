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
import sys

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log as logging
import sqlalchemy as sa

from lbaas.db.sqlalchemy import base as b
from lbaas.db.v1.sqlalchemy import models
from lbaas import exceptions as exc

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def get_backend():
    """Consumed by openstack common code.

    The backend is this module itself.
    :return Name of db backend.
    """
    return sys.modules[__name__]


def setup_db():
    try:
        models.Listener.metadata.create_all(b.get_engine())
    except sa.exc.OperationalError as e:
        raise exc.DBException("Failed to setup database: %s" % e)


def drop_db():
    global _facade

    try:
        models.Listener.metadata.drop_all(b.get_engine())
        _facade = None
    except Exception as e:
        raise exc.DBException("Failed to drop database: %s" % e)


# Transaction management.

def start_tx():
    b.start_tx()


def commit_tx():
    b.commit_tx()


def rollback_tx():
    b.rollback_tx()


def end_tx():
    b.end_tx()


@contextlib.contextmanager
def transaction():
    try:
        start_tx()
        yield
        commit_tx()
    finally:
        end_tx()


def _secure_query(model, *columns):
    query = b.model_query(model, columns)

    return query


def _paginate_query(model, limit=None, marker=None, sort_keys=None,
                    sort_dirs=None, query=None):
    if not query:
        query = _secure_query(model)

    query = db_utils.paginate_query(
        query,
        model,
        limit,
        sort_keys if sort_keys else {},
        marker=marker,
        sort_dirs=sort_dirs
    )

    return query.all()


def _delete_all(model, session=None, **kwargs):
    _secure_query(model).filter_by(**kwargs).delete()


def _get_collection_sorted_by_name(model, **kwargs):
    return _secure_query(model).filter_by(**kwargs).order_by(model.name).all()


def _get_collection_sorted_by_time(model, **kwargs):
    query = _secure_query(model)

    return query.filter_by(**kwargs).order_by(model.created_at).all()


def _get_db_object_by_name(model, name):
    return _secure_query(model).filter_by(name=name).first()


def _get_db_object_by_id(model, id):
    return _secure_query(model).filter_by(id=id).first()


# Member definitions.

def get_member(name):
    member = _get_member(name)

    if not member:
        raise exc.NotFoundException(
            "Member not found [member_name=%s]" % name)

    return member


def load_member(name):
    return _get_member(name)


def get_members(**kwargs):
    return _get_collection_sorted_by_name(models.Member, **kwargs)


@b.session_aware()
def create_member(values, session=None):
    member = models.Member()

    member.update(values.copy())

    try:
        member.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntryException(
            "Duplicate entry for MemberDefinition: %s" % e.columns
        )

    return member


@b.session_aware()
def update_member(name, values, session=None):
    member = _get_member(name)

    if not member:
        raise exc.NotFoundException(
            "Member not found [member_name=%s]" % name)

    member.update(values.copy())

    return member


@b.session_aware()
def create_or_update_member(name, values, session=None):
    if not _get_member(name):
        return create_member(values)
    else:
        return update_member(name, values)


@b.session_aware()
def delete_member(name, session=None):
    member = _get_member(name)

    if not member:
        raise exc.NotFoundException(
            "Member not found [member_name=%s]" % name)

    session.delete(member)


def _get_member(name):
    return _get_db_object_by_name(models.Member, name)


@b.session_aware()
def delete_members(**kwargs):
    return _delete_all(models.Member, **kwargs)


# Listeners.

def get_listener(name):
    listener = _get_listener(name)

    if not listener:
        raise exc.NotFoundException("Listener not found [name=%s]" % name)

    return listener


def load_listener(name):
    return _get_listener(name)


def get_listeners(**kwargs):
    return _get_collection_sorted_by_name(models.Listener, **kwargs)


@b.session_aware()
def create_listener(values, session=None):
    listener = models.Listener()

    listener.update(values)

    try:
        listener.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntryException(
            "Duplicate entry for Listener: %s" % e.columns
        )

    return listener


@b.session_aware()
def update_listener(name, values, session=None):
    listener = _get_listener(name)

    if not listener:
        raise exc.NotFoundException("Listener not found [name=%s]" % name)

    listener.update(values)

    return listener


@b.session_aware()
def create_or_update_listener(name, values, session=None):
    listener = _get_listener(name)

    if not listener:
        return create_listener(values)
    else:
        return update_listener(name, values)


@b.session_aware()
def delete_listener(name, session=None):
    listener = _get_listener(name)

    if not listener:
        raise exc.NotFoundException("Listener not found [name=%s]" % name)

    session.delete(listener)


def _get_listener(name):
    return _get_db_object_by_name(models.Listener, name)


@b.session_aware()
def delete_listeners(**kwargs):
    return _delete_all(models.Listener, **kwargs)
