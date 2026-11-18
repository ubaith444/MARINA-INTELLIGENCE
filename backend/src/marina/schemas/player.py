"""Schemas for Players and Club Squad Registrations."""

import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import Field

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
    height_cm: Optional[int] = Field(default=None, ge=120, le=230)
    weight_kg: Optional[int] = Field(default=None, ge=40, le=140)
    preferred_foot: Optional[str] = Field(default=None, max_length=16)
    is_active: bool = Field(default=True)


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


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
