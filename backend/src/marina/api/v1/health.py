"""Health and Diagnostic REST Endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.config import settings
from marina.db.session import check_db_connection, get_db
from marina.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Platform Health & Connectivity Check",
    description="Validates FastAPI runtime health, database connectivity, and core platform metadata.",
)
async def get_health() -> HealthResponse:
    db_ok = await check_db_connection()
    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database="connected" if db_ok else "unreachable",
        app_env=settings.APP_ENV,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
        focus_club=settings.DEFAULT_CLUB_NAME,
        focus_season=settings.DEFAULT_SEASON_CODE,
        focus_competition="Indian Super League",
    )
