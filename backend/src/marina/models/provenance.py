"""Data Provenance and Ingestion History Models."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin
from marina.models.common import BatchStatus, ProviderType

if TYPE_CHECKING:
    from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
    from marina.models.match import Match, MatchEvent


class DataSource(Base, TimestampMixin):
    """Catalog of authoritative sources feeding the MARINA INTELLIGENCE platform."""
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, name="provider_type_enum"),
        nullable=False,
        default=ProviderType.OFFICIAL_LEAGUE,
    )
    base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    api_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    import_batches: Mapped[List["ImportHistory"]] = relationship(
        "ImportHistory", back_populates="data_source", cascade="all, delete-orphan"
    )
    team_statistics: Mapped[List["TeamMatchStatistic"]] = relationship(
        "TeamMatchStatistic", back_populates="data_source"
    )
    player_statistics: Mapped[List["PlayerMatchStatistic"]] = relationship(
        "PlayerMatchStatistic", back_populates="data_source"
    )
    match_events: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", back_populates="data_source"
    )


class ImportHistory(Base, TimestampMixin):
    """Audit log of ingestion batches and provenance tracking."""
    __tablename__ = "import_history"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[BatchStatus] = mapped_column(
        Enum(BatchStatus, name="batch_status_enum"),
        nullable=False,
        default=BatchStatus.PENDING,
    )
    records_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checksum_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    payload_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="import_batches")

    __table_args__ = (
        Index("ix_import_history_source_batch", "data_source_id", "batch_id"),
    )


class DataSyncLog(Base, TimestampMixin):
    """Audit log of automated and manual data synchronization runs."""
    __tablename__ = "data_sync_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    sync_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS")
    matches_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discrepancy_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DataMetricVerification(Base, TimestampMixin):
    """Metric-by-metric provenance tracking conflicting provider values and dispute flags."""
    __tablename__ = "data_verification"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    match_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=True, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    primary_source: Mapped[str] = mapped_column(String(64), nullable=False)
    primary_value: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    secondary_source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    secondary_value: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="VERIFIED", nullable=False)
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    match: Mapped[Optional["Match"]] = relationship("Match")

