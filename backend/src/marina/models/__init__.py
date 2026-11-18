"""SQLAlchemy Models Registry for MARINA INTELLIGENCE."""

from marina.db.base import Base, GUID, TimestampMixin
from marina.models.common import (
    BatchStatus,
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    ProviderType,
    SquadStatus,
    VerificationStatus,
)
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match, MatchEvent
from marina.models.player import Player, SquadRegistration
from marina.models.provenance import DataSource, ImportHistory
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team, Venue

__all__ = [
    "Base",
    "GUID",
    "TimestampMixin",
    "BatchStatus",
    "EventType",
    "LineupRole",
    "MatchPeriod",
    "MatchStatus",
    "PlayerPosition",
    "ProviderType",
    "SquadStatus",
    "VerificationStatus",
    "Competition",
    "Season",
    "Venue",
    "Team",
    "Player",
    "SquadRegistration",
    "Match",
    "Lineup",
    "MatchEvent",
    "TeamMatchStatistic",
    "PlayerMatchStatistic",
    "DataSource",
    "ImportHistory",
]
