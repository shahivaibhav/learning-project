"""Sent at

Revision ID: 9c670c89f176
Revises: 0e4f43901db7
Create Date: 2025-02-07 10:07:00.727932

"""
from typing import Sequence, Union
from sqlalchemy import DateTime, func
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c670c89f176'
down_revision: Union[str, None] = '0e4f43901db7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_at', DateTime, server_default=func.now(), nullable=False))


def downgrade() -> None:
    op.drop_column('send_campaigns', sa.Column('sent_at'))
