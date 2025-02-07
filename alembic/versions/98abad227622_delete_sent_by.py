"""Delete sent_by

Revision ID: 98abad227622
Revises: 0c1e3bd8ec18
Create Date: 2025-02-06 14:26:57.180607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98abad227622'
down_revision: Union[str, None] = '0c1e3bd8ec18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('send_campaigns', 'sent_by')


def downgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_by', sa.Integer, nullable=True))