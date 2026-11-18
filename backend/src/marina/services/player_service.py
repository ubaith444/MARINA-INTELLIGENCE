"""Player Identity and Squad Registration Services."""

import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.models.player import Player, SquadRegistration
from marina.repositories.player_repo import (
    PlayerRepository,
    SquadRegistrationRepository,
)
from marina.schemas.player import PlayerCreate, SquadRegistrationCreate


class PlayerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.player_repo = PlayerRepository(session)
        self.squad_repo = SquadRegistrationRepository(session)

    async def get_or_create_player(self, payload: PlayerCreate) -> Player:
        existing = await self.player_repo.get_by_slug(payload.slug)
        if existing:
            return existing
        player = Player(**payload.model_dump())
        return await self.player_repo.create(player)

    async def register_player_to_squad(
        self, payload: SquadRegistrationCreate
    ) -> SquadRegistration:
        registration = SquadRegistration(**payload.model_dump())
        return await self.squad_repo.create(registration)

    async def list_players(self, offset: int = 0, limit: int = 50) -> Sequence[Player]:
        return await self.player_repo.list(offset=offset, limit=limit)

    async def list_team_squad(
        self, team_id: uuid.UUID, season_id: uuid.UUID
    ) -> Sequence[SquadRegistration]:
        return await self.squad_repo.list_by_team_season(team_id=team_id, season_id=season_id)
