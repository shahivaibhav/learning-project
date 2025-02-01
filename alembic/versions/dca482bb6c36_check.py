"""check

Revision ID: dca482bb6c36
Revises: 252efd10a725
Create Date: 2025-01-31 16:14:04.566161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy import Integer, String, DateTime, func, ForeignKey


# revision identifiers, used by Alembic.
revision: str = 'dca482bb6c36'
down_revision: Union[str, None] = '252efd10a725'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'user_campaign_sequence',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('user_campaign_id', Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_date', DateTime(timezone=True), nullable=False),
        sa.Column('created_at', DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('user_campaign_sequence')