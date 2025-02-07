"""Sent By

Revision ID: 87d74a82a37f
Revises: 092e3fe3c419
Create Date: 2025-02-06 12:04:01.182807

"""
from typing import Sequence, Union
from sqlalchemy import Integer, ForeignKey
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87d74a82a37f'
down_revision: Union[str, None] = '092e3fe3c419'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_by', Integer, ForeignKey('users.id', ondelete='CASCADE')))

def downgrade() -> None:
    op.drop_column('send_campaigns', 'sent_by')
