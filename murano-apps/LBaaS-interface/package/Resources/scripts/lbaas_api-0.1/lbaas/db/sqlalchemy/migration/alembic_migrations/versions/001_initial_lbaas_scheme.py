# Copyright 2015 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Initial LBaaS scheme

Revision ID: 001
Revises: None
Create Date: 2015-12-11 12:58:30.775597

"""

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None

from alembic import op
import sqlalchemy as sa

from lbaas.db.sqlalchemy import types


def upgrade():
    op.create_table(
        'listeners_v1',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('protocol', sa.String(length=10), nullable=True),
        sa.Column('protocol_port', sa.Integer(), nullable=True),
        sa.Column('algorithm', sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'members_v1',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('protocol', sa.String(length=10), nullable=True),
        sa.Column('protocol_port', sa.Integer(), nullable=True),
        sa.Column('tags', types.JsonEncoded(), nullable=True),
        sa.Column('listener_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['listener_id'], [u'listeners_v1.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
