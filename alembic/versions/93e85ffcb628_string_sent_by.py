"""String sent_by

Revision ID: 93e85ffcb628
Revises: 98abad227622
Create Date: 2025-02-06 14:27:46.536017

"""
from typing import Sequence, Union
from sqlalchemy import String
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93e85ffcb628'
down_revision: Union[str, None] = '98abad227622'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'send_campaigns', sa.Column('sent_by', String, nullable=False))


def downgrade() -> None:
    pass
