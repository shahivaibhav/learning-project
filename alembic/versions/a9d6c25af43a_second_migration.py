"""Second migration

Revision ID: a9d6c25af43a
Revises: be7704624190
Create Date: 2025-01-20 16:42:16.593497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a9d6c25af43a'
down_revision: Union[str, None] = 'be7704624190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the PracticeUser table with a ForeignKey to User
    op.create_table(
        'users',  # Table name
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_user.id'), ondelete='CASCADE'),  # ForeignKey to Django's User model
        sa.Column('roles', sa.String(), nullable=True),
    )


def downgrade() -> None:
    # Drop the PracticeUser table in case of rollback
    op.drop_table('users')
