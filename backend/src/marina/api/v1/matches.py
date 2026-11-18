"""Matches REST Endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    EntityNotFoundError,
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.db.session import get_db
from marina.models.common import MatchStatus
from marina.schemas.match import MatchCreate, MatchDetailRead, MatchRead
from marina.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches & Fixtures"])


@router.get("", response_model=List[MatchRead], summary="List Fixtures & Matches")
async def list_matches(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[MatchStatus] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    service = MatchService(db)
    matches = await service.list_matches(
        season_id=season_id,
        team_id=team_id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return [MatchRead.model_validate(m) for m in matches]


@router.post(
    "",
    response_model=MatchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule Match Fixture",
    description="Schedules a match fixture. For upcoming fixtures, scores must remain NULL to ensure data integrity.",
)
async def create_match(
    payload: MatchCreate,
    db: AsyncSession = Depends(get_db),
) -> MatchRead:
    service = MatchService(db)
    try:
        match = await service.schedule_match(payload)
        return MatchRead.model_validate(match)
    except (FabricatedDataViolationError, IntegrityConstraintViolationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{match_id}", response_model=MatchDetailRead, summary="Get Match Details")
async def get_match_detail(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MatchDetailRead:
    service = MatchService(db)
    try:
        match = await service.get_match_detail(match_id)
        return MatchDetailRead.model_validate(match)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
