"""add_coin_toss_type_enum

Revision ID: add_coin_toss_type_enum
Revises: 
Create Date: 2025-10-08 03:45:11.572

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = 'add_coin_toss_type_enum'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the CoinTossType enum
    coin_toss_type_enum = ENUM('draw_decider', 'starting_team', name='cointosstype', create_type=False)
    coin_toss_type_enum.create(op.get_bind(), checkfirst=True)

def downgrade():
    # Drop the CoinTossType enum
    op.execute('DROP TYPE IF EXISTS cointosstype')