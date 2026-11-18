"""Statistics Service Enforcing MARINA INTELLIGENCE Data Integrity Rules.

RULES:
1. Never fabricate Chennaiyin FC 2026–27 match results or player statistics.
2. Do not convert unavailable statistics to zero. Unmeasured values MUST remain None/NULL.
3. Statistics are strictly rejected for scheduled / unplayed fixtures.
4. Every statistic entry requires validated source provenance.
"""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    EntityNotFoundError,
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.models.common import MatchStatus
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.repositories.match_repo import MatchRepository
from marina.repositories.provenance_repo import DataSourceRepository
from marina.repositories.statistics_repo import (
    PlayerStatisticsRepository,
    TeamStatisticsRepository,
)
from marina.schemas.statistics import (
    PlayerMatchStatisticCreate,
    TeamMatchStatisticCreate,
)


class StatisticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.team_stats_repo = TeamStatisticsRepository(session)
        self.player_stats_repo = PlayerStatisticsRepository(session)
        self.match_repo = MatchRepository(session)
        self.data_source_repo = DataSourceRepository(session)

    async def record_team_statistics(
        self, payload: TeamMatchStatisticCreate
    ) -> TeamMatchStatistic:
        # 1. Verify match existence and status
        match = await self.match_repo.get_by_id(payload.match_id)
        if not match:
            raise EntityNotFoundError(f"Match {payload.match_id} does not exist.")

        # Data Integrity: Reject statistics for fixtures that haven't occurred
        if match.match_status in (
            MatchStatus.SCHEDULED,
            MatchStatus.TIMED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        ):
            raise FabricatedDataViolationError(
                f"Cannot record statistics for match in '{match.match_status}' status. "
                "Data fabrication for unplayed or scheduled fixtures is strictly forbidden."
            )

        # 2. Verify data source provenance
        source = await self.data_source_repo.get_by_id(payload.data_source_id)
        if not source:
            raise IntegrityConstraintViolationError(
                f"Data source {payload.data_source_id} does not exist. Provenance tracking is mandatory."
            )

        # 3. Create record preserving None for unmeasured metrics
        stat_entity = TeamMatchStatistic(**payload.model_dump())
        return await self.team_stats_repo.create(stat_entity)

    async def record_player_statistics(
        self, payload: PlayerMatchStatisticCreate
    ) -> PlayerMatchStatistic:
        # 1. Verify match existence and status
        match = await self.match_repo.get_by_id(payload.match_id)
        if not match:
            raise EntityNotFoundError(f"Match {payload.match_id} does not exist.")

        # Data Integrity: Reject statistics for fixtures that haven't occurred
        if match.match_status in (
            MatchStatus.SCHEDULED,
            MatchStatus.TIMED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        ):
            raise FabricatedDataViolationError(
                f"Cannot record statistics for player in match with status '{match.match_status}'. "
                "Fabrication of upcoming fixture statistics is strictly prohibited."
            )

        # 2. Verify data source provenance
        source = await self.data_source_repo.get_by_id(payload.data_source_id)
        if not source:
            raise IntegrityConstraintViolationError(
                f"Data source {payload.data_source_id} does not exist. Provenance tracking is mandatory."
            )

        # 3. Create record preserving None for unmeasured metrics
        stat_entity = PlayerMatchStatistic(**payload.model_dump())
        return await self.player_stats_repo.create(stat_entity)
