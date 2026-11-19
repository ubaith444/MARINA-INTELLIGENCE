"""Schemas for Squad Import, Synchronization, and Historical Audits."""

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from marina.schemas.common import BaseSchema


class RawSquadPlayerIn(BaseModel):
    squad_number: Optional[int] = Field(default=None, alias="#")
    player_name: str = Field(alias="Player")
    position: str = Field(alias="Position")
    date_of_birth: Optional[str] = Field(default=None, alias="Date of birth (Age)")
    nationality: str = Field(default="India", alias="Nationality")
    height: Optional[str] = Field(default=None, alias="Height")
    preferred_foot: Optional[str] = Field(default=None, alias="Foot")
    joined_date: Optional[str] = Field(default=None, alias="Joined")
    previous_club: Optional[str] = Field(default=None, alias="Signed from")
    contract_expiry: Optional[str] = Field(default=None, alias="Contract until")
    market_value: Optional[str] = Field(default=None, alias="Market value")

    class Config:
        populate_by_name = True


class SquadImportPreviewResponse(BaseSchema):
    team_id: str
    season_id: str
    batch_id: str
    total_incoming: int
    new_players: List[Dict[str, Any]]
    updated_players: List[Dict[str, Any]]
    leaving_players: List[Dict[str, Any]]
    retained_players: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    missing_fields_summary: Dict[str, int]
    requires_confirmation: bool


class SquadSyncRequest(BaseModel):
    team_id: Optional[uuid.UUID] = None
    season_id: Optional[uuid.UUID] = None
    batch_id: Optional[str] = None
    players: Optional[List[Dict[str, Any]]] = None
    confirmed: bool = Field(default=True, description="Explicit user confirmation to deactivate departed players")
    deactivate_absent: bool = Field(default=True, description="Deactivate 2026-27 squad members not in incoming roster")


class SquadSyncResponse(BaseSchema):
    batch_id: str
    team_id: str
    season_id: str
    total_processed: int
    new_created: int
    updated: int
    deactivated: int
    retained: int
    active_squad_count: int
    status: str
    message: str
    timestamp: str


class SquadMemberRead(BaseSchema):
    id: str
    player_id: str
    name: str
    known_name: Optional[str] = None
    squad_number: Optional[int] = None
    position: str
    pos_group: str
    nationality: str
    secondary_nationality: Optional[str] = None
    is_domestic: bool
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    height_m: Optional[float] = None
    height_cm: Optional[int] = None
    preferred_foot: Optional[str] = None
    joined_date: Optional[str] = None
    previous_club: Optional[str] = None
    contract_expiry: Optional[str] = None
    market_value_inr: Optional[int] = None
    market_value_original: Optional[str] = None
    is_active: bool


class SquadImportHistoryRead(BaseSchema):
    id: str
    batch_id: str
    team_id: str
    season_id: str
    source_name: str
    total_incoming: int
    new_players: int
    updated_players: int
    deactivated_players: int
    retained_players: int
    status: str
    report_summary: Optional[str] = None
    imported_by: Optional[str] = None
    created_at: str


class PlayerUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    known_name: Optional[str] = None
    primary_position: Optional[str] = None
    nationality: Optional[str] = None
    secondary_nationality: Optional[str] = None
    preferred_foot: Optional[str] = None
    height_m: Optional[float] = None
    squad_number: Optional[int] = None
    joined_date: Optional[str] = None
    contract_expiry: Optional[str] = None
    previous_club: Optional[str] = None
    market_value_inr: Optional[int] = None
    market_value_original: Optional[str] = None
    is_active: Optional[bool] = None
