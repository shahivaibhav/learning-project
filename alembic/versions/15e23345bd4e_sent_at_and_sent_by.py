"""sent at and sent by

Revision ID: 15e23345bd4e
Revises: 9c670c89f176
Create Date: 2025-02-07 10:39:31.373310

"""
from typing import Sequence, Union
from sqlalchemy import Integer, DateTime, func
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15e23345bd4e'
down_revision: Union[str, None] = '9c670c89f176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_messages', sa.Column('sent_by', Integer, nullable=False))
    op.add_column('user_messages', sa.Column('sent_at', DateTime, server_default=func.now(), nullable=False))


def downgrade() -> None:
    pass
