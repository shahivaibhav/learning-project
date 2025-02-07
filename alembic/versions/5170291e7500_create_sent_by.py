"""Create sent by

Revision ID: 5170291e7500
Revises: d600ec92aca3
Create Date: 2025-02-06 14:01:26.920146

"""
from typing import Sequence, Union
from sqlalchemy import Integer, ForeignKey
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5170291e7500'
down_revision: Union[str, None] = 'd600ec92aca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'send_campaigns', sa.Column('sent_by', Integer, ForeignKey('users.user_id', ondelete='CASCADE')))

def downgrade() -> None:
    pass
