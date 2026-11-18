"""Match, Match Events, and Lineup Domain Models.
Supports future/scheduled fixtures without fabricated scores or outcomes.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin
from marina.models.common import (
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    VerificationStatus,
)

if TYPE_CHECKING:
    from marina.models.competition import Season
    from marina.models.player import Player, SquadRegistration
    from marina.models.provenance import DataSource
    from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
    from marina.models.team import Team, Venue


class Match(Base, TimestampMixin):
    """Single competitive match fixture.
    For future/scheduled seasons (such as ISL 2026–27), scores and stats are strictly NULL.
    """
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    season_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    home_team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    away_team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    venue_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, index=True
    )
    match_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    scheduled_kickoff: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    actual_kickoff: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    match_status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status_enum"),
        nullable=False,
        default=MatchStatus.SCHEDULED,
        index=True,
    )

    # Strictly Nullable Scores: Never fabricate scores for upcoming or pending matches
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_penalty_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_penalty_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attendance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    referee: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    pitch_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    weather_summary: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Relationships
    season: Mapped["Season"] = relationship("Season", back_populates="matches")
    home_team: Mapped["Team"] = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_matches", lazy="selectin"
    )
    away_team: Mapped["Team"] = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_matches", lazy="selectin"
    )
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="matches", lazy="selectin")
    lineups: Mapped[List["Lineup"]] = relationship(
        "Lineup", back_populates="match", cascade="all, delete-orphan", lazy="selectin"
    )
    events: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", back_populates="match", cascade="all, delete-orphan", order_by="MatchEvent.minute", lazy="selectin"
    )
    team_statistics: Mapped[List["TeamMatchStatistic"]] = relationship(
        "TeamMatchStatistic", back_populates="match", cascade="all, delete-orphan"
    )
    player_statistics: Mapped[List["PlayerMatchStatistic"]] = relationship(
        "PlayerMatchStatistic", back_populates="match", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_matches_season_status", "season_id", "match_status"),
        Index("ix_matches_teams", "home_team_id", "away_team_id"),
    )


class Lineup(Base, TimestampMixin):
    """Starting XI, substitutes, and match squad selections."""
    __tablename__ = "lineups"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    squad_registration_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("squad_registrations.id", ondelete="SET NULL"), nullable=True
    )
    lineup_role: Mapped[LineupRole] = mapped_column(
        Enum(LineupRole, name="lineup_role_enum"),
        nullable=False,
        default=LineupRole.STARTER,
    )
    position: Mapped[Optional[PlayerPosition]] = mapped_column(
        Enum(PlayerPosition, name="lineup_position_enum"),
        nullable=True,
    )
    tactical_formation: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # e.g. "4-2-3-1"
    jersey_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_captain: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    minutes_played: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_substitute_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sub_in_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sub_out_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="lineups")
    team: Mapped["Team"] = relationship("Team", back_populates="lineups")
    player: Mapped["Player"] = relationship("Player", back_populates="lineups", lazy="selectin")
    squad_registration: Mapped[Optional["SquadRegistration"]] = relationship(
        "SquadRegistration", back_populates="lineups"
    )

    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_match_player_lineup"),
    )


class MatchEvent(Base, TimestampMixin):
    """Discrete match events: goals, cards, substitutions, VAR decisions."""
    __tablename__ = "match_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True, index=True
    )
    primary_player_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True
    )
    secondary_player_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True
    )
    data_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type_enum"),
        nullable=False,
        index=True,
    )
    period: Mapped[MatchPeriod] = mapped_column(
        Enum(MatchPeriod, name="match_period_enum"),
        nullable=False,
        default=MatchPeriod.FIRST_HALF,
    )
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    stoppage_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status_enum"),
        nullable=False,
        default=VerificationStatus.PROVISIONAL,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="events")
    primary_player: Mapped[Optional["Player"]] = relationship(
        "Player", foreign_keys=[primary_player_id], back_populates="events_as_primary"
    )
    secondary_player: Mapped[Optional["Player"]] = relationship(
        "Player", foreign_keys=[secondary_player_id], back_populates="events_as_secondary"
    )
    data_source: Mapped[Optional["DataSource"]] = relationship(
        "DataSource", back_populates="match_events"
    )

    __table_args__ = (
        Index("ix_match_events_timeline", "match_id", "minute", "period"),
    )
