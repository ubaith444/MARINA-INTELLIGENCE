"""Teams and Venues REST Endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.db.session import get_db
from marina.schemas.team import (
    LeadershipGroupResponse,
    TeamCreate,
    TeamRead,
    VenueCreate,
    VenueRead,
)
from marina.services.leadership_service import LeadershipService
from marina.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams & Venues"])


@router.get("/leadership-group", response_model=LeadershipGroupResponse, summary="Get Season Leadership Group")
async def get_season_leadership_group(
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> LeadershipGroupResponse:
    """Returns the verified five-member leadership group for Chennaiyin FC in ISL 2026–27."""
    service = LeadershipService(db)
    return await service.get_leadership_group(season_id=season_id)


@router.get("/{team_id}/leadership-group", response_model=LeadershipGroupResponse, summary="Get Team Leadership Group")
async def get_team_leadership_group(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> LeadershipGroupResponse:
    """Returns the season-specific leadership group for a designated club."""
    service = LeadershipService(db)
    return await service.get_leadership_group(team_id=team_id, season_id=season_id)


@router.get("", response_model=List[TeamRead], summary="List Football Clubs")
async def list_teams(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[TeamRead]:
    service = TeamService(db)
    teams = await service.list_teams(offset=offset, limit=limit)
    return [TeamRead.model_validate(t) for t in teams]


@router.post(
    "",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Football Club",
)
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
) -> TeamRead:
    service = TeamService(db)
    team = await service.get_or_create_team(payload)
    return TeamRead.model_validate(team)


@router.get("/{slug}", response_model=TeamRead, summary="Get Team by Slug")
async def get_team(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> TeamRead:
    service = TeamService(db)
    try:
        team = await service.get_by_slug(slug)
        return TeamRead.model_validate(team)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/venues",
    response_model=VenueRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Stadium Venue",
)
async def create_venue(
    payload: VenueCreate,
    db: AsyncSession = Depends(get_db),
) -> VenueRead:
    service = TeamService(db)
    venue = await service.get_or_create_venue(payload)
    return VenueRead.model_validate(venue)
