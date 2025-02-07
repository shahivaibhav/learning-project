"""Soft delete

Revision ID: 092e3fe3c419
Revises: b5f37440d94f
Create Date: 2025-02-06 11:21:47.392371

"""
from typing import Sequence, Union
from sqlalchemy import Integer, Boolean
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '092e3fe3c419'
down_revision: Union[str, None] = 'b5f37440d94f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_campaign', sa.Column('is_deleted', Boolean, nullable=False, server_default='false'))


def downgrade() -> None:
    pass
