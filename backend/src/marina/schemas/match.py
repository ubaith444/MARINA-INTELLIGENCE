"""Schemas for Matches, Lineups, and Match Events."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import Field

from marina.models.common import (
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    VerificationStatus,
)
from marina.schemas.common import BaseSchema
from marina.schemas.player import PlayerRead
from marina.schemas.team import TeamRead, VenueRead


class MatchBase(BaseSchema):
    season_id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    venue_id: Optional[uuid.UUID] = None
    match_number: Optional[int] = Field(default=None, ge=1, le=100)
    scheduled_kickoff: datetime
    actual_kickoff: Optional[datetime] = None
    match_status: MatchStatus = Field(default=MatchStatus.SCHEDULED)

    # Strictly Nullable: Never populate fabricated scores for upcoming fixtures
    home_score: Optional[int] = Field(default=None, ge=0)
    away_score: Optional[int] = Field(default=None, ge=0)
    home_penalty_score: Optional[int] = Field(default=None, ge=0)
    away_penalty_score: Optional[int] = Field(default=None, ge=0)
    attendance: Optional[int] = Field(default=None, ge=0)
    referee: Optional[str] = Field(default=None, max_length=128)
    pitch_condition: Optional[str] = Field(default=None, max_length=64)
    weather_summary: Optional[str] = Field(default=None, max_length=128)


class MatchCreate(MatchBase):
    pass


class LineupRead(BaseSchema):
    id: uuid.UUID
    match_id: uuid.UUID
    team_id: uuid.UUID
    player_id: uuid.UUID
    squad_registration_id: Optional[uuid.UUID] = None
    lineup_role: LineupRole
    position: Optional[PlayerPosition] = None
    tactical_formation: Optional[str] = None
    jersey_number: Optional[int] = None
    is_captain: bool
    minutes_played: Optional[int] = None
    is_substitute_in: bool
    sub_in_minute: Optional[int] = None
    sub_out_minute: Optional[int] = None
    player: Optional[PlayerRead] = None


class MatchEventRead(BaseSchema):
    id: uuid.UUID
    match_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    primary_player_id: Optional[uuid.UUID] = None
    secondary_player_id: Optional[uuid.UUID] = None
    data_source_id: Optional[uuid.UUID] = None
    event_type: EventType
    period: MatchPeriod
    minute: int
    stoppage_minute: Optional[int] = None
    description: Optional[str] = None
    verification_status: VerificationStatus
    is_verified: bool


class MatchRead(MatchBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    home_team: Optional[TeamRead] = None
    away_team: Optional[TeamRead] = None
    venue: Optional[VenueRead] = None


class MatchDetailRead(MatchRead):
    lineups: List[LineupRead] = []
    events: List[MatchEventRead] = []
