"""Data Provenance and Ingestion Sources REST Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marina.db.session import get_db
from marina.schemas.provenance import DataSourceCreate, DataSourceRead
from marina.services.provenance_service import ProvenanceService

router = APIRouter(prefix="/provenance", tags=["Data Provenance"])


@router.get("/sources", response_model=List[DataSourceRead], summary="List Authoritative Data Sources")
async def list_data_sources(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[DataSourceRead]:
    service = ProvenanceService(db)
    sources = await service.list_data_sources(offset=offset, limit=limit)
    return [DataSourceRead.model_validate(s) for s in sources]


@router.post(
    "/sources",
    response_model=DataSourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register Data Source Provider",
)
async def create_data_source(
    payload: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
) -> DataSourceRead:
    service = ProvenanceService(db)
    source = await service.get_or_create_data_source(payload)
    return DataSourceRead.model_validate(source)
