"""Match, Lineup, and Match Event Repositories."""

import uuid
from typing import Optional, Sequence
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.common import MatchStatus
from marina.models.match import Lineup, Match, MatchEvent
from marina.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Match, session)

    async def get_match_detail(self, match_id: uuid.UUID) -> Optional[Match]:
        stmt = (
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
                selectinload(Match.lineups).selectinload(Lineup.player),
                selectinload(Match.events),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_matches(
        self,
        season_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        status: Optional[MatchStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Match]:
        stmt = (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
            )
        )
        if season_id:
            stmt = stmt.where(Match.season_id == season_id)
        if team_id:
            stmt = stmt.where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
        if status:
            stmt = stmt.where(Match.match_status == status)

        stmt = stmt.order_by(Match.scheduled_kickoff.asc()).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()


class LineupRepository(BaseRepository[Lineup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Lineup, session)

    async def list_by_match_team(
        self, match_id: uuid.UUID, team_id: uuid.UUID
    ) -> Sequence[Lineup]:
        stmt = (
            select(Lineup)
            .where(Lineup.match_id == match_id, Lineup.team_id == team_id)
            .options(selectinload(Lineup.player))
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()


class MatchEventRepository(BaseRepository[MatchEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MatchEvent, session)

    async def list_by_match(self, match_id: uuid.UUID) -> Sequence[MatchEvent]:
        stmt = (
            select(MatchEvent)
            .where(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.minute.asc(), MatchEvent.stoppage_minute.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
