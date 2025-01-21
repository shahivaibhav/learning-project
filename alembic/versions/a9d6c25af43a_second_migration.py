"""Second migration

Revision ID: a9d6c25af43a
Revises: be7704624190
Create Date: 2025-01-20 16:42:16.593497

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# Revision identifiers
revision: str = 'a9d6c25af43a'
down_revision: Union[str, None] = 'be7704624190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
#     # Create the 'users' table with a ForeignKey to 'auth_user'
#     op.create_table(
#         'users',
#         sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
#         sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_user.id', ondelete='CASCADE'), nullable=False),
#         sa.Column('roles', sa.String(), nullable=True),
#     )


def downgrade() -> None:
    # Drop the 'users' table in case of rollback
    op.drop_table('users')
