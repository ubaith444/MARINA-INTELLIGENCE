"""Data Synchronization, Audit Logs, and Discrepancy REST Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.db.session import get_db
from marina.models.provenance import DataMetricVerification, DataSyncLog
from marina.schemas.common import BaseSchema
from marina.services.match_ingestion_service import MatchIngestionService

router = APIRouter(prefix="/sync", tags=["Data Sync & Provenance Audit"])


class SyncLogRead(BaseSchema):
    id: str
    sync_type: str
    provider_name: str
    status: str
    matches_synced: int
    records_updated: int
    discrepancy_count: int
    details: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: int
    created_at: str


class DataVerificationRead(BaseSchema):
    id: str
    match_id: Optional[str] = None
    entity_type: str
    entity_id: Optional[str] = None
    metric_name: str
    primary_source: str
    primary_value: Optional[str] = None
    secondary_source: Optional[str] = None
    secondary_value: Optional[str] = None
    verification_status: str
    is_disputed: bool
    notes: Optional[str] = None
    created_at: str


class SyncTriggerResponse(BaseSchema):
    status: str
    matches_synced: int
    discrepancies_flagged: int
    records_updated: int
    duration_ms: int
    message: str


@router.post(
    "/matches",
    response_model=SyncTriggerResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger Completed Match Synchronization",
    description="Synchronizes the last 5 completed ISL 2026–27 matches with verified metrics and logs discrepancies.",
)
async def trigger_match_sync(db: AsyncSession = Depends(get_db)) -> SyncTriggerResponse:
    service = MatchIngestionService(db)
    result = await service.ingest_completed_matches()
    return SyncTriggerResponse(
        status=result["status"],
        matches_synced=result["matches_synced"],
        discrepancies_flagged=result["discrepancies_flagged"],
        records_updated=result["records_updated"],
        duration_ms=result["duration_ms"],
        message="Successfully synchronized 5 completed fixtures and recorded verification provenance.",
    )


@router.get("/logs", response_model=List[SyncLogRead], summary="List Data Synchronization Audit Logs")
async def list_sync_logs(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[SyncLogRead]:
    stmt = select(DataSyncLog).order_by(desc(DataSyncLog.created_at)).limit(limit)
    logs = (await db.execute(stmt)).scalars().all()
    return [
        SyncLogRead(
            id=str(log.id),
            sync_type=log.sync_type,
            provider_name=log.provider_name,
            status=log.status,
            matches_synced=log.matches_synced,
            records_updated=log.records_updated,
            discrepancy_count=log.discrepancy_count,
            details=log.details,
            error_message=log.error_message,
            duration_ms=log.duration_ms,
            created_at=log.created_at.isoformat() if log.created_at else "",
        )
        for log in logs
    ]


@router.get("/discrepancies", response_model=List[DataVerificationRead], summary="List Discrepant & Disputed Data Metrics")
async def list_discrepancies(
    disputed_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[DataVerificationRead]:
    stmt = select(DataMetricVerification)
    if disputed_only:
        stmt = stmt.where(DataMetricVerification.is_disputed.is_(True))
    stmt = stmt.order_by(desc(DataMetricVerification.created_at)).limit(limit)
    records = (await db.execute(stmt)).scalars().all()
    return [
        DataVerificationRead(
            id=str(r.id),
            match_id=str(r.match_id) if r.match_id else None,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            metric_name=r.metric_name,
            primary_source=r.primary_source,
            primary_value=r.primary_value,
            secondary_source=r.secondary_source,
            secondary_value=r.secondary_value,
            verification_status=r.verification_status,
            is_disputed=r.is_disputed,
            notes=r.notes,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in records
    ]
