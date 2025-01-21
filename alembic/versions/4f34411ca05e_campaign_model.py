"""Campaign Model

Revision ID: 4f34411ca05e
Revises: a9d6c25af43a
Create Date: 2025-01-20 21:30:48.830984

"""
from typing import Sequence, Union
from sqlalchemy import Integer, String, DateTime, func, ForeignKey

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f34411ca05e'
down_revision: Union[str, None] = 'a9d6c25af43a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_campaign',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('type', String, nullable=False),
        sa.Column('text', String, nullable=False),
        sa.Column('description', String, nullable=True),
        sa.Column('status', String, nullable=False),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        sa.Column('created_by', Integer, nullable=False)
    )

    # Create the user_campaign_sequence table
    op.create_table(
        'user_campaign_sequence',
        sa.Column('id', Integer, primary_key=True, autoincrement=True),
        sa.Column('user_campaign_id', Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_date', DateTime(timezone=True), nullable=False),
        sa.Column('status', String, nullable=True),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        sa.Column('created_by', Integer, nullable=False)
    )


def downgrade():
    # Drop the user_campaign_sequence table if we need to downgrade
    # op.execute("DROP TABLE user_campaign CASCADE")
    op.drop_constraint('user_campaign_sequence_user_campaign_id_fkey', 'user_campaign_sequence', type_='foreignkey')
    
    # Now drop the user_campaign table
    op.drop_table('user_campaign')


    # Drop the user_campaign table if we need to downgrade
    