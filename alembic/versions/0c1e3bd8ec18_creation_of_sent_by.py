"""Creation of sent by

Revision ID: 0c1e3bd8ec18
Revises: 6a193e15cbf8
Create Date: 2025-02-06 14:18:25.904797

"""
from typing import Sequence, Union
from sqlalchemy import Integer, ForeignKey
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c1e3bd8ec18'
down_revision: Union[str, None] = '6a193e15cbf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'send_campaigns', sa.Column('sent_by', Integer, ForeignKey('users.id', ondelete='CASCADE')))


def downgrade() -> None:
    pass
