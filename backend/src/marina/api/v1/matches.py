"""Matches REST Endpoints."""

import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.match_intelligence import MatchIntelligenceEngine
from marina.core.exceptions import (
    EntityNotFoundError,
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.db.session import get_db
from marina.models.common import MatchStatus
from marina.models.match import Lineup, MatchEvent, MatchLineup, MatchPass, MatchShot, MatchSubstitute
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.schemas.match import (
    LineupRead,
    MatchCreate,
    MatchDetailRead,
    MatchEventRead,
    MatchLineupRead,
    MatchPlayersResponse,
    MatchRead,
    MatchSubstituteRead,
    PlayerMatchDetailItem,
)
from marina.schemas.statistics import PlayerMatchStatisticRead, TeamMatchStatisticRead
from marina.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches & Fixtures"])


@router.get("", response_model=List[MatchRead], summary="List Fixtures & Matches")
async def list_matches(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[str] = Query(default=None, description="Match status (SCHEDULED, FINISHED, COMPLETED, etc.)"),
    is_home: Optional[bool] = Query(default=None, description="Filter by home matches (true) or away (false)"),
    matchweek: Optional[int] = Query(default=None, description="Filter by matchweek number"),
    start_date: Optional[date] = Query(default=None, description="Filter kickoff on or after date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="Filter kickoff on or before date (YYYY-MM-DD)"),
    search: Optional[str] = Query(default=None, description="Search opponent name or venue"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    match_status: Optional[MatchStatus] = None
    if status:
        status_clean = status.strip().upper()
        if status_clean in ("COMPLETED", "FINISHED"):
            match_status = MatchStatus.FINISHED
        else:
            try:
                match_status = MatchStatus(status_clean)
            except ValueError:
                match_status = None

    service = MatchService(db)
    matches = await service.list_matches(
        season_id=season_id,
        team_id=team_id,
        status=match_status,
        is_home=is_home,
        matchweek=matchweek,
        start_date=start_date,
        end_date=end_date,
        search=search,
        offset=offset,
        limit=limit,
    )
    return [MatchRead.model_validate(m) for m in matches]


@router.get("/upcoming", response_model=List[MatchRead], summary="List Upcoming Scheduled Fixtures")
async def list_upcoming_matches(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    is_home: Optional[bool] = Query(default=None),
    matchweek: Optional[int] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    """Returns scheduled upcoming fixtures where scores remain strictly NULL."""
    service = MatchService(db)
    matches = await service.list_matches(
        season_id=season_id,
        team_id=team_id,
        status=MatchStatus.SCHEDULED,
        is_home=is_home,
        matchweek=matchweek,
        offset=offset,
        limit=limit,
    )
    return [MatchRead.model_validate(m) for m in matches]


@router.get("/completed", response_model=List[MatchRead], summary="List Completed Matches")
async def list_completed_matches(
    season_id: Optional[uuid.UUID] = Query(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    is_home: Optional[bool] = Query(default=None),
    matchweek: Optional[int] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    """Returns completed/finished match records with verified scores."""
    service = MatchService(db)
    matches = await service.list_matches(
        season_id=season_id,
        team_id=team_id,
        status=MatchStatus.FINISHED,
        is_home=is_home,
        matchweek=matchweek,
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


@router.get("/{match_id}/players", response_model=MatchPlayersResponse, summary="Get Match Lineups & Individual Player Statistics")
async def get_match_players(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MatchPlayersResponse:
    """Returns verified Starting XI, substitutes, and granular player match statistics."""
    service = MatchService(db)
    try:
        match = await service.get_match_detail(match_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # Fetch starting XI (MatchLineup)
    starters_stmt = (
        select(MatchLineup)
        .where(MatchLineup.match_id == match_id)
        .options(selectinload(MatchLineup.player))
        .order_by(MatchLineup.jersey_number.asc())
    )
    starters = (await db.execute(starters_stmt)).scalars().all()

    # Fetch substitutes (MatchSubstitute)
    subs_stmt = (
        select(MatchSubstitute)
        .where(MatchSubstitute.match_id == match_id)
        .options(
            selectinload(MatchSubstitute.player),
            selectinload(MatchSubstitute.replaced_player),
        )
        .order_by(MatchSubstitute.sub_in_minute.asc())
    )
    subs = (await db.execute(subs_stmt)).scalars().all()

    # Fetch player match stats
    stats_stmt = (
        select(PlayerMatchStatistic)
        .where(PlayerMatchStatistic.match_id == match_id)
        .options(selectinload(PlayerMatchStatistic.player), selectinload(PlayerMatchStatistic.data_source))
    )
    stats_rows = (await db.execute(stats_stmt)).scalars().all()
    stats_by_player = {s.player_id: s for s in stats_rows}

    formation = starters[0].tactical_formation if starters and starters[0].tactical_formation else None
    data_source_str = (
        match.source_url
        or (stats_rows[0].data_source.name if stats_rows and stats_rows[0].data_source else "Official ISL Match Centre")
    )

    def build_player_item(
        player_id: uuid.UUID,
        name: str,
        jersey_number: Optional[int],
        position: Optional[str],
        lineup_role: str,
        is_captain: bool = False,
        minutes_played: Optional[int] = None,
        sub_in_minute: Optional[int] = None,
        sub_out_minute: Optional[int] = None,
        replaced_player_id: Optional[uuid.UUID] = None,
        replaced_player_name: Optional[str] = None,
        tactical_formation: Optional[str] = None,
        verification_status: str = "VERIFIED",
        is_verified: bool = True,
    ) -> PlayerMatchDetailItem:
        p_stat = stats_by_player.get(player_id)
        return PlayerMatchDetailItem(
            player_id=player_id,
            name=name,
            jersey_number=jersey_number,
            position=position,
            lineup_role=lineup_role,
            is_captain=is_captain,
            minutes_played=minutes_played if minutes_played is not None else (p_stat.minutes_played if p_stat else None),
            sub_in_minute=sub_in_minute,
            sub_out_minute=sub_out_minute,
            replaced_player_id=replaced_player_id,
            replaced_player_name=replaced_player_name,
            tactical_formation=tactical_formation,
            goals=p_stat.goals if p_stat else None,
            assists=p_stat.assists if p_stat else None,
            shots_total=p_stat.shots_total if p_stat else None,
            shots_on_target=p_stat.shots_on_target if p_stat else None,
            passes_total=p_stat.passes_total if p_stat else None,
            passes_completed=p_stat.passes_completed if p_stat else None,
            pass_accuracy_pct=p_stat.pass_accuracy_pct if p_stat else None,
            tackles_won=p_stat.tackles_won if p_stat else None,
            interceptions=p_stat.interceptions if p_stat else None,
            clearances=p_stat.clearances if p_stat else None,
            blocks=p_stat.blocks if p_stat else None,
            saves=p_stat.saves if p_stat else None,
            clean_sheet=p_stat.clean_sheet if p_stat else None,
            yellow_cards=p_stat.yellow_cards if p_stat else None,
            red_cards=p_stat.red_cards if p_stat else None,
            verification_status=verification_status,
            is_verified=is_verified,
        )

    starting_xi_items = [
        build_player_item(
            player_id=s.player_id,
            name=(s.player.known_name or f"{s.player.first_name} {s.player.last_name}") if s.player else "Unknown Player",
            jersey_number=s.jersey_number,
            position=s.position.value if s.position else None,
            lineup_role="STARTER",
            is_captain=s.is_captain,
            minutes_played=s.minutes_played,
            sub_out_minute=s.sub_out_minute,
            tactical_formation=s.tactical_formation,
            verification_status=s.verification_status.value if hasattr(s.verification_status, "value") else str(s.verification_status),
            is_verified=s.is_verified,
        )
        for s in starters
    ]

    substitutes_items = []
    bench_unused_items = []
    for sub in subs:
        p_name = (sub.player.known_name or f"{sub.player.first_name} {sub.player.last_name}") if sub.player else "Unknown Player"
        rep_name = (sub.replaced_player.known_name or f"{sub.replaced_player.first_name} {sub.replaced_player.last_name}") if sub.replaced_player else None
        item = build_player_item(
            player_id=sub.player_id,
            name=p_name,
            jersey_number=sub.jersey_number,
            position=sub.position.value if sub.position else None,
            lineup_role="SUBSTITUTE",
            is_captain=False,
            minutes_played=sub.minutes_played,
            sub_in_minute=sub.sub_in_minute,
            sub_out_minute=sub.sub_out_minute,
            replaced_player_id=sub.replaced_player_id,
            replaced_player_name=rep_name,
            verification_status=sub.verification_status.value if hasattr(sub.verification_status, "value") else str(sub.verification_status),
            is_verified=sub.is_verified,
        )
        if sub.is_used:
            substitutes_items.append(item)
        else:
            bench_unused_items.append(item)

    return MatchPlayersResponse(
        match_id=match_id,
        formation=formation,
        starting_xi=starting_xi_items,
        substitutes=substitutes_items,
        bench_unused=bench_unused_items,
        data_source=data_source_str,
    )


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


@router.get("/{match_id}/report", summary="Get Match-by-Match Report and Tactical Breakdown")
async def get_match_report_endpoint(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    engine = MatchIntelligenceEngine(db)
    try:
        return await engine.generate_match_report(match_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{match_id}/statistics", summary="Get Match Team and Player Statistics")
async def get_match_statistics(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    team_stats = (
        await db.execute(
            select(TeamMatchStatistic)
            .where(TeamMatchStatistic.match_id == match_id)
            .options(selectinload(TeamMatchStatistic.team), selectinload(TeamMatchStatistic.data_source))
        )
    ).scalars().all()

    player_stats = (
        await db.execute(
            select(PlayerMatchStatistic)
            .where(PlayerMatchStatistic.match_id == match_id)
            .options(selectinload(PlayerMatchStatistic.player), selectinload(PlayerMatchStatistic.team))
        )
    ).scalars().all()

    return {
        "match_id": str(match_id),
        "team_statistics": [TeamMatchStatisticRead.model_validate(ts) for ts in team_stats],
        "player_statistics": [PlayerMatchStatisticRead.model_validate(ps) for ps in player_stats],
    }


@router.get("/{match_id}/events", response_model=List[MatchEventRead], summary="Get Chronological Match Events")
async def get_match_events(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[MatchEventRead]:
    stmt = (
        select(MatchEvent)
        .where(MatchEvent.match_id == match_id)
        .options(
            selectinload(MatchEvent.primary_player),
            selectinload(MatchEvent.secondary_player),
        )
        .order_by(MatchEvent.minute.asc(), MatchEvent.stoppage_minute.asc())
    )
    events = (await db.execute(stmt)).scalars().all()
    return [MatchEventRead.model_validate(e) for e in events]


@router.get("/{match_id}/lineups", response_model=List[LineupRead], summary="Get Match Lineups")
async def get_match_lineups(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[LineupRead]:
    stmt = (
        select(Lineup)
        .where(Lineup.match_id == match_id)
        .options(selectinload(Lineup.player))
        .order_by(Lineup.jersey_number.asc())
    )
    lineups = (await db.execute(stmt)).scalars().all()
    return [LineupRead.model_validate(l) for l in lineups]


@router.get("/{match_id}/shots", summary="Get Match Shot Events")
async def get_match_shots(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    stmt = (
        select(MatchShot)
        .where(MatchShot.match_id == match_id)
        .order_by(MatchShot.minute.asc())
    )
    shots = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(s.id),
            "match_id": str(s.match_id),
            "team_id": str(s.team_id),
            "player_id": str(s.player_id) if s.player_id else None,
            "minute": s.minute,
            "period": s.period.value,
            "outcome": s.outcome,
            "shot_type": s.shot_type,
            "is_inside_box": s.is_inside_box,
            "x_coord": s.x_coord,
            "y_coord": s.y_coord,
            "expected_goals": s.expected_goals,
        }
        for s in shots
    ]


@router.post("/lineups/import", summary="Import Verified Historical Lineups & Substitutions")
async def import_historical_lineups(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Imports verified starting lineups, tactical formations, and actual substitutions for the 5 completed matches."""
    from marina.services.lineup_import_service import LineupImportService

    service = LineupImportService(db)
    try:
        return await service.import_historical_lineups()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lineup import failed: {str(e)}",
        )


@router.get("/{match_id}/starting-xi", response_model=List[MatchLineupRead], summary="Get Match Starting XI")
async def get_match_starting_xi(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[MatchLineupRead]:
    """Returns the verified 11 starting players and tactical formation."""
    stmt = (
        select(MatchLineup)
        .where(MatchLineup.match_id == match_id)
        .options(selectinload(MatchLineup.player))
        .order_by(MatchLineup.jersey_number.asc())
    )
    starters = (await db.execute(stmt)).scalars().all()
    return [MatchLineupRead.model_validate(s) for s in starters]


@router.get("/{match_id}/substitutes", response_model=List[MatchSubstituteRead], summary="Get Match Substitutes")
async def get_match_substitutes(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[MatchSubstituteRead]:
    """Returns verified matchday substitutes and actual substitutions made."""
    stmt = (
        select(MatchSubstitute)
        .where(MatchSubstitute.match_id == match_id)
        .options(
            selectinload(MatchSubstitute.player),
            selectinload(MatchSubstitute.replaced_player),
        )
        .order_by(MatchSubstitute.sub_in_minute.asc())
    )
    subs = (await db.execute(stmt)).scalars().all()
    return [MatchSubstituteRead.model_validate(s) for s in subs]


