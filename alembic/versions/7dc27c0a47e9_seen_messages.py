"""Seen messages

Revision ID: 7dc27c0a47e9
Revises: 15e23345bd4e
Create Date: 2025-02-07 11:24:48.224666

"""
from typing import Sequence, Union
from sqlalchemy import Boolean, DateTime, func
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dc27c0a47e9'
down_revision: Union[str, None] = '15e23345bd4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_messages', sa.Column('seen', Boolean, default=False))
    op.add_column(
        'send_campaigns', sa.Column('seen', Boolean, default=False))
    

def downgrade() -> None:
    pass
