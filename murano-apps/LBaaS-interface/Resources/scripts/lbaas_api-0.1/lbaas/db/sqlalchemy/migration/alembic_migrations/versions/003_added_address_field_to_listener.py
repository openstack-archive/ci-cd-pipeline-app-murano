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

"""Added address field to listener

Revision ID: 003
Revises: 002
Create Date: 2016-04-01 11:35:09.048572

"""

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'listeners_v1',
        sa.Column('address', sa.String(length=200), nullable=True)
    )
