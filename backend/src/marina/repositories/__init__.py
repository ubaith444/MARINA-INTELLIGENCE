"""Repository Registry for MARINA INTELLIGENCE."""

from marina.repositories.base import BaseRepository
from marina.repositories.competition_repo import (
    CompetitionRepository,
    SeasonRepository,
)
from marina.repositories.match_repo import (
    LineupRepository,
    MatchEventRepository,
    MatchRepository,
)
from marina.repositories.player_repo import (
    PlayerRepository,
    SquadRegistrationRepository,
)
from marina.repositories.provenance_repo import (
    DataSourceRepository,
    ImportHistoryRepository,
)
from marina.repositories.statistics_repo import (
    PlayerStatisticsRepository,
    TeamStatisticsRepository,
)
from marina.repositories.team_repo import TeamRepository, VenueRepository

__all__ = [
    "BaseRepository",
    "CompetitionRepository",
    "SeasonRepository",
    "VenueRepository",
    "TeamRepository",
    "PlayerRepository",
    "SquadRegistrationRepository",
    "MatchRepository",
    "LineupRepository",
    "MatchEventRepository",
    "TeamStatisticsRepository",
    "PlayerStatisticsRepository",
    "DataSourceRepository",
    "ImportHistoryRepository",
]
