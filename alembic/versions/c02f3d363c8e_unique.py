"""Unique

Revision ID: c02f3d363c8e
Revises: 87d74a82a37f
Create Date: 2025-02-06 12:36:15.584347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c02f3d363c8e'
down_revision: Union[str, None] = '87d74a82a37f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_users_user_id', 'users', ['user_id'])


def downgrade() -> None:
    op.drop_constraint('uq_users_user_id', 'users', type_='unique')
