"""Add team_squad_memberships, squad_import_history, and player squad columns.

Revision ID: 0003_squad_memberships
Revises: 0002_raw_archive_columns
Create Date: 2026-11-18 12:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from marina.db.base import GUID

# revision identifiers, used by Alembic.
revision: str = "0003_squad_memberships"
down_revision: Union[str, None] = "0002_raw_archive_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add extra columns to players
    op.add_column("players", sa.Column("squad_number", sa.Integer(), nullable=True))
    op.add_column("players", sa.Column("height_m", sa.Float(), nullable=True))
    op.add_column("players", sa.Column("joined_date", sa.Date(), nullable=True))
    op.add_column("players", sa.Column("previous_club", sa.String(length=128), nullable=True))
    op.add_column("players", sa.Column("contract_expiry", sa.Date(), nullable=True))
    op.add_column("players", sa.Column("market_value_inr", sa.BigInteger(), nullable=True))
    op.add_column("players", sa.Column("market_value_original", sa.String(length=64), nullable=True))
    op.add_column("players", sa.Column("source_name", sa.String(length=128), nullable=True))
    op.add_column("players", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))

    # 2. Create team_squad_memberships
    op.create_table(
        "team_squad_memberships",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("season_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("squad_number", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(length=64), nullable=True),
        sa.Column("joined_date", sa.Date(), nullable=True),
        sa.Column("previous_club", sa.String(length=128), nullable=True),
        sa.Column("contract_expiry", sa.Date(), nullable=True),
        sa.Column("market_value_inr", sa.BigInteger(), nullable=True),
        sa.Column("market_value_original", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "team_id", "player_id", name="uq_squad_membership_player_season"),
    )
    op.create_index("ix_team_squad_memberships_team_id", "team_squad_memberships", ["team_id"], unique=False)
    op.create_index("ix_team_squad_memberships_season_id", "team_squad_memberships", ["season_id"], unique=False)
    op.create_index("ix_team_squad_memberships_player_id", "team_squad_memberships", ["player_id"], unique=False)
    op.create_index("ix_team_squad_memberships_is_active", "team_squad_memberships", ["is_active"], unique=False)
    op.create_index("ix_squad_membership_lookup", "team_squad_memberships", ["season_id", "team_id", "squad_number"], unique=False)

    # 3. Create squad_import_history
    op.create_table(
        "squad_import_history",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("season_id", GUID(), nullable=False),
        sa.Column("batch_id", sa.String(length=128), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("total_incoming", sa.Integer(), nullable=False),
        sa.Column("new_players", sa.Integer(), nullable=False),
        sa.Column("updated_players", sa.Integer(), nullable=False),
        sa.Column("deactivated_players", sa.Integer(), nullable=False),
        sa.Column("retained_players", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("report_summary", sa.Text(), nullable=True),
        sa.Column("imported_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_squad_import_history_team_id", "squad_import_history", ["team_id"], unique=False)
    op.create_index("ix_squad_import_history_season_id", "squad_import_history", ["season_id"], unique=False)
    op.create_index("ix_squad_import_history_batch_id", "squad_import_history", ["batch_id"], unique=False)


def downgrade() -> None:
    op.drop_table("squad_import_history")
    op.drop_table("team_squad_memberships")
    op.drop_column("players", "verified_at")
    op.drop_column("players", "source_name")
    op.drop_column("players", "market_value_original")
    op.drop_column("players", "market_value_inr")
    op.drop_column("players", "contract_expiry")
    op.drop_column("players", "previous_club")
    op.drop_column("players", "joined_date")
    op.drop_column("players", "height_m")
    op.drop_column("players", "squad_number")
