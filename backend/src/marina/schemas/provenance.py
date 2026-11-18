"""Schemas for Data Sources and Import Provenance."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field

from marina.models.common import BatchStatus, ProviderType
from marina.schemas.common import BaseSchema


class DataSourceBase(BaseSchema):
    code: str = Field(min_length=2, max_length=64, description="Unique source code, e.g. ISL_OFFICIAL")
    name: str = Field(min_length=2, max_length=128, description="Human readable source name")
    provider_type: ProviderType = Field(default=ProviderType.OFFICIAL_LEAGUE)
    base_url: Optional[str] = Field(default=None, max_length=255)
    api_version: Optional[str] = Field(default=None, max_length=32)
    is_active: bool = Field(default=True)
    trust_score: int = Field(default=100, ge=1, le=100, description="Trust factor (1-100)")
    notes: Optional[str] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceRead(DataSourceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ImportHistoryBase(BaseSchema):
    data_source_id: uuid.UUID
    entity_type: str = Field(max_length=64)
    batch_id: str = Field(max_length=128)
    status: BatchStatus = Field(default=BatchStatus.PENDING)
    records_imported: int = Field(default=0, ge=0)
    records_failed: int = Field(default=0, ge=0)
    error_payload: Optional[str] = None
    checksum_hash: Optional[str] = None


class ImportHistoryCreate(ImportHistoryBase):
    pass


class ImportHistoryRead(ImportHistoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
