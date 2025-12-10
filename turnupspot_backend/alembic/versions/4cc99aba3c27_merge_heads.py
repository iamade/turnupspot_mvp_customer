"""merge heads

Revision ID: 4cc99aba3c27
Revises: add_coin_toss_fields, ba462233fa5e
Create Date: 2025-10-01 22:57:45.441134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cc99aba3c27'
down_revision = ('add_coin_toss_fields', 'ba462233fa5e')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass