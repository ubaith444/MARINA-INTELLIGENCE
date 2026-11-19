"""Schemas for Players and Club Squad Registrations."""

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from marina.models.common import PlayerPosition, SquadStatus
from marina.schemas.common import BaseSchema


class PlayerBase(BaseSchema):
    slug: str = Field(min_length=2, max_length=128, description="Unique player slug")
    first_name: str = Field(min_length=1, max_length=64)
    last_name: str = Field(min_length=1, max_length=64)
    known_name: Optional[str] = Field(default=None, max_length=128)
    date_of_birth: Optional[date] = None
    nationality: str = Field(default="India", max_length=64)
    secondary_nationality: Optional[str] = Field(default=None, max_length=64)
    primary_position: PlayerPosition = Field(default=PlayerPosition.CM)
    secondary_position: Optional[PlayerPosition] = None
    height_cm: Optional[int] = Field(default=None, ge=100, le=240)
    height_m: Optional[float] = Field(default=None, ge=1.0, le=2.4)
    weight_kg: Optional[int] = Field(default=None, ge=40, le=140)
    preferred_foot: Optional[str] = Field(default=None, max_length=16)
    is_active: bool = Field(default=True)
    squad_number: Optional[int] = Field(default=None, ge=1, le=99)
    joined_date: Optional[date] = None
    previous_club: Optional[str] = Field(default=None, max_length=128)
    contract_expiry: Optional[date] = None
    market_value_inr: Optional[int] = None
    market_value_original: Optional[str] = Field(default=None, max_length=64)
    source_name: Optional[str] = Field(default=None, max_length=128)
    verified_at: Optional[datetime] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    known_name: Optional[str] = None
    primary_position: Optional[PlayerPosition] = None
    secondary_position: Optional[PlayerPosition] = None
    nationality: Optional[str] = None
    secondary_nationality: Optional[str] = None
    height_m: Optional[float] = None
    height_cm: Optional[int] = None
    preferred_foot: Optional[str] = None
    squad_number: Optional[int] = None
    joined_date: Optional[date] = None
    previous_club: Optional[str] = None
    contract_expiry: Optional[date] = None
    market_value_inr: Optional[int] = None
    market_value_original: Optional[str] = None
    is_active: Optional[bool] = None


class PlayerRead(PlayerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_leadership_group: bool = False
    leadership_role: Optional[str] = None


class PlayerDetailRead(PlayerRead):
    career_memberships: List[Dict[str, Any]] = []
    historical_statistics: Dict[str, Any] = {}


class SquadRegistrationBase(BaseSchema):
    player_id: uuid.UUID
    team_id: uuid.UUID
    season_id: uuid.UUID
    jersey_number: Optional[int] = Field(default=None, ge=1, le=99)
    squad_status: SquadStatus = Field(default=SquadStatus.FIRST_TEAM)
    registered_at: Optional[date] = None
    deregistered_at: Optional[date] = None
    is_active: bool = Field(default=True)


class SquadRegistrationCreate(SquadRegistrationBase):
    pass


class SquadRegistrationRead(SquadRegistrationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    player: Optional[PlayerRead] = None
