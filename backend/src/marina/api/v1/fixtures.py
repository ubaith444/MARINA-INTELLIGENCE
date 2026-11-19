"""Fixtures & ISL 2026–27 Season Schedule REST Endpoints."""

import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import EntityNotFoundError
from marina.db.session import get_db
from marina.schemas.match import (
    FixtureImportResponse,
    MatchDetailRead,
    MatchRead,
)
from marina.services.fixture_service import FixtureService

router = APIRouter(prefix="/fixtures", tags=["Fixtures & Season Schedule"])


def _load_bundled_fixtures() -> List[Dict[str, Any]]:
    """Loads official bundled Chennaiyin FC 2026–27 24 fixtures dataset."""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(cur_dir)), "data", "chennaiyin_fc_2026_27_fixtures.json"
    )
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return FixtureService.parse_raw_fixtures(f.read(), format_hint="json")

    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(cur_dir)), "data", "chennaiyin_fc_2026_27_fixtures.csv"
    )
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            return FixtureService.parse_raw_fixtures(f.read(), format_hint="csv")

    return []


# -----------------------------------------------------------------------------
# 1. Season Specific Fixtures List (Must be declared before /{match_id})
# -----------------------------------------------------------------------------

@router.get(
    "/season/2026-27",
    response_model=List[MatchRead],
    summary="Get Chennaiyin FC 2026–27 Full Season Fixtures",
    description="Returns all 24 fixtures for Chennaiyin FC in ISL 2026–27 (12 published first-leg and 12 provisional second-leg).",
)
async def get_season_2026_27_fixtures(
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    service = FixtureService(db)
    fixtures = await service.get_season_fixtures("2026-27")
    return [MatchRead.model_validate(f) for f in fixtures]


# -----------------------------------------------------------------------------
# 2. General Filtered Fixtures List
# -----------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[MatchRead],
    summary="List & Filter Fixtures",
    description="Query fixtures with filters for opponent, home/away venue, publication status, verification status, and date range.",
)
async def list_fixtures(
    season_id: Optional[uuid.UUID] = Query(default=None),
    opponent: Optional[str] = Query(default=None, description="Opponent club name or abbreviation"),
    home_away: Optional[str] = Query(default=None, description="Filter: HOME, AWAY, or ALL"),
    verification_status: Optional[str] = Query(
        default=None,
        description="Filter: PUBLISHED, PROVISIONAL, DISCREPANCY_FLAGGED, COMPLETED, or ALL",
    ),
    publication_status: Optional[str] = Query(
        default=None, description="Filter: PUBLISHED or PROVISIONAL"
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[MatchRead]:
    service = FixtureService(db)
    fixtures = await service.list_fixtures(
        season_id=season_id,
        opponent=opponent,
        home_away=home_away,
        verification_status=verification_status,
        publication_status=publication_status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return [MatchRead.model_validate(f) for f in fixtures]


# -----------------------------------------------------------------------------
# 3. Single Fixture Detail
# -----------------------------------------------------------------------------

@router.get(
    "/{match_id}",
    response_model=MatchDetailRead,
    summary="Get Fixture Details by Match ID",
    description="Returns detailed fixture metadata including teams, venue, lineups, and match events.",
)
async def get_fixture_by_id(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MatchDetailRead:
    service = FixtureService(db)
    fixture = await service.get_fixture_by_id(match_id)
    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fixture with ID '{match_id}' not found.",
        )
    return MatchDetailRead.model_validate(fixture)


# -----------------------------------------------------------------------------
# 4. Fixture Import Endpoint (Idempotent)
# -----------------------------------------------------------------------------

@router.post(
    "/import",
    response_model=FixtureImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Import or Update 24 Chennaiyin FC Fixtures",
    description="Idempotently imports the 24-fixture schedule into PostgreSQL. Preserves existing verified scores without overwriting.",
)
async def import_fixtures(
    file: Optional[UploadFile] = File(default=None),
    payload: Optional[List[Dict[str, Any]]] = Body(default=None),
    season_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> FixtureImportResponse:
    service = FixtureService(db)

    raw_records: List[Dict[str, Any]] = []

    if file:
        content = await file.read()
        format_hint = "json" if file.filename and file.filename.endswith(".json") else "csv"
        raw_records = service.parse_raw_fixtures(content, format_hint=format_hint)
    elif payload:
        raw_records = payload
    else:
        # Load bundled official dataset
        raw_records = _load_bundled_fixtures()

    if not raw_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fixture records provided in upload or bundled dataset.",
        )

    try:
        result = await service.import_fixtures(
            raw_records=raw_records,
            season_id=season_id,
        )
        return FixtureImportResponse.model_validate(result)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fixture import failed: {str(e)}",
        )
