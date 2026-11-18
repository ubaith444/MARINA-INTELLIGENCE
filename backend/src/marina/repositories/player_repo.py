"""Player and Squad Registration Repositories."""

import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.player import Player, SquadRegistration
from marina.repositories.base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Player, session)

    async def get_by_slug(self, slug: str) -> Optional[Player]:
        stmt = (
            select(Player)
            .where(Player.slug == slug)
            .options(selectinload(Player.squad_registrations))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()


class SquadRegistrationRepository(BaseRepository[SquadRegistration]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SquadRegistration, session)

    async def list_by_team_season(
        self, team_id: uuid.UUID, season_id: uuid.UUID
    ) -> Sequence[SquadRegistration]:
        stmt = (
            select(SquadRegistration)
            .where(
                SquadRegistration.team_id == team_id,
                SquadRegistration.season_id == season_id,
                SquadRegistration.is_active.is_(True),
            )
            .options(selectinload(SquadRegistration.player))
            .order_by(SquadRegistration.jersey_number.nulls_last())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
