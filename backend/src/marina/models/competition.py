"""Competition and Season Domain Models."""

import uuid
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from marina.models.match import Match
    from marina.models.player import SquadRegistration


class Competition(Base, TimestampMixin):
    """Football competition / tournament entity (e.g., Indian Super League)."""
    __tablename__ = "competitions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    country: Mapped[str] = mapped_column(String(64), default="India", nullable=False)
    federation: Mapped[str] = mapped_column(String(64), default="AIFF", nullable=False)
    tier: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    competition_type: Mapped[str] = mapped_column(String(32), default="LEAGUE", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    seasons: Mapped[List["Season"]] = relationship(
        "Season", back_populates="competition", cascade="all, delete-orphan", order_by="desc(Season.start_date)"
    )


class Season(Base, TimestampMixin):
    """Season edition for a competition (e.g., ISL 2026–27, extensible to future ISL seasons)."""
    __tablename__ = "seasons"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    competition_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "2026–27"
    slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # e.g. "isl-2026-27"
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    competition: Mapped["Competition"] = relationship("Competition", back_populates="seasons")
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="season", cascade="all, delete-orphan")
    squad_registrations: Mapped[List["SquadRegistration"]] = relationship(
        "SquadRegistration", back_populates="season", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("competition_id", "name", name="uq_season_competition_name"),
        UniqueConstraint("competition_id", "slug", name="uq_season_competition_slug"),
    )
