"""Merge heads add_coin_toss_type_enum and 4cc99aba3c27

Revision ID: 8538a0d0fc45
Revises: add_coin_toss_type_enum, 4cc99aba3c27
Create Date: 2025-10-08 03:47:52.445384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8538a0d0fc45'
down_revision = ('add_coin_toss_type_enum', '4cc99aba3c27')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass