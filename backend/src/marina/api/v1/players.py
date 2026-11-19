"""Players and Squad Registrations REST Endpoints."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.db.session import get_db
from marina.models.common import MatchStatus, PlayerPosition
from marina.models.match import Lineup, Match
from marina.models.player import Player, SquadRegistration, TeamSquadMembership
from marina.models.statistics import PlayerMatchStatistic
from marina.models.team import Team
from marina.schemas.player import (
    PlayerCreate,
    PlayerDetailRead,
    PlayerRead,
    PlayerUpdate,
    SquadRegistrationCreate,
    SquadRegistrationRead,
)
from marina.services.leadership_service import LeadershipService
from marina.services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["Players & Squads"])


@router.get("", response_model=List[PlayerRead], summary="List Players")
async def list_players(
    position: Optional[str] = Query(default=None, description="Filter by position (e.g. GK, CB, CM, CF)"),
    nationality: Optional[str] = Query(default=None, description="Filter by nationality (e.g. India)"),
    is_indian: Optional[bool] = Query(default=None, description="Filter Indian domestic players"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    search: Optional[str] = Query(default=None, description="Search by player name"),
    season_id: Optional[uuid.UUID] = Query(default=None, description="Filter players registered in season"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[PlayerRead]:
    stmt = select(Player)

    if season_id:
        stmt = stmt.join(TeamSquadMembership).where(TeamSquadMembership.season_id == season_id)

    if is_active is not None:
        stmt = stmt.where(Player.is_active == is_active)

    if is_indian is True:
        stmt = stmt.where(Player.nationality == "India")
    elif is_indian is False:
        stmt = stmt.where(Player.nationality != "India")

    if nationality:
        if nationality.upper() == "DOMESTIC":
            stmt = stmt.where(Player.nationality == "India")
        elif nationality.upper() == "OVERSEAS":
            stmt = stmt.where(Player.nationality != "India")
        else:
            stmt = stmt.where(Player.nationality.ilike(f"%{nationality}%"))

    if position and position.upper() != "ALL":
        try:
            pos_enum = PlayerPosition(position.upper())
            stmt = stmt.where(Player.primary_position == pos_enum)
        except ValueError:
            stmt = stmt.where(Player.primary_position.cast(String).ilike(f"%{position}%"))

    if search:
        search_filter = or_(
            Player.first_name.ilike(f"%{search}%"),
            Player.last_name.ilike(f"%{search}%"),
            Player.known_name.ilike(f"%{search}%"),
            Player.slug.ilike(f"%{search}%"),
        )
        stmt = stmt.where(search_filter)

    stmt = stmt.order_by(Player.squad_number.asc().nullslast(), Player.last_name.asc())
    stmt = stmt.offset(offset).limit(limit)

    players = list((await db.execute(stmt)).scalars().all())
    lead_service = LeadershipService(db)
    result = []
    for p in players:
        p_read = PlayerRead.model_validate(p)
        is_lead, role = await lead_service.get_player_leadership_info(p.id)
        p_read.is_leadership_group = is_lead
        p_read.leadership_role = role
        result.append(p_read)
    return result


@router.get("/statistics", summary="Get Verified Player Performance Statistics")
async def get_player_season_statistics(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    position: Optional[str] = Query(default=None, description="Position filter (ALL, GK, DEF, MID, FWD)"),
    is_indian: Optional[bool] = Query(default=None, description="Filter Indian domestic players"),
    search: Optional[str] = Query(default=None, description="Player name search"),
    sort_by: Optional[str] = Query(default=None, description="Sort field (minutes, goals, assists, appearances, jersey)"),
    order: Optional[str] = Query(default="desc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db),
):
    """Returns verified player performance metrics for the season strictly from match records."""
    from marina.services.season_overview_service import SeasonOverviewService
    service = SeasonOverviewService(db)
    items = await service.get_player_statistics(season_id=season_id, team_id=team_id)

    # Apply Indian player filter
    if is_indian is True:
        items = [it for it in items if it.is_indian or it.nationality == "India" or "India" in (it.nationality or "")]
    elif is_indian is False:
        items = [it for it in items if not it.is_indian and it.nationality != "India" and "India" not in (it.nationality or "")]

    # Apply search filter
    if search:
        s_lower = search.strip().lower()
        items = [it for it in items if s_lower in it.name.lower()]

    # Apply position filter
    if position and position.upper() != "ALL":
        pos_u = position.strip().upper()
        if pos_u == "GK":
            items = [it for it in items if "GOALKEEPER" in it.position.upper() or it.position.upper() == "GK"]
        elif pos_u == "DEF":
            items = [it for it in items if any(k in it.position.upper() for k in ["BACK", "DEFENDER", "CB", "LB", "RB"])]
        elif pos_u == "MID":
            items = [it for it in items if any(k in it.position.upper() for k in ["MIDFIELD", "CM", "DM", "AM", "LM", "RM"])]
        elif pos_u == "FWD":
            items = [it for it in items if any(k in it.position.upper() for k in ["FORWARD", "WING", "STRIKER", "CF", "LW", "RW"])]

    # Apply sorting
    if sort_by:
        reverse = order.lower() == "desc"
        if sort_by == "minutes":
            items.sort(key=lambda x: (x.minutes_played, x.appearances), reverse=reverse)
        elif sort_by == "goals":
            items.sort(key=lambda x: (x.goals, x.assists, x.minutes_played), reverse=reverse)
        elif sort_by == "assists":
            items.sort(key=lambda x: (x.assists, x.goals, x.minutes_played), reverse=reverse)
        elif sort_by == "appearances":
            items.sort(key=lambda x: (x.appearances, x.starts, x.minutes_played), reverse=reverse)
        elif sort_by == "jersey":
            items.sort(key=lambda x: x.jersey_number or 999, reverse=reverse)

    return items


@router.get("/top-scorers", summary="Get Season Top Goal Scorers")
async def get_season_top_scorers(
    season_id: Optional[uuid.UUID] = Query(default=None, description="Season UUID filter"),
    team_id: Optional[uuid.UUID] = Query(default=None, description="Team UUID filter"),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Returns verified top goal scorers for the season. Empty list if 0 goals recorded."""
    from marina.services.season_overview_service import SeasonOverviewService
    service = SeasonOverviewService(db)
    return await service.get_top_scorers(season_id=season_id, team_id=team_id, limit=limit)


@router.get("/{player_id}", response_model=PlayerDetailRead, summary="Get Player Profile and Career Record")
async def get_player_by_id(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PlayerDetailRead:
    stmt = select(Player).where(Player.id == player_id)
    player = (await db.execute(stmt)).scalars().first()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player {player_id} not found.")

    # Fetch career memberships
    mem_stmt = (
        select(TeamSquadMembership)
        .where(TeamSquadMembership.player_id == player_id)
        .options(selectinload(TeamSquadMembership.season), selectinload(TeamSquadMembership.team))
        .order_by(TeamSquadMembership.created_at.desc())
    )
    memberships = list((await db.execute(mem_stmt)).scalars().all())
    career = [
        {
            "membership_id": str(m.id),
            "season_name": m.season.name if m.season else "Unknown",
            "team_name": m.team.name if m.team else "Unknown",
            "squad_number": m.squad_number,
            "position": m.position,
            "contract_expiry": m.contract_expiry.isoformat() if m.contract_expiry else None,
            "is_active": m.is_active,
        }
        for m in memberships
    ]

    # Fetch historical stats summary
    stat_stmt = select(
        func.count(PlayerMatchStatistic.id).label("matches_count"),
        func.coalesce(func.sum(PlayerMatchStatistic.minutes_played), 0).label("minutes"),
        func.coalesce(func.sum(PlayerMatchStatistic.goals), 0).label("goals"),
        func.coalesce(func.sum(PlayerMatchStatistic.assists), 0).label("assists"),
        func.coalesce(func.sum(PlayerMatchStatistic.yellow_cards), 0).label("yellows"),
        func.coalesce(func.sum(PlayerMatchStatistic.red_cards), 0).label("reds"),
    ).where(PlayerMatchStatistic.player_id == player_id)

    row = (await db.execute(stat_stmt)).first()
    stats_summary = {
        "appearances": row.matches_count if row else 0,
        "minutes_played": row.minutes if row else 0,
        "goals": row.goals if row else 0,
        "assists": row.assists if row else 0,
        "yellow_cards": row.yellows if row else 0,
        "red_cards": row.reds if row else 0,
    }

    data = PlayerRead.model_validate(player).model_dump()
    data["career_memberships"] = career
    data["historical_statistics"] = stats_summary

    # Leadership Group membership check
    lead_service = LeadershipService(db)
    is_leadership, leadership_role = await lead_service.get_player_leadership_info(player_id)
    data["is_leadership_group"] = is_leadership
    data["leadership_role"] = leadership_role

    return PlayerDetailRead.model_validate(data)


@router.patch("/{player_id}", response_model=PlayerRead, summary="Update Player Profile")
async def update_player(
    player_id: uuid.UUID,
    payload: PlayerUpdate,
    db: AsyncSession = Depends(get_db),
) -> PlayerRead:
    stmt = select(Player).where(Player.id == player_id)
    player = (await db.execute(stmt)).scalars().first()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player {player_id} not found.")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(player, field, val)

    player.verified_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(player)
    return PlayerRead.model_validate(player)


@router.get("/{player_id}/matches", summary="Get Match-by-Match Player Performance")
async def get_player_matches(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Returns verified match-by-match performance for this specific player."""
    player = (await db.execute(select(Player).where(Player.id == player_id))).scalars().first()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player {player_id} not found.")

    stmt = (
        select(Match, Lineup, PlayerMatchStatistic)
        .join(Lineup, (Lineup.match_id == Match.id) & (Lineup.player_id == player_id), isouter=True)
        .join(
            PlayerMatchStatistic,
            (PlayerMatchStatistic.match_id == Match.id) & (PlayerMatchStatistic.player_id == player_id),
            isouter=True,
        )
        .options(selectinload(Match.home_team), selectinload(Match.away_team))
        .where(
            or_(
                Lineup.id.isnot(None),
                PlayerMatchStatistic.id.isnot(None),
            )
        )
        .order_by(Match.match_number.asc())
    )
    rows = (await db.execute(stmt)).all()

    cfc_id = (await db.execute(select(Team.id).where(Team.short_name == "CFC"))).scalars().first()

    matches_data = []
    for match, lineup, stat in rows:
        is_home = match.home_team_id == cfc_id
        opponent = match.away_team if is_home else match.home_team
        cfc_score = match.home_score if is_home else match.away_score
        opp_score = match.away_score if is_home else match.home_score

        result = None
        if match.match_status == MatchStatus.FINISHED and cfc_score is not None and opp_score is not None:
            if cfc_score > opp_score:
                result = "W"
            elif cfc_score == opp_score:
                result = "D"
            else:
                result = "L"

        matches_data.append({
            "match_id": str(match.id),
            "match_number": match.match_number,
            "match_date": match.scheduled_kickoff.isoformat() if match.scheduled_kickoff else None,
            "match_status": match.match_status.value if hasattr(match.match_status, "value") else str(match.match_status),
            "opponent_name": opponent.name if opponent else "Unknown",
            "opponent_short_name": opponent.short_name if opponent else "OPP",
            "is_home": is_home,
            "cfc_score": cfc_score,
            "opponent_score": opp_score,
            "result": result,
            "lineup_role": "SUBSTITUTE" if (lineup and lineup.is_substitute_in) else (lineup.lineup_role.value if (lineup and hasattr(lineup.lineup_role, "value")) else ("STARTER" if lineup else None)),
            "position": str(lineup.position.value) if (lineup and lineup.position and hasattr(lineup.position, "value")) else (str(player.primary_position.value) if hasattr(player.primary_position, "value") else str(player.primary_position)),
            "jersey_number": lineup.jersey_number if lineup else player.squad_number,
            "is_captain": lineup.is_captain if lineup else False,
            "minutes_played": (stat.minutes_played if stat and stat.minutes_played is not None else (lineup.minutes_played if lineup else None)),
            "goals": stat.goals if stat and stat.goals is not None else 0,
            "assists": stat.assists if stat and stat.assists is not None else 0,
            "yellow_cards": stat.yellow_cards if stat and stat.yellow_cards is not None else 0,
            "red_cards": stat.red_cards if stat and stat.red_cards is not None else 0,
            "shots_total": stat.shots_total if stat else None,
            "shots_on_target": stat.shots_on_target if stat else None,
            "passes_total": stat.passes_total if stat else None,
            "passes_completed": stat.passes_completed if stat else None,
            "tackles_won": stat.tackles_won if stat else None,
            "saves": stat.saves if stat else None,
            "goals_conceded": stat.goals_conceded if stat else None,
            "clean_sheet": stat.clean_sheet if stat else None,
        })

    return matches_data


@router.get("/{player_id}/performance", summary="Get Granular Player Intelligence Performance")
async def get_player_performance(
    player_id: uuid.UUID,
    season_id: Optional[uuid.UUID] = Query(default=None),
    min_minutes: int = Query(default=45, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Returns standardized player performance, per-90 metrics, and tactical ratings."""
    from marina.analytics.player_intelligence import PlayerIntelligenceEngine
    engine = PlayerIntelligenceEngine(db)
    try:
        return await engine.calculate_player_performance(
            player_id=player_id,
            season_id=season_id,
            min_minutes_for_per90=min_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
