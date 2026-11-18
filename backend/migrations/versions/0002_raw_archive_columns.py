"""Add raw archive tracking columns to import_history.

Revision ID: 0002_raw_archive_columns
Revises: 0001_initial_schema
Create Date: 2026-11-18 11:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_raw_archive_columns"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("import_history", sa.Column("source_url", sa.String(length=512), nullable=True))
    op.add_column("import_history", sa.Column("payload_path", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("import_history", "payload_path")
    op.drop_column("import_history", "source_url")
