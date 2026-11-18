"""Players and Squad Registrations REST Endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.db.session import get_db
from marina.schemas.player import (
    PlayerCreate,
    PlayerRead,
    SquadRegistrationCreate,
    SquadRegistrationRead,
)
from marina.services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["Players & Squads"])


@router.get("", response_model=List[PlayerRead], summary="List Players")
async def list_players(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[PlayerRead]:
    service = PlayerService(db)
    players = await service.list_players(offset=offset, limit=limit)
    return [PlayerRead.model_validate(p) for p in players]


@router.post(
    "",
    response_model=PlayerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Player Identity",
    description="Registers an intrinsic player identity, decoupled from any specific club registration.",
)
async def create_player(
    payload: PlayerCreate,
    db: AsyncSession = Depends(get_db),
) -> PlayerRead:
    service = PlayerService(db)
    player = await service.get_or_create_player(payload)
    return PlayerRead.model_validate(player)


@router.post(
    "/squad-registrations",
    response_model=SquadRegistrationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Player to Club Season Squad",
)
async def register_player_to_squad(
    payload: SquadRegistrationCreate,
    db: AsyncSession = Depends(get_db),
) -> SquadRegistrationRead:
    service = PlayerService(db)
    reg = await service.register_player_to_squad(payload)
    return SquadRegistrationRead.model_validate(reg)


@router.get(
    "/squad-registrations/team/{team_id}/season/{season_id}",
    response_model=List[SquadRegistrationRead],
    summary="Get Club Squad for Designated Season",
)
async def get_team_squad(
    team_id: uuid.UUID,
    season_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[SquadRegistrationRead]:
    service = PlayerService(db)
    registrations = await service.list_team_squad(team_id=team_id, season_id=season_id)
    return [SquadRegistrationRead.model_validate(r) for r in registrations]
