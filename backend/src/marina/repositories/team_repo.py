"""Team and Venue Repositories."""

from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.team import Team, Venue
from marina.repositories.base import BaseRepository


class VenueRepository(BaseRepository[Venue]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Venue, session)

    async def get_by_name(self, name: str) -> Optional[Venue]:
        res = await self.session.execute(select(Venue).where(Venue.name == name))
        return res.scalars().first()


class TeamRepository(BaseRepository[Team]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Team, session)

    async def get_by_slug(self, slug: str) -> Optional[Team]:
        stmt = (
            select(Team)
            .where(Team.slug == slug)
            .options(selectinload(Team.primary_venue))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_short_name(self, short_name: str) -> Optional[Team]:
        stmt = (
            select(Team)
            .where(Team.short_name == short_name)
            .options(selectinload(Team.primary_venue))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_teams(self, offset: int = 0, limit: int = 50) -> Sequence[Team]:
        stmt = (
            select(Team)
            .options(selectinload(Team.primary_venue))
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
