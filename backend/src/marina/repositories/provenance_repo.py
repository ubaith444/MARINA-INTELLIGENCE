"""Provenance and Data Source Repositories."""

from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.provenance import DataSource, ImportHistory
from marina.repositories.base import BaseRepository


class DataSourceRepository(BaseRepository[DataSource]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DataSource, session)

    async def get_by_code(self, code: str) -> Optional[DataSource]:
        res = await self.session.execute(
            select(DataSource).where(DataSource.code == code)
        )
        return res.scalars().first()


class ImportHistoryRepository(BaseRepository[ImportHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ImportHistory, session)

    async def list_by_source(
        self, data_source_id: str, offset: int = 0, limit: int = 50
    ) -> Sequence[ImportHistory]:
        stmt = (
            select(ImportHistory)
            .where(ImportHistory.data_source_id == data_source_id)
            .options(selectinload(ImportHistory.data_source))
            .order_by(ImportHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
