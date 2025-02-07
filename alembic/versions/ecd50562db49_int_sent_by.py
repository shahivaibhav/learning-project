"""int sent_by

Revision ID: ecd50562db49
Revises: 93e85ffcb628
Create Date: 2025-02-06 14:33:38.208344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecd50562db49'
down_revision: Union[str, None] = '93e85ffcb628'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('send_campaigns', 'sent_by')


def downgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_by', sa.Integer, nullable=True))