"""Storing all sent Campaigns

Revision ID: 252efd10a725
Revises: 85703d1d800e
Create Date: 2025-01-28 16:49:43.871256

"""
from typing import Sequence, Union
from sqlalchemy import Integer, ForeignKey

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '252efd10a725'
down_revision: Union[str, None] = '85703d1d800e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
    # op.create_table(
    #     'send_campaigns',
    #     sa.Column('id', Integer, primary_key=True, autoincrement=True),
    #     sa.Column('user_campaign_id', Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False)
    # )


def downgrade() -> None:
    op.drop_table("send_campaigns")
