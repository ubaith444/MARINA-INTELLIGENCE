"""Analytics and Performance Intelligence REST Endpoints."""

import uuid
from typing import Any, Dict, List, Optional
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
    AIAnalystDossierResponse,
    AIAnalystQueryRequest,
    AttackingAnalyticsResponse,
    AverageLineupResponse,
    DefensiveActionsResponse,
    DefensiveAnalyticsResponse,
    DefensiveIntelligenceResponse,
    HeatmapResponse,
    HomeAwayAnalyticsResponse,
    MatchCompareResponse,
    MatchTacticalBreakdownResponse,
    MatchTacticalReportResponse,
    OppositionAnalysisResponse,
    PassingAnalyticsResponse,
    PassingNetworkResponse,
    PerformanceTrendsResponse,
    PlayerListAnalyticsResponse,
    PlayerMatchHistoryResponse,
    PlayerPerformanceResponse,
    ShotMapResponse,
    SquadCoverageAuditResponse,
    SubstituteAnalyticsResponse,
    TeamSeasonPerformanceResponse,
    TerritorialMetricsResponse,
    XgOverviewResponse,
)
from marina.schemas.season_overview import SeasonFormResponse, SeasonOverviewResponse
from marina.services.ai_analyst_service import AIFootballAnalystService, QUESTION_ARCHETYPES
from marina.services.average_lineup_service import AverageLineupService
from marina.services.coverage_audit_service import SquadCoverageAuditService
from marina.services.defensive_service import DefensiveIntelligenceService
from marina.services.season_overview_service import SeasonOverviewService
from marina.services.substitute_service import SubstituteIntelligenceService
from marina.services.tactical_service import TacticalTerritorialService

router = APIRouter(prefix="/analytics", tags=["Football Analytics & Performance Intelligence"])


async def _resolve_team_uuid(
    db: AsyncSession,
    team_id_or_slug: Optional[str | uuid.UUID] = None,
) -> uuid.UUID:
    """Resolves UUID or slug/alias (e.g. 'chennaiyin-fc', 'cfc-1', 'cfc') to a valid Team UUID."""
    if not team_id_or_slug:
        t_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc = (await db.execute(t_stmt)).scalars().first()
        if not cfc:
            cfc = (await db.execute(select(Team).limit(1))).scalars().first()
        if not cfc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No team available.")
        return cfc.id

    if isinstance(team_id_or_slug, uuid.UUID):
        return team_id_or_slug

    try:
        return uuid.UUID(str(team_id_or_slug))
    except (ValueError, TypeError, AttributeError):
        pass

    clean_str = str(team_id_or_slug).strip().lower()

    # Match by slug or short name
    stmt = select(Team).where(
        (Team.slug == clean_str) | (Team.short_name.ilike(clean_str))
    )
    team = (await db.execute(stmt)).scalars().first()
    if team:
        return team.id

    # If cfc-1, cfc, or chennaiyin alias, resolve to Chennaiyin FC
    if "cfc" in clean_str or "chennai" in clean_str:
        t_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc = (await db.execute(t_stmt)).scalars().first()
        if cfc:
            return cfc.id

    # Fallback to first available team
    first_team = (await db.execute(select(Team).limit(1))).scalars().first()
    if first_team:
        return first_team.id

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id_or_slug}' not found.")


async def _resolve_season_uuid(
    db: AsyncSession,
    season_id_or_slug: Optional[str | uuid.UUID] = None,
) -> uuid.UUID:
    """Resolves UUID or slug (e.g. '2026-27') to a valid Season UUID."""
    if not season_id_or_slug:
        s_stmt = select(Season).where(Season.is_current.is_(True))
        cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            cur_s = (await db.execute(select(Season).limit(1))).scalars().first()
        if not cur_s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No season available.")
        return cur_s.id

    if isinstance(season_id_or_slug, uuid.UUID):
        return season_id_or_slug

    try:
        return uuid.UUID(str(season_id_or_slug))
    except (ValueError, TypeError, AttributeError):
        pass

    clean_str = str(season_id_or_slug).strip().lower()
    stmt = select(Season).where(Season.slug == clean_str)
    s = (await db.execute(stmt)).scalars().first()
    if s:
        return s.id

    # Fallback to current season
    cur_s = (await db.execute(select(Season).where(Season.is_current.is_(True)))).scalars().first()
    if cur_s:
        return cur_s.id

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Season '{season_id_or_slug}' not found.")


async def _resolve_team_and_season(
    db: AsyncSession,
    team_id: Optional[str | uuid.UUID] = None,
    season_id: Optional[str | uuid.UUID] = None,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Helper to resolve default team (Chennaiyin FC) and current season."""
    resolved_team_id = await _resolve_team_uuid(db, team_id)
    resolved_season_id = await _resolve_season_uuid(db, season_id)
    return resolved_team_id, resolved_season_id


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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
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
    "/teams/{team_id}/season/{season_id}",
    response_model=TeamSeasonPerformanceResponse,
    summary="Team Seasonal Performance & Form Analytics",
    description="Calculates seasonal win/draw/loss record, home/away splits, goal differences, PPM, and recent form sequence.",
)
async def get_team_season_performance(
    team_id: str,
    season_id: str,
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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> AttackingAnalyticsResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = AttackingAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_attacking_metrics(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> DefensiveAnalyticsResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = DefensiveAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_defensive_metrics(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PassingAnalyticsResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = PassingAnalyticsEngine(db)
    try:
        data = await engine.calculate_team_passing_metrics(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> HomeAwayAnalyticsResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = TeamPerformanceEngine(db)
    try:
        data = await engine.calculate_home_away_analysis(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
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
    team_id: str,
    season_id: Optional[str] = Query(default=None),
    rolling_window: int = Query(default=3, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> PerformanceTrendsResponse:
    resolved_team_id, resolved_season_id = await _resolve_team_and_season(db, team_id, season_id)
    engine = PerformanceTrendsEngine(db)
    try:
        data = await engine.calculate_performance_trends(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            rolling_window=rolling_window,
        )
        return PerformanceTrendsResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Player Intelligence & Comparisons
# -----------------------------------------------------------------------------

@router.get(
    "/players",
    response_model=PlayerListAnalyticsResponse,
    summary="Squad Performance & Per-90 Metrics Table",
    description="Returns performance statistics, true per-90 metrics, and squad rankings for all registered squad members.",
)
async def get_all_players_analytics(
    position: Optional[str] = Query(default=None, description="Position filter: GK, DEFENDER, MIDFIELDER, FORWARD"),
    min_minutes: int = Query(default=0, ge=0, description="Minimum playing minutes threshold"),
    search: Optional[str] = Query(default=None, description="Player name search query"),
    sort_by: str = Query(default="minutes", description="Field to sort by (minutes, goals, assists, name)"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db),
) -> PlayerListAnalyticsResponse:
    engine = PlayerIntelligenceEngine(db)
    data = await engine.get_all_players_performance(
        position=position,
        min_minutes=min_minutes,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return PlayerListAnalyticsResponse.model_validate(data)


@router.get(
    "/players/{player_id}",
    response_model=PlayerPerformanceResponse,
    summary="Player Performance & Rankings",
    description="Calculates comprehensive player performance profile, per-90 metrics, squad rankings, and last-5 appearances.",
)
@router.get(
    "/player/{player_id}",
    response_model=PlayerPerformanceResponse,
    include_in_schema=False,
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


@router.get(
    "/players/{player_id}/matches",
    response_model=PlayerMatchHistoryResponse,
    summary="Player Match-by-Match History",
    description="Returns chronological match performance logs for every fixture played by this player.",
)
async def get_player_matches(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PlayerMatchHistoryResponse:
    engine = PlayerIntelligenceEngine(db)
    try:
        data = await engine.get_player_match_history(player_id)
        return PlayerMatchHistoryResponse.model_validate(data)
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


# -----------------------------------------------------------------------------
# Tactical Intelligence & Territorial Dominance Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "/tactical/territorial",
    response_model=TerritorialMetricsResponse,
    summary="Territorial Dominance & Build-up Metrics",
    description="Returns Field Tilt %, Final Third Passes (CFC vs Opponents), Progressive Passes, and Network Density.",
)
async def get_territorial_metrics(
    match_id: Optional[uuid.UUID] = Query(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> TerritorialMetricsResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_territorial_metrics(match_id=match_id, season_id=season_id)
    return TerritorialMetricsResponse.model_validate(data)


@router.get(
    "/tactical/passing-network",
    response_model=PassingNetworkResponse,
    summary="Tactical Passing Network Graph",
    description="Constructs passing network using real Chennaiyin FC squad players with match, player, and period filtering.",
)
async def get_tactical_passing_network(
    match_id: Optional[uuid.UUID] = Query(default=None),
    player_id: Optional[uuid.UUID] = Query(default=None),
    period: Optional[str] = Query(default="FULL_MATCH", description="Period filter: FULL_MATCH, FIRST_HALF, SECOND_HALF"),
    db: AsyncSession = Depends(get_db),
) -> PassingNetworkResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_passing_network(match_id=match_id, player_id=player_id, period=period)
    return PassingNetworkResponse.model_validate(data)


@router.get(
    "/passing-network/{match_id}",
    response_model=PassingNetworkResponse,
    summary="Tactical Passing Network Graph by Match ID",
    description="Returns passing network with NetworkX graph metrics, degree centralities, and period filters.",
)
async def get_passing_network_by_match_id(
    match_id: uuid.UUID,
    player_id: Optional[uuid.UUID] = Query(default=None),
    period: Optional[str] = Query(default="FULL_MATCH", description="Period filter: FULL_MATCH, FIRST_HALF, SECOND_HALF"),
    db: AsyncSession = Depends(get_db),
) -> PassingNetworkResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_passing_network(match_id=match_id, player_id=player_id, period=period)
    return PassingNetworkResponse.model_validate(data)


@router.get(
    "/tactical/passing-network/{match_id}/team/{team_id}",
    response_model=PassingNetworkResponse,
    summary="Tactical Passing Network Graph (Match & Team)",
    description="Returns passing network for a specific match and team.",
)
async def get_passing_network_by_match(
    match_id: uuid.UUID,
    team_id: uuid.UUID,
    player_id: Optional[uuid.UUID] = Query(default=None),
    period: Optional[str] = Query(default="FULL_MATCH"),
    db: AsyncSession = Depends(get_db),
) -> PassingNetworkResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_passing_network(match_id=match_id, player_id=player_id, period=period)
    return PassingNetworkResponse.model_validate(data)


@router.get(
    "/shots",
    response_model=ShotMapResponse,
    summary="Shot Map & Event Analytics",
    description="Returns verified spatial coordinates, goal distances, shooting angles, and outcomes for Chennaiyin FC shots.",
)
@router.get(
    "/tactical/shot-map",
    response_model=ShotMapResponse,
    summary="Spatial Shot Map & Shot Efficiency Analytics",
    description="Returns verified spatial coordinates, goal distances, shooting angles, and outcomes for Chennaiyin FC shots.",
)
async def get_tactical_shot_map(
    match_id: Optional[uuid.UUID] = Query(default=None),
    player_id: Optional[uuid.UUID] = Query(default=None),
    outcome: Optional[str] = Query(default=None, description="Outcome filter: GOAL, SAVED, BLOCKED, MISSED"),
    db: AsyncSession = Depends(get_db),
) -> ShotMapResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_shot_map(match_id=match_id, player_id=player_id)
    if outcome and outcome.upper() != "ALL":
        data["shots"] = [s for s in data["shots"] if s["outcome"].upper() == outcome.upper()]
        data["total_shots"] = len(data["shots"])
        data["goals"] = sum(1 for s in data["shots"] if s["outcome"] == "GOAL")
    return ShotMapResponse.model_validate(data)


@router.get(
    "/xg",
    response_model=XgOverviewResponse,
    summary="Expected Goals (xG) Analytics & Team Aggregates",
    description="Returns actual goals vs expected goals overperformance, conversion rates, player xG breakdown, and match-by-match xG.",
)
async def get_xg_analytics(
    season_id: Optional[uuid.UUID] = Query(default=None),
    match_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> XgOverviewResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_xg_overview(season_id=season_id, match_id=match_id)
    return XgOverviewResponse.model_validate(data)


@router.get(
    "/opposition/{opponent_id}",
    response_model=OppositionAnalysisResponse,
    summary="Opposition Analysis & Tactical Intelligence",
    description="Returns historical H2H records, completed matches, upcoming fixtures, and tactical profiles for ISL 2026-27 opponents.",
)
async def get_opposition_profile(
    opponent_id: str,
    db: AsyncSession = Depends(get_db),
) -> OppositionAnalysisResponse:
    service = TacticalTerritorialService(db)
    try:
        data = await service.get_opposition_analysis(opponent_id_or_slug=opponent_id)
        return OppositionAnalysisResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/matches/compare",
    response_model=MatchCompareResponse,
    summary="Match-to-Match Statistical Comparison",
    description="Compares two fixtures side-by-side with statistical deltas across possession, shooting, passing, and defending.",
)
async def compare_matches_endpoint(
    match_a_id: uuid.UUID = Query(..., description="First match UUID"),
    match_b_id: uuid.UUID = Query(..., description="Second match UUID"),
    db: AsyncSession = Depends(get_db),
) -> MatchCompareResponse:
    service = TacticalTerritorialService(db)
    try:
        data = await service.compare_matches(match_a_id=match_a_id, match_b_id=match_b_id)
        return MatchCompareResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/tactical/shot-map/{match_id}",
    response_model=ShotMapResponse,
    summary="Spatial Shot Map (Single Match)",
    description="Returns spatial shot coordinates and efficiency metrics for a specific match.",
)
async def get_shot_map_by_match(
    match_id: uuid.UUID,
    player_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ShotMapResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_shot_map(match_id=match_id, player_id=player_id)
    return ShotMapResponse.model_validate(data)


@router.get(
    "/tactical/defensive-actions",
    response_model=DefensiveActionsResponse,
    summary="Spatial Defensive Actions (Tackles, Interceptions, Clearances, Blocks, Recoveries)",
    description="Returns verified pitch defensive action events filtered by match and player.",
)
async def get_defensive_actions(
    match_id: Optional[uuid.UUID] = Query(default=None),
    player_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> DefensiveActionsResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_defensive_actions(match_id=match_id, player_id=player_id)
    return DefensiveActionsResponse.model_validate(data)


@router.get(
    "/tactical/heatmap",
    response_model=HeatmapResponse,
    summary="Player Activity Heatmap & Telemetry Availability",
    description="Enforces zero-fabrication standards and provides transparent tracking availability status.",
)
async def get_heatmap(
    match_id: Optional[uuid.UUID] = Query(default=None),
    player_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> HeatmapResponse:
    service = TacticalTerritorialService(db)
    data = await service.get_heatmap(match_id=match_id, player_id=player_id)
    return HeatmapResponse.model_validate(data)


@router.get(
    "/tactical/{match_id}",
    response_model=MatchTacticalBreakdownResponse,
    summary="Match Tactical & Territorial Breakdown",
    description="Comprehensive match tactical breakdown including formation, field tilt, passing network, and shot efficiency.",
)
async def get_match_tactical_breakdown(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MatchTacticalBreakdownResponse:
    service = TacticalTerritorialService(db)
    try:
        data = await service.get_tactical_match_breakdown(match_id=match_id)
        return MatchTacticalBreakdownResponse.model_validate(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/season",
    response_model=SeasonOverviewResponse,
    summary="Get Dynamic Season KPIs",
    description="Returns aggregate season KPIs (Played, Remaining, W, D, L, Points, GF, GA, GD, Win %, Clean Sheets).",
)
async def get_season_overview_analytics(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SeasonOverviewResponse:
    service = SeasonOverviewService(db)
    return await service.get_overview(season_id=season_id, team_id=team_id)


@router.get(
    "/form",
    response_model=SeasonFormResponse,
    summary="Get Recent Season Form",
    description="Returns chronological form of the last 5 completed matches with opponents, scores, and outcomes.",
)
async def get_season_form_analytics(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SeasonFormResponse:
    service = SeasonOverviewService(db)
    return await service.get_form(season_id=season_id, team_id=team_id)


# =========================================================================
# V3 Platform Reorganisation & Advanced Intelligence Endpoints
# =========================================================================

@router.get(
    "/average-lineup",
    response_model=AverageLineupResponse,
    summary="Get Global Average Starting XI and Formation",
    description="Returns the empirical modal formation (4-2-3-1) and most frequent 11 starters with pitch coordinates across completed matches.",
)
async def get_average_lineup_endpoint(
    team_id: Optional[str] = Query(default=None),
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> AverageLineupResponse:
    t_uuid = await _resolve_team_uuid(db, team_id) if team_id else None
    s_uuid = await _resolve_season_uuid(db, season_id) if season_id else None
    service = AverageLineupService(db)
    return await service.get_average_lineup(team_id=t_uuid, season_id=s_uuid)


@router.get(
    "/substitutes",
    response_model=SubstituteAnalyticsResponse,
    summary="Get Substitute Analytics and Impact Analysis",
    description="Returns comprehensive substitute player statistics, starter vs sub comparisons, and match-by-match substitution impact.",
)
async def get_substitute_analytics_endpoint(
    team_id: Optional[str] = Query(default=None),
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SubstituteAnalyticsResponse:
    t_uuid = await _resolve_team_uuid(db, team_id) if team_id else None
    s_uuid = await _resolve_season_uuid(db, season_id) if season_id else None
    service = SubstituteIntelligenceService(db)
    return await service.get_substitute_analytics(team_id=t_uuid, season_id=s_uuid)


@router.get(
    "/defensive-intelligence",
    response_model=DefensiveIntelligenceResponse,
    summary="Get Unified Defensive Intelligence and Player Leaderboard",
    description="Returns team defensive resilience metrics, player defensive leaderboard with per-90 rates, and verified spatial defensive events.",
)
async def get_defensive_intelligence_endpoint(
    team_id: Optional[str] = Query(default=None),
    season_id: Optional[str] = Query(default=None),
    match_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> DefensiveIntelligenceResponse:
    t_uuid = await _resolve_team_uuid(db, team_id) if team_id else None
    s_uuid = await _resolve_season_uuid(db, season_id) if season_id else None
    service = DefensiveIntelligenceService(db)
    return await service.get_defensive_intelligence(team_id=t_uuid, season_id=s_uuid, match_id=match_id)


@router.get(
    "/coverage-audit",
    response_model=SquadCoverageAuditResponse,
    summary="Get Full Squad Data Completeness and Coverage Audit",
    description="Audits all 45 uploaded Chennaiyin FC squad players, separating confirmed zeroes from missing provider telemetry.",
)
async def get_squad_coverage_audit_endpoint(
    team_id: Optional[str] = Query(default=None),
    season_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SquadCoverageAuditResponse:
    t_uuid = await _resolve_team_uuid(db, team_id) if team_id else None
    s_uuid = await _resolve_season_uuid(db, season_id) if season_id else None
    service = SquadCoverageAuditService(db)
    return await service.get_coverage_audit(team_id=t_uuid, season_id=s_uuid)


@router.get(
    "/ai-analyst/archetypes",
    summary="Get Supported AI Football Analyst Query Archetypes",
    description="Returns the 12 natural language question archetypes supported by the deterministic analytical pipeline.",
)
async def get_ai_analyst_archetypes() -> List[Dict[str, Any]]:
    return QUESTION_ARCHETYPES


@router.post(
    "/ai-analyst/ask",
    response_model=AIAnalystDossierResponse,
    summary="Ask AI Football Analyst",
    description="Processes natural language football inquiries through deterministic DB retrieval and metric pipelines without hallucinations.",
)
async def ask_ai_analyst_endpoint(
    payload: AIAnalystQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> AIAnalystDossierResponse:
    service = AIFootballAnalystService(db)
    return await service.answer_query(payload.query)


