"""Team and Player Match Statistics Domain Models.
STRICT DATA INTEGRITY RULES:
1. Never fabricate statistics for upcoming or unplayed fixtures.
2. Unavailable statistics MUST remain NULL (None); NEVER convert missing metrics to 0.
3. Every statistic row MUST record its authoritative data source provenance and verification status.
"""

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from marina.db.base import Base, GUID, TimestampMixin
from marina.models.common import VerificationStatus

if TYPE_CHECKING:
    from marina.models.match import Match
    from marina.models.player import Player
    from marina.models.provenance import DataSource
    from marina.models.team import Team


class TeamMatchStatistic(Base, TimestampMixin):
    """Aggregate team performance metrics for a single match fixture.
    All metric columns are strictly nullable to prevent artificial zero-filling.
    """
    __tablename__ = "team_match_statistics"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="team_stats_verification_enum"),
        nullable=False,
        default=VerificationStatus.PROVISIONAL,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Possession & Territory (Nullable: only populated when recorded by provider)
    possession_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Shooting & Attacking Metrics
    shots_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shots_on_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shots_off_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blocked_shots: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expected_goals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # xG
    expected_goals_conceded: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # xGA
    big_chances_created: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    big_chances_missed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Passing & Distribution
    passes_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passes_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pass_accuracy_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    touches: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Defending & Disciplinary
    tackles_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tackles_won: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interceptions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clearances: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    saves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    corners: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    offsides: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fouls_committed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yellow_cards: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    red_cards: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="team_statistics")
    team: Mapped["Team"] = relationship("Team", back_populates="team_statistics")
    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="team_statistics", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", "data_source_id", name="uq_team_match_stat_source"),
        Index("ix_team_match_stats_lookup", "team_id", "match_id"),
    )


class PlayerMatchStatistic(Base, TimestampMixin):
    """Granular individual player performance metrics for a single match fixture.
    All metric columns are strictly nullable to prevent artificial zero-filling.
    """
    __tablename__ = "player_match_statistics"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="player_stats_verification_enum"),
        nullable=False,
        default=VerificationStatus.PROVISIONAL,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Participation
    minutes_played: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Attacking
    goals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    assists: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shots_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shots_on_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expected_goals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # xG
    expected_assists: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # xA
    key_passes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dribbles_attempted: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dribbles_succeeded: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Distribution
    passes_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passes_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pass_accuracy_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    crosses_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    crosses_successful: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Defending & Duels
    tackles_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tackles_won: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interceptions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clearances: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blocks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    aerial_duels_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    aerial_duels_won: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ground_duels_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ground_duels_won: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Discipline & Goalkeeping
    fouls_committed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fouls_drawn: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yellow_cards: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    red_cards: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    saves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    goals_conceded: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clean_sheet: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Physical / Tracking
    distance_covered_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sprints_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    top_speed_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="player_statistics")
    player: Mapped["Player"] = relationship("Player", back_populates="statistics", lazy="selectin")
    team: Mapped["Team"] = relationship("Team", lazy="selectin")
    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="player_statistics", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("match_id", "player_id", "data_source_id", name="uq_player_match_stat_source"),
        Index("ix_player_match_stats_lookup", "player_id", "match_id"),
    )
