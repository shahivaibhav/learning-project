"""Message Table

Revision ID: 85703d1d800e
Revises: 4f34411ca05e
Create Date: 2025-01-25 17:09:02.704056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Integer, Boolean, DateTime, func, ForeignKey


# revision identifiers, used by Alembic.
revision: str = '85703d1d800e'
down_revision: Union[str, None] = '4f34411ca05e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_messages',
        sa.Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_campaign_id', Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', Integer, ForeignKey('auth_user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_selected', Boolean, default=True)
    )


def downgrade() -> None:
    op.drop_table("user_messages")
