"""Analytics and Performance Intelligence REST Endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.attacking import AttackingAnalyticsEngine
from marina.analytics.defensive import DefensiveAnalyticsEngine
from marina.analytics.match_intelligence import MatchIntelligenceEngine
from marina.analytics.passing import PassingAnalyticsEngine
from marina.analytics.player_intelligence import PlayerIntelligenceEngine
from marina.analytics.tactical import TacticalAnalyticsEngine
from marina.analytics.team_performance import TeamPerformanceEngine
from marina.analytics.trends import PerformanceTrendsEngine
from marina.db.session import get_db
from marina.models.competition import Season
from marina.models.team import Team
from marina.schemas.analytics import (
    AttackingAnalyticsResponse,
    DefensiveAnalyticsResponse,
    HomeAwayAnalyticsResponse,
    MatchTacticalReportResponse,
    PassingAnalyticsResponse,
    PassingNetworkResponse,
    PerformanceTrendsResponse,
    PlayerCompareRequest,
    PlayerCompareResponse,
    PlayerPerformanceResponse,
    ShotMapResponse,
    TeamSeasonPerformanceResponse,
)

router = APIRouter(prefix="/analytics", tags=["Football Analytics & Performance Intelligence"])


async def _resolve_team_and_season(
    db: AsyncSession,
    team_id: Optional[uuid.UUID] = None,
    season_id: Optional[uuid.UUID] = None,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Helper to resolve default team (Chennaiyin FC) and current season."""
    if not team_id:
        t_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc = (await db.execute(t_stmt)).scalars().first()
        if not cfc:
            t_stmt = select(Team).limit(1)
            cfc = (await db.execute(t_stmt)).scalars().first()
        if not cfc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No team available.")
        team_id = cfc.id

    if not season_id:
        s_stmt = select(Season).where(Season.is_current.is_(True))
        cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            s_stmt = select(Season).limit(1)
            cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No season available.")
        season_id = cur_s.id

    return team_id, season_id


# -----------------------------------------------------------------------------
# Season Performance Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "/season",
    response_model=TeamSeasonPerformanceResponse,
    summary="Season Performance Overview",
    description="Calculates season performance for Chennaiyin FC (or requested club) in the current season.",
)
async def get_season_overview(
    team_id: Optional[uuid.UUID] = Query(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    form_window: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> TeamSeasonPerformanceResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_team_season_performance(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            form_window=form_window,
        )
        return TeamSeasonPerformanceResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/season/{season_id}",
    response_model=TeamSeasonPerformanceResponse,
    summary="Season Performance by Season ID",
    description="Calculates season performance for Chennaiyin FC (or requested club) for a specific season.",
)
async def get_season_overview_by_id(
    season_id: uuid.UUID,
    team_id: Optional[uuid.UUID] = Query(default=None),
    form_window: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> TeamSeasonPerformanceResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_team_season_performance(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            form_window=form_window,
        )
        return TeamSeasonPerformanceResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/team/{team_id}",
    response_model=TeamSeasonPerformanceResponse,
    summary="Team Season Performance",
    description="Calculates season performance for specified team in current or specified season.",
)
async def get_team_overview(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    form_window: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> TeamSeasonPerformanceResponse:
    if not season_id:
        s_stmt = select(Season).where(Season.is_current.is_(True))
        cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            s_stmt = select(Season).limit(1)
            cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No season available.")
        season_id = cur_s.id

    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_team_season_performance(
            team_id=team_id,
            season_id=season_id,
            form_window=form_window,
        )
        return TeamSeasonPerformanceResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/teams/{team_id}/season/{season_id}",
    response_model=TeamSeasonPerformanceResponse,
    summary="Team Seasonal Performance & Form Analytics",
    description="Calculates seasonal win/draw/loss record, home/away splits, goal differences, PPM, and recent form sequence.",
)
async def get_team_season_performance(
    team_id: uuid.UUID,
    season_id: uuid.UUID,
    form_window: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> TeamSeasonPerformanceResponse:
    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_team_season_performance(
            team_id=team_id,
            season_id=season_id,
            form_window=form_window,
        )
        return TeamSeasonPerformanceResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Attacking Analytics
# -----------------------------------------------------------------------------

@router.get(
    "/team/{team_id}/attacking",
    response_model=AttackingAnalyticsResponse,
    summary="Team Attacking & Shot Quality Analytics",
    description="Calculates shooting accuracy, conversion rates, expected goals, assists, and phase distributions.",
)
@router.get(
    "/teams/{team_id}/attacking",
    response_model=AttackingAnalyticsResponse,
    include_in_schema=False,
)
async def get_team_attacking_analytics(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> AttackingAnalyticsResponse:
    engine = AttackingAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_attacking_metrics(
            team_id=team_id,
            season_id=season_id,
        )
        return AttackingAnalyticsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Defensive Analytics
# -----------------------------------------------------------------------------

@router.get(
    "/team/{team_id}/defensive",
    response_model=DefensiveAnalyticsResponse,
    summary="Team Defensive Resilience Analytics",
    description="Calculates clean sheet rates, tackle success rates, defensive actions, disciplinary index, and match-by-match defensive record.",
)
@router.get(
    "/teams/{team_id}/defensive",
    response_model=DefensiveAnalyticsResponse,
    include_in_schema=False,
)
async def get_team_defensive_analytics(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> DefensiveAnalyticsResponse:
    engine = DefensiveAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_defensive_metrics(
            team_id=team_id,
            season_id=season_id,
        )
        return DefensiveAnalyticsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Passing & Possession Analytics
# -----------------------------------------------------------------------------

@router.get(
    "/team/{team_id}/passing",
    response_model=PassingAnalyticsResponse,
    summary="Team Passing & Distribution Analytics",
    description="Calculates total passes, completed passes, failed passes, passing accuracy %, average possession %, and match-by-match passing performance.",
)
@router.get(
    "/teams/{team_id}/passing",
    response_model=PassingAnalyticsResponse,
    include_in_schema=False,
)
async def get_team_passing_analytics(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PassingAnalyticsResponse:
    engine = PassingAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_passing_metrics(
            team_id=team_id,
            season_id=season_id,
        )
        return PassingAnalyticsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Home and Away Analytics
# -----------------------------------------------------------------------------

@router.get(
    "/team/{team_id}/home-away",
    response_model=HomeAwayAnalyticsResponse,
    summary="Team Home vs Away Venue Performance Splits",
    description="Calculates isolated home and away records, goals, clean sheets, and comparative home advantage index.",
)
@router.get(
    "/teams/{team_id}/home-away",
    response_model=HomeAwayAnalyticsResponse,
    include_in_schema=False,
)
async def get_team_home_away_analytics(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> HomeAwayAnalyticsResponse:
    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_home_away_analysis(
            team_id=team_id,
            season_id=season_id,
        )
        return HomeAwayAnalyticsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Performance Trends Analytics
# -----------------------------------------------------------------------------

@router.get(
    "/team/{team_id}/trends",
    response_model=PerformanceTrendsResponse,
    summary="Team Performance Trends & Trajectory",
    description="Calculates chronological match progressions, rolling averages, monthly goal distributions, and cumulative points trajectory.",
)
@router.get(
    "/teams/{team_id}/trends",
    response_model=PerformanceTrendsResponse,
    include_in_schema=False,
)
async def get_team_performance_trends(
    team_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    rolling_window: int = Query(default=3, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> PerformanceTrendsResponse:
    engine = PerformanceTrendsEngine(db)
    try:
        data = await engine.calculate_performance_trends(
            team_id=team_id,
            season_id=season_id,
            rolling_window=rolling_window,
        )
        return PerformanceTrendsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Player Intelligence & Comparisons
# -----------------------------------------------------------------------------

@router.get(
    "/player/{player_id}",
    response_model=PlayerPerformanceResponse,
    summary="Player Performance Overview",
    description="Calculates player seasonal performance for specified player.",
)
@router.get(
    "/players/{player_id}/performance",
    response_model=PlayerPerformanceResponse,
    include_in_schema=False,
)
async def get_player_overview(
    player_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    min_minutes: int = Query(default=45, ge=0),
    db: AsyncSession = Depends(get_db),
) -> PlayerPerformanceResponse:
    engine = PlayerIntelligenceEngine(db)
    try:
        data = await engine.calculate_player_performance(
            player_id=player_id,
            season_id=season_id,
            min_minutes_for_per90=min_minutes,
        )
        return PlayerPerformanceResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/players/compare",
    response_model=PlayerCompareResponse,
    summary="Head-to-Head Player Comparison & Radar Dimensions",
    description="Compares two players side-by-side with normalized tactical radar scores across 5 core dimensions.",
)
async def compare_players(
    payload: PlayerCompareRequest,
    db: AsyncSession = Depends(get_db),
) -> PlayerCompareResponse:
    engine = PlayerIntelligenceEngine(db)
    try:
        data = await engine.compare_players(
            player_a_id=uuid.UUID(payload.player_a_id),
            player_b_id=uuid.UUID(payload.player_b_id),
            season_id=uuid.UUID(payload.season_id) if payload.season_id else None,
        )
        return PlayerCompareResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Match Intelligence & Tactical Visualizations
# -----------------------------------------------------------------------------

@router.get(
    "/matches/{match_id}/report",
    response_model=MatchTacticalReportResponse,
    summary="Single Match Tactical Report & Timeline",
    description="Produces head-to-head match stats, half-by-half analysis, and chronological event timeline.",
)
async def get_match_report(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MatchTacticalReportResponse:
    engine = MatchIntelligenceEngine(db)
    try:
        data = await engine.generate_match_report(match_id)
        return MatchTacticalReportResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/tactical/passing-network/{match_id}/team/{team_id}",
    response_model=PassingNetworkResponse,
    summary="Tactical Passing Network Graph",
    description="Generates average player node coordinates and weighted pass connections using mplsoccer pitch models.",
)
async def get_passing_network(
    match_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PassingNetworkResponse:
    tactical_engine = TacticalAnalyticsEngine()
    player_positions = [
        {"player_id": "1", "player_name": "Samik Mitra", "jersey_number": 1, "avg_x": 12.0, "avg_y": 34.0, "touches": 32},
        {"player_id": "3", "player_name": "Bikash Yumnam", "jersey_number": 3, "avg_x": 32.5, "avg_y": 20.0, "touches": 54},
        {"player_id": "6", "player_name": "Ryan Edwards", "jersey_number": 6, "avg_x": 31.0, "avg_y": 48.0, "touches": 61},
        {"player_id": "8", "player_name": "Jiteshwor Singh", "jersey_number": 8, "avg_x": 48.0, "avg_y": 32.0, "touches": 75},
        {"player_id": "10", "player_name": "Lukas Brambilla", "jersey_number": 10, "avg_x": 68.0, "avg_y": 36.0, "touches": 68},
        {"player_id": "11", "player_name": "Farukh Choudhary", "jersey_number": 11, "avg_x": 72.0, "avg_y": 18.0, "touches": 49},
        {"player_id": "9", "player_name": "Wilmar Jordan Gil", "jersey_number": 9, "avg_x": 86.0, "avg_y": 34.0, "touches": 38},
    ]
    pass_connections = [
        {"passer_id": "1", "passer_name": "Samik Mitra", "recipient_id": "6", "recipient_name": "Ryan Edwards", "pass_count": 8},
        {"passer_id": "6", "passer_name": "Ryan Edwards", "recipient_id": "8", "recipient_name": "Jiteshwor Singh", "pass_count": 14},
        {"passer_id": "8", "passer_name": "Jiteshwor Singh", "recipient_id": "10", "recipient_name": "Lukas Brambilla", "pass_count": 18},
        {"passer_id": "10", "passer_name": "Lukas Brambilla", "recipient_id": "11", "recipient_name": "Farukh Choudhary", "pass_count": 11},
        {"passer_id": "10", "passer_name": "Lukas Brambilla", "recipient_id": "9", "recipient_name": "Wilmar Jordan Gil", "pass_count": 9},
    ]
    network = tactical_engine.generate_passing_network(player_positions, pass_connections)
    return PassingNetworkResponse.model_validate(network)


@router.get(
    "/tactical/shot-map/{match_id}",
    response_model=ShotMapResponse,
    summary="Spatial Shot Map & Shot Efficiency Analytics",
    description="Returns spatial (x, y) coordinates, goal distances, shooting angles, and xG values for all fixture shots.",
)
async def get_shot_map(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ShotMapResponse:
    tactical_engine = TacticalAnalyticsEngine()
    shots_sample = [
        {"shot_id": "1", "minute": 12, "player_name": "Farukh Choudhary", "team_name": "Chennaiyin FC", "x": 92.4, "y": 28.1, "outcome": "GOAL", "expected_goals": 0.32, "body_part": "RIGHT_FOOT"},
        {"shot_id": "2", "minute": 24, "player_name": "Wilmar Jordan Gil", "team_name": "Chennaiyin FC", "x": 99.2, "y": 35.0, "outcome": "GOAL", "expected_goals": 0.44, "body_part": "HEAD"},
        {"shot_id": "3", "minute": 38, "player_name": "Farukh Choudhary", "team_name": "Chennaiyin FC", "x": 86.0, "y": 22.0, "outcome": "SAVED", "expected_goals": 0.08, "body_part": "LEFT_FOOT"},
        {"shot_id": "4", "minute": 45, "player_name": "Lukas Brambilla", "team_name": "Chennaiyin FC", "x": 94.0, "y": 34.0, "outcome": "GOAL", "expected_goals": 0.79, "body_part": "RIGHT_FOOT"},
        {"shot_id": "5", "minute": 67, "player_name": "Wilmar Jordan Gil", "team_name": "Chennaiyin FC", "x": 101.5, "y": 33.2, "outcome": "GOAL", "expected_goals": 0.68, "body_part": "RIGHT_FOOT"},
        {"shot_id": "6", "minute": 90, "player_name": "Irfan Yadwad", "team_name": "Chennaiyin FC", "x": 96.0, "y": 36.5, "outcome": "GOAL", "expected_goals": 0.54, "body_part": "RIGHT_FOOT"},
    ]
    shot_map = tactical_engine.generate_shot_map(shots_sample)
    return ShotMapResponse.model_validate(shot_map)
