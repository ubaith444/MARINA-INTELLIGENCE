"""Season Analytics & Data Quality REST Endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from marina.db.session import get_db
from marina.schemas.season_overview import (
    DataQualityResponse,
    PlayerSeasonStatisticItem,
    SeasonFormResponse,
    SeasonHomeAwayResponse,
    SeasonOverviewResponse,
    SeasonResultItem,
    SeasonScoringResponse,
    TopScorerItem,
)
from marina.services.season_overview_service import SeasonOverviewService

router = APIRouter(tags=["Season Performance Overview"])


@router.get(
    "/season/overview",
    response_model=SeasonOverviewResponse,
    summary="Get Dynamic Season KPIs",
    description="Returns dynamically calculated season KPIs (Played, Remaining, W, D, L, Points, GF, GA, GD, Win %, Clean Sheets).",
)
async def get_season_overview(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> SeasonOverviewResponse:
    service = SeasonOverviewService(db)
    return await service.get_overview(season_id=season_id, team_id=team_id)


@router.get(
    "/season/analytics",
    summary="Get Full Season Performance Analytics",
    description="Returns aggregate season KPIs, 5-match form, home/away record splits, scoring performance, and top scorers directly from stored match records.",
)
async def get_full_season_analytics(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SeasonOverviewService(db)
    overview = await service.get_overview(season_id=season_id, team_id=team_id)
    form = await service.get_form(season_id=season_id, team_id=team_id)
    home_away = await service.get_home_away(season_id=season_id, team_id=team_id)
    scoring = await service.get_scoring(season_id=season_id, team_id=team_id)
    top_scorers = await service.get_top_scorers(season_id=season_id, team_id=team_id, limit=5)

    return {
        "overview": overview.model_dump(),
        "form": form.model_dump(),
        "home_away": home_away.model_dump(),
        "scoring": scoring.model_dump(),
        "top_scorers": [s.model_dump() for s in top_scorers],
    }


@router.get(
    "/season/form",
    response_model=SeasonFormResponse,
    summary="Get Recent Season Form",
    description="Returns chronological form of the last 5 completed matches with opponents, scores and outcomes. Empty list if 0 matches played.",
)
async def get_season_form(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> SeasonFormResponse:
    service = SeasonOverviewService(db)
    return await service.get_form(season_id=season_id, team_id=team_id)


@router.get(
    "/season/results",
    response_model=List[SeasonResultItem],
    summary="Get Season Results List",
    description="Returns all verified completed match results for the season. Empty list if 0 matches completed.",
)
async def get_season_results(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> List[SeasonResultItem]:
    service = SeasonOverviewService(db)
    return await service.get_results(season_id=season_id, team_id=team_id)


@router.get(
    "/season/home-away",
    response_model=SeasonHomeAwayResponse,
    summary="Get Home vs Away Performance Splits",
    description="Returns home vs away record splits with played, scheduled, wins, draws, losses, points, GF, GA, GD and win %.",
)
async def get_season_home_away(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> SeasonHomeAwayResponse:
    service = SeasonOverviewService(db)
    return await service.get_home_away(season_id=season_id, team_id=team_id)


@router.get(
    "/season/scoring",
    response_model=SeasonScoringResponse,
    summary="Get Season Scoring Performance",
    description="Returns aggregate goals scored, conceded, goals per match, clean sheets, and home/away goal distributions.",
)
async def get_season_scoring(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> SeasonScoringResponse:
    service = SeasonOverviewService(db)
    return await service.get_scoring(season_id=season_id, team_id=team_id)


@router.get(
    "/data-quality",
    response_model=DataQualityResponse,
    summary="Get Database Integrity & Quality Audit",
    description="Runs automated data integrity checks across squad, fixtures, unplayed score safety, and historical season isolation.",
)
async def get_data_quality_report(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    db: AsyncSession = Depends(get_db),
) -> DataQualityResponse:
    service = SeasonOverviewService(db)
    return await service.get_data_quality_report(season_id=season_id)


@router.get(
    "/season/top-scorers",
    response_model=List[TopScorerItem],
    summary="Get Top Goal Scorers and Assist Leaders",
)
async def get_top_scorers(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[TopScorerItem]:
    service = SeasonOverviewService(db)
    return await service.get_top_scorers(season_id=season_id, team_id=team_id, limit=limit)


@router.get(
    "/season/player-stats",
    response_model=List[PlayerSeasonStatisticItem],
    summary="Get Detailed Player Season Statistics",
)
async def get_player_season_stats(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> List[PlayerSeasonStatisticItem]:
    service = SeasonOverviewService(db)
    return await service.get_player_season_stats(season_id=season_id, team_id=team_id)


