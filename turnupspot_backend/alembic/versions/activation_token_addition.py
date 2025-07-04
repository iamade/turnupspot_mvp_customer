"""add activation_token column to users table

Revision ID: 123456789abc
Revises: f48844ffe2e7
Create Date: 2024-06-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '123456789abc'
down_revision = 'f48844ffe2e7'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('activation_token', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'activation_token') 