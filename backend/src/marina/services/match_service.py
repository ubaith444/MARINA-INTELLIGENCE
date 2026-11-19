"""Match Service Enforcing Match Lifecycle and Result Integrity."""

import uuid
from datetime import date
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    EntityNotFoundError,
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.models.common import MatchStatus
from marina.models.match import Match
from marina.repositories.match_repo import MatchRepository
from marina.repositories.team_repo import TeamRepository
from marina.schemas.match import MatchCreate


class MatchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.match_repo = MatchRepository(session)
        self.team_repo = TeamRepository(session)

    async def schedule_match(self, payload: MatchCreate) -> Match:
        # Integrity check: home team and away team cannot be identical
        if payload.home_team_id == payload.away_team_id:
            raise IntegrityConstraintViolationError("Home team and away team cannot be identical.")

        # If match is scheduled in the future, scores MUST NOT be fabricated
        if payload.match_status == MatchStatus.SCHEDULED:
            if payload.home_score is not None or payload.away_score is not None:
                raise FabricatedDataViolationError(
                    "Cannot assign scores to a SCHEDULED fixture. "
                    "Scores must remain null until the match is played."
                )

        match_entity = Match(**payload.model_dump())
        return await self.match_repo.create(match_entity)

    async def get_match_detail(self, match_id: uuid.UUID) -> Match:
        match = await self.match_repo.get_match_detail(match_id)
        if not match:
            raise EntityNotFoundError(f"Match {match_id} not found.")
        return match

    async def list_matches(
        self,
        season_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        status: Optional[MatchStatus] = None,
        is_home: Optional[bool] = None,
        matchweek: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Match]:
        return await self.match_repo.list_matches(
            season_id=season_id,
            team_id=team_id,
            status=status,
            is_home=is_home,
            matchweek=matchweek,
            start_date=start_date,
            end_date=end_date,
            search=search,
            offset=offset,
            limit=limit,
        )
