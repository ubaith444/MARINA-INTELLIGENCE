"""Competition and Season Repositories."""

from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.competition import Competition, Season
from marina.repositories.base import BaseRepository


class CompetitionRepository(BaseRepository[Competition]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Competition, session)

    async def get_by_code(self, code: str) -> Optional[Competition]:
        stmt = (
            select(Competition)
            .where(Competition.code == code)
            .options(selectinload(Competition.seasons))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()


class SeasonRepository(BaseRepository[Season]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Season, session)

    async def get_by_slug(self, slug: str) -> Optional[Season]:
        stmt = (
            select(Season)
            .where(Season.slug == slug)
            .options(selectinload(Season.competition))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_current_season(self, competition_code: str = "ISL") -> Optional[Season]:
        stmt = (
            select(Season)
            .join(Competition)
            .where(Competition.code == competition_code, Season.is_current.is_(True))
            .options(selectinload(Season.competition))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()
