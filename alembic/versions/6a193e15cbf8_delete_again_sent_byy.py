"""Delete again sent byy

Revision ID: 6a193e15cbf8
Revises: 5170291e7500
Create Date: 2025-02-06 14:17:26.374104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a193e15cbf8'
down_revision: Union[str, None] = '5170291e7500'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('send_campaigns', 'sent_by')


def downgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_by', sa.Integer, nullable=True))