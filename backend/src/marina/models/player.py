"""Player and Club Registration Domain Models.
Separates intrinsic human player identity from temporary club/season squad registrations.
"""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin
from marina.models.common import PlayerPosition, SquadStatus

if TYPE_CHECKING:
    from marina.models.competition import Season
    from marina.models.match import Lineup, MatchEvent
    from marina.models.statistics import PlayerMatchStatistic
    from marina.models.team import Team


class Player(Base, TimestampMixin):
    """Intrinsic physical football player identity, decoupled from any specific club."""
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    known_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    nationality: Mapped[str] = mapped_column(String(64), default="India", nullable=False, index=True)
    secondary_nationality: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    primary_position: Mapped[PlayerPosition] = mapped_column(
        Enum(PlayerPosition, name="player_position_enum"),
        nullable=False,
        default=PlayerPosition.CM,
    )
    secondary_position: Mapped[Optional[PlayerPosition]] = mapped_column(
        Enum(PlayerPosition, name="player_position_secondary_enum"),
        nullable=True,
    )
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preferred_foot: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # LEFT, RIGHT, BOTH
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Squad & Contract Attributes (Current active snapshot)
    squad_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    joined_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    previous_club: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    contract_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    market_value_inr: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    market_value_original: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, default="Chennaiyin FC Official / Transfermarkt"
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    squad_registrations: Mapped[List["SquadRegistration"]] = relationship(
        "SquadRegistration", back_populates="player", cascade="all, delete-orphan"
    )
    squad_memberships: Mapped[List["TeamSquadMembership"]] = relationship(
        "TeamSquadMembership", back_populates="player", cascade="all, delete-orphan"
    )
    lineups: Mapped[List["Lineup"]] = relationship("Lineup", back_populates="player")
    statistics: Mapped[List["PlayerMatchStatistic"]] = relationship(
        "PlayerMatchStatistic", back_populates="player"
    )
    events_as_primary: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", foreign_keys="MatchEvent.primary_player_id", back_populates="primary_player"
    )
    events_as_secondary: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", foreign_keys="MatchEvent.secondary_player_id", back_populates="secondary_player"
    )


class SquadRegistration(Base, TimestampMixin):
    """Official registration of a player with a club team for a designated season."""
    __tablename__ = "squad_registrations"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    season_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jersey_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    squad_status: Mapped[SquadStatus] = mapped_column(
        Enum(SquadStatus, name="squad_status_enum"),
        nullable=False,
        default=SquadStatus.FIRST_TEAM,
    )
    registered_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deregistered_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="squad_registrations", lazy="selectin")
    team: Mapped["Team"] = relationship("Team", back_populates="squad_registrations", lazy="selectin")
    season: Mapped["Season"] = relationship("Season", back_populates="squad_registrations", lazy="selectin")
    lineups: Mapped[List["Lineup"]] = relationship("Lineup", back_populates="squad_registration")

    __table_args__ = (
        UniqueConstraint("season_id", "team_id", "player_id", name="uq_squad_registration_player_season"),
        Index("ix_squad_reg_lookup", "season_id", "team_id", "jersey_number"),
    )


class TeamSquadMembership(Base, TimestampMixin):
    """Season-specific squad membership for a player in a club roster.
    Preserves historical squad associations and contract terms when rosters roll over.
    """
    __tablename__ = "team_squad_memberships"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    season_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    squad_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    joined_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    previous_club: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    contract_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    market_value_inr: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    market_value_original: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="squad_memberships", lazy="selectin")
    team: Mapped["Team"] = relationship("Team", lazy="selectin")
    season: Mapped["Season"] = relationship("Season", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("season_id", "team_id", "player_id", name="uq_squad_membership_player_season"),
        Index("ix_squad_membership_lookup", "season_id", "team_id", "squad_number"),
    )


class SquadImportHistory(Base, TimestampMixin):
    """Audit log of squad import and synchronization operations."""
    __tablename__ = "squad_import_history"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    season_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    batch_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(128), default="Chennaiyin FC 2026-27 Official Roster", nullable=False)
    total_incoming: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deactivated_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retained_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    report_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imported_by: Mapped[Optional[str]] = mapped_column(String(64), default="admin", nullable=True)

    # Relationships
    team: Mapped["Team"] = relationship("Team", lazy="selectin")
    season: Mapped["Season"] = relationship("Season", lazy="selectin")
