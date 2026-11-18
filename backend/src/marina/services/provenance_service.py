"""Provenance and Ingestion Auditing Services."""

from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.provenance import DataSource, ImportHistory
from marina.repositories.provenance_repo import (
    DataSourceRepository,
    ImportHistoryRepository,
)
from marina.schemas.provenance import DataSourceCreate, ImportHistoryCreate


class ProvenanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.source_repo = DataSourceRepository(session)
        self.history_repo = ImportHistoryRepository(session)

    async def get_or_create_data_source(self, payload: DataSourceCreate) -> DataSource:
        existing = await self.source_repo.get_by_code(payload.code)
        if existing:
            return existing
        source = DataSource(**payload.model_dump())
        return await self.source_repo.create(source)

    async def log_import_batch(self, payload: ImportHistoryCreate) -> ImportHistory:
        batch = ImportHistory(**payload.model_dump())
        return await self.history_repo.create(batch)

    async def list_data_sources(self, offset: int = 0, limit: int = 50) -> Sequence[DataSource]:
        return await self.source_repo.list(offset=offset, limit=limit)
