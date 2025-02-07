"""integer sent_by

Revision ID: 0e4f43901db7
Revises: ecd50562db49
Create Date: 2025-02-06 14:35:56.315197

"""
from typing import Sequence, Union
from sqlalchemy import Integer
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e4f43901db7'
down_revision: Union[str, None] = 'ecd50562db49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'send_campaigns', sa.Column('sent_by', Integer, nullable=False))


def downgrade() -> None:
    pass
