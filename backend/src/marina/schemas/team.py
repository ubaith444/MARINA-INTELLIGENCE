"""Schemas for Teams and Venues."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import Field

from marina.schemas.common import BaseSchema


class VenueBase(BaseSchema):
    name: str = Field(min_length=2, max_length=128)
    city: str = Field(min_length=2, max_length=64)
    state: Optional[str] = Field(default=None, max_length=64)
    country: str = Field(default="India", max_length=64)
    capacity: Optional[int] = Field(default=None, ge=0)
    surface: Optional[str] = Field(default="Natural Grass", max_length=32)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = Field(default=True)


class VenueCreate(VenueBase):
    pass


class VenueRead(VenueBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamBase(BaseSchema):
    name: str = Field(min_length=2, max_length=128, description="Official club name")
    short_name: str = Field(min_length=2, max_length=32, description="Short code, e.g. CFC")
    slug: str = Field(min_length=2, max_length=64, description="Slug, e.g. chennaiyin-fc")
    founded_year: Optional[int] = Field(default=None, ge=1850, le=2100)
    primary_venue_id: Optional[uuid.UUID] = None
    primary_color: Optional[str] = Field(default=None, max_length=16)
    secondary_color: Optional[str] = Field(default=None, max_length=16)
    website_url: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    primary_venue: Optional[VenueRead] = None


class LeadershipMemberRead(BaseSchema):
    id: uuid.UUID
    player_id: uuid.UUID
    player_name: str
    jersey_number: Optional[int] = None
    position: str
    primary_position: str
    nationality: str
    is_indian: bool = False
    leadership_role: str = "Leadership Group"
    is_captain: bool = False
    is_vice_captain: bool = False
    image_url: Optional[str] = None
    notes: Optional[str] = None


class LeadershipGroupResponse(BaseSchema):
    team_id: uuid.UUID
    team_name: str
    team_short_name: str
    season_id: uuid.UUID
    season_name: str
    role_title: str = "Leadership Group"
    total_members: int
    members: List[LeadershipMemberRead]

