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

import six

from oslo_config import cfg
from oslo_db import options
from oslo_db.sqlalchemy import session as db_session
from oslo_log import log as logging

from lbaas import exceptions as exc
from lbaas import utils


LOG = logging.getLogger(__name__)

# Note(dzimine): sqlite only works for basic testing.
options.set_defaults(cfg.CONF, connection="sqlite:///lbaas.sqlite")

_DB_SESSION_THREAD_LOCAL_NAME = "db_sql_alchemy_session"

_facade = None


def _get_facade():
    global _facade

    if not _facade:
        _facade = db_session.EngineFacade(
            cfg.CONF.database.connection,
            sqlite_fk=True,
            autocommit=False,
            **dict(six.iteritems(cfg.CONF.database))
        )

    return _facade


def get_engine():
    return _get_facade().get_engine()


def _get_session():
    return _get_facade().get_session()


def _get_thread_local_session():
    return utils.get_thread_local(_DB_SESSION_THREAD_LOCAL_NAME)


def _get_or_create_thread_local_session():
    ses = _get_thread_local_session()

    if ses:
        return ses, False

    ses = _get_session()
    _set_thread_local_session(ses)

    return ses, True


def _set_thread_local_session(session):
    utils.set_thread_local(_DB_SESSION_THREAD_LOCAL_NAME, session)


def session_aware(param_name="session"):
    """Decorator for methods working within db session."""

    def _decorator(func):
        def _within_session(*args, **kw):
            # If 'created' flag is True it means that the transaction is
            # demarcated explicitly outside this module.
            ses, created = _get_or_create_thread_local_session()

            try:
                kw[param_name] = ses

                result = func(*args, **kw)

                if created:
                    ses.commit()

                return result
            except Exception:
                if created:
                    ses.rollback()
                raise
            finally:
                if created:
                    _set_thread_local_session(None)
                    ses.close()

        _within_session.__doc__ = func.__doc__

        return _within_session

    return _decorator


# Transaction management.


def start_tx():
    """Starts transaction.

    Opens new database session and starts new transaction assuming
    there wasn't any opened sessions within the same thread.
    """
    if _get_thread_local_session():
        raise exc.DataAccessException(
            "Database transaction has already been started."
        )

    _set_thread_local_session(_get_session())


def commit_tx():
    """Commits previously started database transaction."""
    ses = _get_thread_local_session()

    if not ses:
        raise exc.DataAccessException(
            "Nothing to commit. Database transaction"
            " has not been previously started."
        )

    ses.commit()


def rollback_tx():
    """Rolls back previously started database transaction."""
    ses = _get_thread_local_session()

    if not ses:
        raise exc.DataAccessException(
            "Nothing to roll back. Database transaction has not been started."
        )

    ses.rollback()


def end_tx():
    """Ends transaction.

    Ends current database transaction.
    It rolls back all uncommitted changes and closes database session.
    """
    ses = _get_thread_local_session()

    if not ses:
        raise exc.DataAccessException(
            "Database transaction has not been started."
        )

    if ses.dirty:
        rollback_tx()

    ses.close()
    _set_thread_local_session(None)


@session_aware()
def get_driver_name(session=None):
    return session.bind.url.drivername


@session_aware()
def model_query(model, columns=(), session=None):
    """Query helper.

    :param model: Base model to query.
    :param columns: Optional. Which columns to be queried.
    """

    if columns:
        return session.query(*columns)

    return session.query(model)
