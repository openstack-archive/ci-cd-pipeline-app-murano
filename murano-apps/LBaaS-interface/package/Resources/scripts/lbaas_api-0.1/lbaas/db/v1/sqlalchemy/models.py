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

import sqlalchemy as sa
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from lbaas.db.sqlalchemy import model_base as mb
from lbaas.db.sqlalchemy import types as st


# Definition objects.


class Listener(mb.LbaasModelBase):
    """Listener object"""

    __tablename__ = 'listeners_v1'

    __table_args__ = (
        sa.UniqueConstraint('name'),
    )

    id = mb.id_column()
    address = sa.Column(sa.String(200))
    name = sa.Column(sa.String(80))
    description = sa.Column(sa.Text(), nullable=True)
    protocol = sa.Column(sa.String(10))
    protocol_port = sa.Column(sa.Integer())
    algorithm = sa.Column(sa.String(30))
    options = sa.Column(st.JsonDictType(), default={})
    ssl_info = sa.Column(st.JsonDictType(), default={})


class Member(mb.LbaasModelBase):
    """Member object."""

    __tablename__ = 'members_v1'

    __table_args__ = (
        sa.UniqueConstraint('name'),
    )

    # Main properties.
    id = mb.id_column()
    name = sa.Column(sa.String(80))
    description = sa.Column(sa.String(255), nullable=True)

    address = sa.Column(sa.String(200))
    protocol = sa.Column(sa.String(10))
    protocol_port = sa.Column(sa.Integer())
    tags = sa.Column(st.JsonListType())

# Many-to-one for 'Member' and 'Listener'.


Member.listener_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(Listener.id)
)

Listener.members = relationship(
    Member,
    backref=backref('listener', remote_side=[Listener.id]),
    cascade='all, delete-orphan',
    foreign_keys=Member.listener_id,
    lazy='select'
)
