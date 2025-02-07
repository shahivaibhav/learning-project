"""Sent by

Revision ID: 61006134042f
Revises: c02f3d363c8e
Create Date: 2025-02-06 12:40:00.938328

"""
from typing import Sequence, Union
from sqlalchemy import Integer, ForeignKey
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61006134042f'
down_revision: Union[str, None] = 'c02f3d363c8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing constraint and column first
    op.drop_constraint('send_campaigns_sent_by_fkey', 'send_campaigns', type_='foreignkey')
    op.drop_column('send_campaigns', 'sent_by')

    # Add the updated column with new ForeignKey
    op.add_column('send_campaigns', 
        sa.Column('sent_by', Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    )
    


def downgrade() -> None:
    # Revert to previous column definition
    op.drop_constraint('send_campaigns_sent_by_fkey', 'send_campaigns', type_='foreignkey')
    op.drop_column('send_campaigns', 'sent_by')

    # Restore the original column with ForeignKey to users.id
    op.add_column('send_campaigns', 
        sa.Column('sent_by', Integer, ForeignKey('users.id', ondelete='CASCADE'))
    )
