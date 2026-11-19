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
from marina.models.match import Lineup, Match, MatchEvent, MatchLineup, MatchPass, MatchShot, MatchSubstitute
from marina.models.player import (
    Player,
    SquadImportHistory,
    SquadRegistration,
    TeamSquadMembership,
)
from marina.models.provenance import DataMetricVerification, DataSource, DataSyncLog, ImportHistory
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import SeasonLeadershipMember, Team, Venue

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
    "SeasonLeadershipMember",
    "Player",
    "SquadRegistration",
    "TeamSquadMembership",
    "SquadImportHistory",
    "Match",
    "Lineup",
    "MatchLineup",
    "MatchSubstitute",
    "MatchEvent",
    "MatchShot",
    "MatchPass",
    "TeamMatchStatistic",
    "PlayerMatchStatistic",
    "DataSource",
    "ImportHistory",
    "DataSyncLog",
    "DataMetricVerification",
]
