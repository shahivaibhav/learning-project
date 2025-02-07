"""Associate with Existing user

Revision ID: b5f37440d94f
Revises: dca482bb6c36
Create Date: 2025-02-05 12:04:49.490538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy import Integer, String, DateTime, func, ForeignKey

# revision identifiers, used by Alembic.
revision: str = 'b5f37440d94f'
down_revision: Union[str, None] = 'dca482bb6c36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
    # op.create_table(
    #     'associated_practices',
    #     sa.Column('id', Integer, primary_key=True, autoincrement=True),
    #     sa.Column('existing_user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # )


def downgrade() -> None:
    op.drop_table('associated_practices')
