"""Competition and Season REST Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.db.session import get_db
from marina.schemas.competition import (
    CompetitionCreate,
    CompetitionRead,
    SeasonCreate,
    SeasonRead,
)
from marina.services.competition_service import CompetitionService

router = APIRouter(prefix="/competitions", tags=["Competitions"])


@router.get("", response_model=List[CompetitionRead], summary="List Competitions")
async def list_competitions(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[CompetitionRead]:
    service = CompetitionService(db)
    items = await service.list_competitions(offset=offset, limit=limit)
    return [CompetitionRead.model_validate(c) for c in items]


@router.post(
    "",
    response_model=CompetitionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Competition",
)
async def create_competition(
    payload: CompetitionCreate,
    db: AsyncSession = Depends(get_db),
) -> CompetitionRead:
    service = CompetitionService(db)
    comp = await service.get_or_create_competition(payload)
    return CompetitionRead.model_validate(comp)


@router.post(
    "/seasons",
    response_model=SeasonRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Season Edition",
)
async def create_season(
    payload: SeasonCreate,
    db: AsyncSession = Depends(get_db),
) -> SeasonRead:
    service = CompetitionService(db)
    season = await service.create_season(payload)
    return SeasonRead.model_validate(season)


@router.get(
    "/seasons/{slug}",
    response_model=SeasonRead,
    summary="Get Season By Slug",
)
async def get_season(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> SeasonRead:
    service = CompetitionService(db)
    try:
        season = await service.get_season_by_slug(slug)
        return SeasonRead.model_validate(season)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
