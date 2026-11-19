"""Add fixture management and verification columns to matches table.

Revision ID: 0004_fixture_management
Revises: 0003_squad_memberships
Create Date: 2026-11-18 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_fixture_management"
down_revision: Union[str, None] = "0003_squad_memberships"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("matches") as batch_op:
        batch_op.alter_column("scheduled_kickoff", existing_type=sa.DateTime(timezone=True), nullable=True)
        batch_op.add_column(sa.Column("fixture_leg", sa.String(length=32), nullable=True, server_default="FIRST_LEG"))
        batch_op.add_column(sa.Column("publication_status", sa.String(length=32), nullable=False, server_default="PROVISIONAL"))
        batch_op.add_column(sa.Column("verification_status", sa.String(length=32), nullable=False, server_default="PROVISIONAL"))
        batch_op.add_column(sa.Column("venue_verification_status", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("has_discrepancy", sa.Boolean(), nullable=False, server_default=sa.text("0")))
        batch_op.add_column(sa.Column("discrepancy_notes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("source_url", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("kickoff_time_ist", sa.String(length=32), nullable=True))
        batch_op.create_index("ix_matches_season_number", ["season_id", "match_number"], unique=False)
        batch_op.create_index("ix_matches_verification_status", ["verification_status"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("matches") as batch_op:
        batch_op.drop_index("ix_matches_verification_status")
        batch_op.drop_index("ix_matches_season_number")
        batch_op.drop_column("kickoff_time_ist")
        batch_op.drop_column("last_verified_at")
        batch_op.drop_column("source_url")
        batch_op.drop_column("discrepancy_notes")
        batch_op.drop_column("has_discrepancy")
        batch_op.drop_column("venue_verification_status")
        batch_op.drop_column("verification_status")
        batch_op.drop_column("publication_status")
        batch_op.drop_column("fixture_leg")
        batch_op.alter_column("scheduled_kickoff", existing_type=sa.DateTime(timezone=True), nullable=False)
