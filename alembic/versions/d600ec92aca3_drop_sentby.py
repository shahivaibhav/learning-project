"""Drop sentby

Revision ID: d600ec92aca3
Revises: 61006134042f
Create Date: 2025-02-06 13:59:58.289915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd600ec92aca3'
down_revision: Union[str, None] = '61006134042f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('send_campaigns', 'sent_by')


def downgrade() -> None:
    op.add_column('send_campaigns', sa.Column('sent_by', sa.Integer, nullable=True))
