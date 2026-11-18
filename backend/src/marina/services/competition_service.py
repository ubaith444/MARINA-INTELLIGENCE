"""Competition and Season Domain Services."""

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.models.competition import Competition, Season
from marina.repositories.competition_repo import (
    CompetitionRepository,
    SeasonRepository,
)
from marina.schemas.competition import CompetitionCreate, SeasonCreate


class CompetitionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.comp_repo = CompetitionRepository(session)
        self.season_repo = SeasonRepository(session)

    async def get_or_create_competition(self, payload: CompetitionCreate) -> Competition:
        existing = await self.comp_repo.get_by_code(payload.code)
        if existing:
            return existing
        comp = Competition(**payload.model_dump())
        return await self.comp_repo.create(comp)

    async def create_season(self, payload: SeasonCreate) -> Season:
        season = Season(**payload.model_dump())
        return await self.season_repo.create(season)

    async def list_competitions(self, offset: int = 0, limit: int = 50) -> Sequence[Competition]:
        return await self.comp_repo.list(offset=offset, limit=limit)

    async def list_seasons(self, offset: int = 0, limit: int = 50) -> Sequence[Season]:
        return await self.season_repo.list(offset=offset, limit=limit)

    async def get_current_season(self, competition_code: str = "ISL") -> Optional[Season]:
        return await self.season_repo.get_current_season(competition_code)

    async def get_season_by_slug(self, slug: str) -> Season:
        season = await self.season_repo.get_by_slug(slug)
        if not season:
            raise EntityNotFoundError(f"Season with slug '{slug}' not found.")
        return season
