"""Service Layer Registry for MARINA INTELLIGENCE."""

from marina.services.competition_service import CompetitionService
from marina.services.match_service import MatchService
from marina.services.player_service import PlayerService
from marina.services.provenance_service import ProvenanceService
from marina.services.statistics_service import StatisticsService
from marina.services.team_service import TeamService

__all__ = [
    "CompetitionService",
    "TeamService",
    "PlayerService",
    "MatchService",
    "StatisticsService",
    "ProvenanceService",
]
