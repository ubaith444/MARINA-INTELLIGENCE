"""Statistics Repositories with Provenance Enforcement."""

import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.repositories.base import BaseRepository


class TeamStatisticsRepository(BaseRepository[TeamMatchStatistic]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TeamMatchStatistic, session)

    async def get_by_match_team(
        self, match_id: uuid.UUID, team_id: uuid.UUID
    ) -> Sequence[TeamMatchStatistic]:
        stmt = (
            select(TeamMatchStatistic)
            .where(
                TeamMatchStatistic.match_id == match_id,
                TeamMatchStatistic.team_id == team_id,
            )
            .options(selectinload(TeamMatchStatistic.data_source))
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()


class PlayerStatisticsRepository(BaseRepository[PlayerMatchStatistic]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PlayerMatchStatistic, session)

    async def list_by_match(
        self, match_id: uuid.UUID, team_id: Optional[uuid.UUID] = None
    ) -> Sequence[PlayerMatchStatistic]:
        stmt = (
            select(PlayerMatchStatistic)
            .where(PlayerMatchStatistic.match_id == match_id)
            .options(
                selectinload(PlayerMatchStatistic.player),
                selectinload(PlayerMatchStatistic.data_source),
            )
        )
        if team_id:
            stmt = stmt.where(PlayerMatchStatistic.team_id == team_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
