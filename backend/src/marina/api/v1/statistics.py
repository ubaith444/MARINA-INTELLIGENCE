"""Statistics REST Endpoints Enforcing Provenance and Non-Fabrication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    EntityNotFoundError,
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.db.session import get_db
from marina.schemas.statistics import (
    PlayerMatchStatisticCreate,
    PlayerMatchStatisticRead,
    TeamMatchStatisticCreate,
    TeamMatchStatisticRead,
)
from marina.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Match Statistics"])


@router.post(
    "/teams",
    response_model=TeamMatchStatisticRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record Team Match Statistics",
    description="Records team metrics with required provenance. Forbids recording stats for scheduled/unplayed fixtures.",
)
async def record_team_statistics(
    payload: TeamMatchStatisticCreate,
    db: AsyncSession = Depends(get_db),
) -> TeamMatchStatisticRead:
    service = StatisticsService(db)
    try:
        record = await service.record_team_statistics(payload)
        return TeamMatchStatisticRead.model_validate(record)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (FabricatedDataViolationError, IntegrityConstraintViolationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/players",
    response_model=PlayerMatchStatisticRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record Player Match Statistics",
    description="Records player metrics with required provenance. Preserves NULL for unmeasured metrics.",
)
async def record_player_statistics(
    payload: PlayerMatchStatisticCreate,
    db: AsyncSession = Depends(get_db),
) -> PlayerMatchStatisticRead:
    service = StatisticsService(db)
    try:
        record = await service.record_player_statistics(payload)
        return PlayerMatchStatisticRead.model_validate(record)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (FabricatedDataViolationError, IntegrityConstraintViolationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
