"""Player and Club Registration Domain Models.
Separates intrinsic human player identity from temporary club/season squad registrations.
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Date, Enum, ForeignKey, Index, Integer, String, UniqueConstraint
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
    weight_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preferred_foot: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # LEFT, RIGHT, BOTH
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    squad_registrations: Mapped[List["SquadRegistration"]] = relationship(
        "SquadRegistration", back_populates="player", cascade="all, delete-orphan"
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
