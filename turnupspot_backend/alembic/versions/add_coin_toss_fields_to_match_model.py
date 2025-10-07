"""Add coin toss fields to Match model

Revision ID: add_coin_toss_fields
Revises: f46abf58eb28
Create Date: 2025-10-01 16:17:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_coin_toss_fields'
down_revision = 'f46abf58eb28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add coin toss enum type
    coin_toss_type_enum = sa.Enum('draw_decider', 'starting_team', name='cointosstype')
    coin_toss_type_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to matches table
    op.add_column('matches', sa.Column('requires_coin_toss', sa.Boolean(), nullable=True, default=False))
    op.add_column('matches', sa.Column('coin_toss_type', coin_toss_type_enum, nullable=True))
    op.add_column('matches', sa.Column('coin_toss_result', sa.String(), nullable=True))
    op.add_column('matches', sa.Column('coin_toss_winner_id', sa.String(), nullable=True))

    # Add foreign key constraint for coin_toss_winner_id
    op.create_foreign_key(
        'fk_matches_coin_toss_winner_id',
        'matches', 'game_teams',
        ['coin_toss_winner_id'], ['id']
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_matches_coin_toss_winner_id', 'matches', type_='foreignkey')

    # Remove columns
    op.drop_column('matches', 'coin_toss_winner_id')
    op.drop_column('matches', 'coin_toss_result')
    op.drop_column('matches', 'coin_toss_type')
    op.drop_column('matches', 'requires_coin_toss')

    # Drop enum type
    coin_toss_type_enum = sa.Enum('draw_decider', 'starting_team', name='cointosstype')
    coin_toss_type_enum.drop(op.get_bind(), checkfirst=True)