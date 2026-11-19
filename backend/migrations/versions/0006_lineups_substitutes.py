"""Add match_lineups and match_substitutes tables.

Revision ID: 0006_lineups_substitutes
Revises: 0005_match_data_integration
Create Date: 2026-11-18 15:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from marina.db.base import GUID

# revision identifiers, used by Alembic.
revision: str = "0006_lineups_substitutes"
down_revision: Union[str, None] = "0005_match_data_integration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create match_lineups
    op.create_table(
        "match_lineups",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("lineup_role", sa.String(length=32), nullable=False, server_default="STARTER"),
        sa.Column("position", sa.String(length=32), nullable=True),
        sa.Column("tactical_formation", sa.String(length=32), nullable=True),
        sa.Column("jersey_number", sa.Integer(), nullable=True),
        sa.Column("is_captain", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("minutes_played", sa.Integer(), nullable=True),
        sa.Column("sub_out_minute", sa.Integer(), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False, server_default="VERIFIED"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_lineup_player"),
    )
    op.create_index("ix_match_lineups_match_id", "match_lineups", ["match_id"], unique=False)
    op.create_index("ix_match_lineups_team_id", "match_lineups", ["team_id"], unique=False)
    op.create_index("ix_match_lineups_player_id", "match_lineups", ["player_id"], unique=False)

    # 2. Create match_substitutes
    op.create_table(
        "match_substitutes",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("jersey_number", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=32), nullable=True),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("sub_in_minute", sa.Integer(), nullable=True),
        sa.Column("sub_out_minute", sa.Integer(), nullable=True),
        sa.Column("replaced_player_id", GUID(), nullable=True),
        sa.Column("minutes_played", sa.Integer(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("verification_status", sa.String(length=32), nullable=False, server_default="VERIFIED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["replaced_player_id"], ["players.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_substitute_player"),
    )
    op.create_index("ix_match_substitutes_match_id", "match_substitutes", ["match_id"], unique=False)
    op.create_index("ix_match_substitutes_team_id", "match_substitutes", ["team_id"], unique=False)
    op.create_index("ix_match_substitutes_player_id", "match_substitutes", ["player_id"], unique=False)


def downgrade() -> None:
    op.drop_table("match_substitutes")
    op.drop_table("match_lineups")
