"""Team and Venue Services."""

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.models.team import Team, Venue
from marina.repositories.team_repo import TeamRepository, VenueRepository
from marina.schemas.team import TeamCreate, VenueCreate


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.team_repo = TeamRepository(session)
        self.venue_repo = VenueRepository(session)

    async def get_or_create_venue(self, payload: VenueCreate) -> Venue:
        existing = await self.venue_repo.get_by_name(payload.name)
        if existing:
            return existing
        venue = Venue(**payload.model_dump())
        return await self.venue_repo.create(venue)

    async def get_or_create_team(self, payload: TeamCreate) -> Team:
        existing = await self.team_repo.get_by_slug(payload.slug)
        if existing:
            return existing
        team = Team(**payload.model_dump())
        return await self.team_repo.create(team)

    async def list_teams(self, offset: int = 0, limit: int = 50) -> Sequence[Team]:
        return await self.team_repo.list_teams(offset=offset, limit=limit)

    async def get_by_slug(self, slug: str) -> Team:
        team = await self.team_repo.get_by_slug(slug)
        if not team:
            raise EntityNotFoundError(f"Team with slug '{slug}' not found.")
        return team
