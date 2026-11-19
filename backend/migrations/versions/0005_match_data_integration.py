"""Add data_sync_logs, data_verification, match_shots, and match_passes tables.

Revision ID: 0005_match_data_integration
Revises: 0004_fixture_management
Create Date: 2026-11-18 14:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from marina.db.base import GUID

# revision identifiers, used by Alembic.
revision: str = "0005_match_data_integration"
down_revision: Union[str, None] = "0004_fixture_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create data_sync_logs
    op.create_table(
        "data_sync_logs",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("sync_type", sa.String(length=64), nullable=False),
        sa.Column("provider_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="SUCCESS"),
        sa.Column("matches_synced", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("discrepancy_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sync_logs_sync_type", "data_sync_logs", ["sync_type"], unique=False)
    op.create_index("ix_data_sync_logs_provider_name", "data_sync_logs", ["provider_name"], unique=False)

    # 2. Create data_verification
    op.create_table(
        "data_verification",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=True),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=True),
        sa.Column("metric_name", sa.String(length=64), nullable=False),
        sa.Column("primary_source", sa.String(length=64), nullable=False),
        sa.Column("primary_value", sa.String(length=128), nullable=True),
        sa.Column("secondary_source", sa.String(length=64), nullable=True),
        sa.Column("secondary_value", sa.String(length=128), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False, server_default="VERIFIED"),
        sa.Column("is_disputed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_verification_match_id", "data_verification", ["match_id"], unique=False)
    op.create_index("ix_data_verification_entity_type", "data_verification", ["entity_type"], unique=False)
    op.create_index("ix_data_verification_metric_name", "data_verification", ["metric_name"], unique=False)

    # 3. Create match_shots
    op.create_table(
        "match_shots",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=True),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=32), nullable=False, server_default="FIRST_HALF"),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("shot_type", sa.String(length=32), nullable=True),
        sa.Column("is_inside_box", sa.Boolean(), nullable=True),
        sa.Column("x_coord", sa.Float(), nullable=True),
        sa.Column("y_coord", sa.Float(), nullable=True),
        sa.Column("expected_goals", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_match_shots_match_id", "match_shots", ["match_id"], unique=False)
    op.create_index("ix_match_shots_player_id", "match_shots", ["player_id"], unique=False)

    # 4. Create match_passes
    op.create_table(
        "match_passes",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=True),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=32), nullable=False, server_default="FIRST_HALF"),
        sa.Column("is_successful", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("pass_type", sa.String(length=32), nullable=True),
        sa.Column("start_x", sa.Float(), nullable=True),
        sa.Column("start_y", sa.Float(), nullable=True),
        sa.Column("end_x", sa.Float(), nullable=True),
        sa.Column("end_y", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_match_passes_match_id", "match_passes", ["match_id"], unique=False)
    op.create_index("ix_match_passes_player_id", "match_passes", ["player_id"], unique=False)


def downgrade() -> None:
    op.drop_table("match_passes")
    op.drop_table("match_shots")
    op.drop_table("data_verification")
    op.drop_table("data_sync_logs")
