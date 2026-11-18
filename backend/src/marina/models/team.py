"""Team and Venue Domain Models."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from marina.models.match import Lineup, Match
    from marina.models.player import SquadRegistration
    from marina.models.statistics import TeamMatchStatistic


class Venue(Base, TimestampMixin):
    """Stadium or football ground."""
    __tablename__ = "venues"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    country: Mapped[str] = mapped_column(String(64), default="India", nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    surface: Mapped[Optional[str]] = mapped_column(String(32), default="Natural Grass", nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    teams: Mapped[List["Team"]] = relationship("Team", back_populates="primary_venue")
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="venue")


class Team(Base, TimestampMixin):
    """Football Club entity (e.g. Chennaiyin FC, Kerala Blasters, Mohun Bagan SG, etc.)."""
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    short_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # e.g. "CFC"
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    primary_venue_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, index=True
    )
    primary_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    secondary_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    primary_venue: Mapped[Optional["Venue"]] = relationship(
        "Venue", back_populates="teams", lazy="selectin"
    )
    home_matches: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.home_team_id", back_populates="home_team"
    )
    away_matches: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.away_team_id", back_populates="away_team"
    )
    squad_registrations: Mapped[List["SquadRegistration"]] = relationship(
        "SquadRegistration", back_populates="team", cascade="all, delete-orphan"
    )
    lineups: Mapped[List["Lineup"]] = relationship("Lineup", back_populates="team")
    team_statistics: Mapped[List["TeamMatchStatistic"]] = relationship(
        "TeamMatchStatistic", back_populates="team"
    )
