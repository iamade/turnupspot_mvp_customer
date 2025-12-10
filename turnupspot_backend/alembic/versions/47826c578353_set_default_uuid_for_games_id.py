"""Set default UUID for games.id

Revision ID: 47826c578353
Revises: 8538a0d0fc45
Create Date: 2025-11-20 02:21:52.116132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47826c578353'
down_revision = '8538a0d0fc45'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE games ALTER COLUMN id SET DEFAULT gen_random_uuid();')


def downgrade() -> None:
    op.execute('ALTER TABLE games ALTER COLUMN id DROP DEFAULT;')