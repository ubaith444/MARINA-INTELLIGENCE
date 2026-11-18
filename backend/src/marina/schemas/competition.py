"""Schemas for Competitions and Seasons."""

import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import Field

from marina.schemas.common import BaseSchema


class CompetitionBase(BaseSchema):
    code: str = Field(min_length=2, max_length=32, description="Unique code, e.g. ISL")
    name: str = Field(min_length=2, max_length=128, description="Competition name")
    country: str = Field(default="India", max_length=64)
    federation: str = Field(default="AIFF", max_length=64)
    tier: int = Field(default=1, ge=1)
    competition_type: str = Field(default="LEAGUE", max_length=32)
    is_active: bool = Field(default=True)


class CompetitionCreate(CompetitionBase):
    pass


class CompetitionRead(CompetitionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SeasonBase(BaseSchema):
    competition_id: uuid.UUID
    name: str = Field(min_length=4, max_length=64, description="Season label, e.g. 2026–27")
    slug: str = Field(min_length=4, max_length=64, description="URL slug, e.g. isl-2026-27")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = Field(default=False)
    is_completed: bool = Field(default=False)


class SeasonCreate(SeasonBase):
    pass


class SeasonRead(SeasonBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
