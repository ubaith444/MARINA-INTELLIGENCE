"""Squad Import, Synchronization, and Active Roster REST Endpoints."""

import os
import uuid
from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.db.session import get_db
from marina.models.competition import Season
from marina.models.team import Team
from marina.schemas.squad_sync import (
    SquadImportHistoryRead,
    SquadImportPreviewResponse,
    SquadMemberRead,
    SquadSyncRequest,
    SquadSyncResponse,
)
from marina.services.squad_sync_service import SquadSyncService

router = APIRouter(prefix="/squads", tags=["Squad Synchronization & Roster Management"])


async def _resolve_cfc_and_season(
    db: AsyncSession,
    team_id: Optional[uuid.UUID] = None,
    season_id: Optional[uuid.UUID] = None,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Resolves target team (Chennaiyin FC) and current season (2026-27)."""
    if not team_id:
        t_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc = (await db.execute(t_stmt)).scalars().first()
        if not cfc:
            t_stmt = select(Team).limit(1)
            cfc = (await db.execute(t_stmt)).scalars().first()
        if not cfc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chennaiyin FC team record not found.")
        team_id = cfc.id

    if not season_id:
        s_stmt = select(Season).where(Season.is_current.is_(True))
        cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            s_stmt = select(Season).where(Season.slug.ilike("%2026-27%"))
            cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            s_stmt = select(Season).limit(1)
            cur_s = (await db.execute(s_stmt)).scalars().first()
        if not cur_s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Season 2026-27 record not found.")
        season_id = cur_s.id

    return team_id, season_id


def _get_bundled_roster() -> List[Dict[str, Any]]:
    """Loads bundled official Chennaiyin FC 2026-27 squad data."""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(os.path.dirname(cur_dir)), "data", "chennaiyin_fc_2026_27_squad.csv")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return SquadSyncService.parse_raw_records(f.read(), format_hint="csv")
    return []


# -----------------------------------------------------------------------------
# 1. Roster Import & Preview
# -----------------------------------------------------------------------------

@router.post(
    "/import",
    response_model=SquadImportPreviewResponse,
    summary="Preview Squad Import & Duplicate Detection",
    description="Parses uploaded CSV/JSON roster or body, matches against existing player identities, and flags departures/new signings.",
)
async def preview_squad_import(
    file: Optional[UploadFile] = File(default=None),
    team_id: Optional[uuid.UUID] = Query(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SquadImportPreviewResponse:
    resolved_team_id, resolved_season_id = await _resolve_cfc_and_season(db, team_id, season_id)
    service = SquadSyncService(db)

    raw_records: List[Dict[str, Any]] = []
    if file:
        content = await file.read()
        format_hint = "json" if file.filename and file.filename.endswith(".json") else "csv"
        raw_records = service.parse_raw_records(content, format_hint=format_hint)
    else:
        # Load bundled official supplied squad
        raw_records = _get_bundled_roster()

    if not raw_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid roster data provided in upload or bundled files.",
        )

    try:
        preview = await service.preview_squad_import(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            raw_records=raw_records,
        )
        return SquadImportPreviewResponse.model_validate(preview)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/import/json",
    response_model=SquadImportPreviewResponse,
    summary="Preview Squad Import via JSON Payload",
    description="Accepts JSON list of raw player records to audit before synchronization.",
)
async def preview_squad_import_json(
    payload: List[Dict[str, Any]],
    team_id: Optional[uuid.UUID] = Query(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SquadImportPreviewResponse:
    resolved_team_id, resolved_season_id = await _resolve_cfc_and_season(db, team_id, season_id)
    service = SquadSyncService(db)

    if not payload:
        payload = _get_bundled_roster()

    try:
        preview = await service.preview_squad_import(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            raw_records=payload,
        )
        return SquadImportPreviewResponse.model_validate(preview)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# 2. Squad Synchronization Execution
# -----------------------------------------------------------------------------

@router.post(
    "/sync",
    response_model=SquadSyncResponse,
    summary="Synchronize Squad Roster",
    description="Atomically replaces active squad with incoming roster. Inserts new players, updates profiles, and deactivates departures while preserving all historical match data.",
)
async def synchronize_squad(
    payload: SquadSyncRequest,
    db: AsyncSession = Depends(get_db),
) -> SquadSyncResponse:
    resolved_team_id, resolved_season_id = await _resolve_cfc_and_season(db, payload.team_id, payload.season_id)
    service = SquadSyncService(db)

    incoming_records = payload.players
    if not incoming_records:
        incoming_records = _get_bundled_roster()

    if not incoming_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No incoming squad records provided for synchronization.",
        )

    try:
        sync_result = await service.synchronize_squad(
            team_id=resolved_team_id,
            season_id=resolved_season_id,
            incoming_records=incoming_records,
            confirmed=payload.confirmed,
            deactivate_absent=payload.deactivate_absent,
        )
        return SquadSyncResponse.model_validate(sync_result)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Squad synchronization failed and was rolled back: {str(e)}",
        )


# -----------------------------------------------------------------------------
# 3. Active Squad Read
# -----------------------------------------------------------------------------

@router.get(
    "/chennaiyin-fc/2026-27",
    response_model=List[SquadMemberRead],
    summary="Get Chennaiyin FC 2026–27 Squad",
    description="Returns full active squad with jersey numbers, positions, market values, and contract information.",
)
async def get_chennaiyin_fc_2026_27_squad(
    include_inactive: bool = Query(default=False, description="Include deactivated past squad members"),
    position: Optional[str] = Query(default=None, description="Filter by position group (GK, DEF, MID, FWD)"),
    nationality: Optional[str] = Query(default=None, description="Filter by DOMESTIC or OVERSEAS"),
    db: AsyncSession = Depends(get_db),
) -> List[SquadMemberRead]:
    resolved_team_id, resolved_season_id = await _resolve_cfc_and_season(db)
    service = SquadSyncService(db)

    members = await service.get_active_squad(
        team_id=resolved_team_id,
        season_id=resolved_season_id,
        include_inactive=include_inactive,
        position_filter=position,
        nationality_filter=nationality,
    )
    return [SquadMemberRead.model_validate(m) for m in members]


# -----------------------------------------------------------------------------
# 4. Import & Sync History
# -----------------------------------------------------------------------------

@router.get(
    "/import/history",
    response_model=List[SquadImportHistoryRead],
    summary="Get Squad Import Audit History",
    description="Returns chronological audit logs of squad synchronizations and imports.",
)
async def get_squad_import_history(
    team_id: Optional[uuid.UUID] = Query(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[SquadImportHistoryRead]:
    service = SquadSyncService(db)
    logs = await service.get_import_history(team_id=team_id, season_id=season_id, limit=limit)
    return [SquadImportHistoryRead.model_validate(l) for l in logs]
