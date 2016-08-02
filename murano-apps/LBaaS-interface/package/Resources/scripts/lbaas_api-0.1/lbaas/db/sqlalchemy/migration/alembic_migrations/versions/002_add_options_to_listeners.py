# Copyright 2016 OpenStack Foundation.
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

"""Add options to listeners

Revision ID: 002
Revises: 001
Create Date: 2016-01-14 17:15:03.867571

"""

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'

from alembic import op
import sqlalchemy as sa

from lbaas.db.sqlalchemy import types


def upgrade():
    op.add_column(
        'listeners_v1',
        sa.Column('options', types.JsonEncoded(), nullable=True)
    )
    op.add_column(
        'listeners_v1',
        sa.Column('ssl_info', types.JsonEncoded(), nullable=True)
    )
