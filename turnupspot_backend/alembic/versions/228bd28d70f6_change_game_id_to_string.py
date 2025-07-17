"""change_game_id_to_string

Revision ID: 228bd28d70f6
Revises: 98d1ae7dcbb8
Create Date: 2025-07-17 00:35:09.063569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '228bd28d70f6'
down_revision = '98d1ae7dcbb8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('game_players_game_id_fkey', 'game_players', type_='foreignkey')
    op.drop_constraint('game_teams_game_id_fkey', 'game_teams', type_='foreignkey')
    op.drop_constraint('game_day_participants_game_id_fkey', 'game_day_participants', type_='foreignkey')

    # Alter column types
    op.alter_column('game_players', 'game_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('game_teams', 'game_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('game_day_participants', 'game_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('games', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('games_id_seq'::regclass)"))

    # Recreate foreign key constraints
    op.create_foreign_key('game_players_game_id_fkey', 'game_players', 'games', ['game_id'], ['id'])
    op.create_foreign_key('game_teams_game_id_fkey', 'game_teams', 'games', ['game_id'], ['id'])
    op.create_foreign_key('game_day_participants_game_id_fkey', 'game_day_participants', 'games', ['game_id'], ['id'])


def downgrade() -> None:
    # Drop new foreign key constraints
    op.drop_constraint('game_players_game_id_fkey', 'game_players', type_='foreignkey')
    op.drop_constraint('game_teams_game_id_fkey', 'game_teams', type_='foreignkey')
    op.drop_constraint('game_day_participants_game_id_fkey', 'game_day_participants', type_='foreignkey')

    # Revert column types
    op.alter_column('games', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('games_id_seq'::regclass)"))
    op.alter_column('game_teams', 'game_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('game_players', 'game_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('game_day_participants', 'game_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # Recreate old foreign key constraints
    op.create_foreign_key('game_players_game_id_fkey', 'game_players', 'games', ['game_id'], ['id'])
    op.create_foreign_key('game_teams_game_id_fkey', 'game_teams', 'games', ['game_id'], ['id'])
    op.create_foreign_key('game_day_participants_game_id_fkey', 'game_day_participants', 'games', ['game_id'], ['id'])