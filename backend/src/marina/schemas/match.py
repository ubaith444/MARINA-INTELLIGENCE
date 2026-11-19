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
    scheduled_kickoff: Optional[datetime] = None
    actual_kickoff: Optional[datetime] = None
    match_status: MatchStatus = Field(default=MatchStatus.SCHEDULED)

    # Fixture Leg & Verification Metadata
    fixture_leg: Optional[str] = "FIRST_LEG"  # FIRST_LEG, SECOND_LEG
    publication_status: str = "PROVISIONAL"  # PUBLISHED, PROVISIONAL
    verification_status: str = "PROVISIONAL"  # PUBLISHED, PROVISIONAL, DISCREPANCY_FLAGGED, PENDING
    venue_verification_status: Optional[str] = None  # CONFIRMED, INFERRED, TBC
    has_discrepancy: bool = False
    discrepancy_notes: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    kickoff_time_ist: Optional[str] = None

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


class MatchLineupRead(BaseSchema):
    id: uuid.UUID
    match_id: uuid.UUID
    team_id: uuid.UUID
    player_id: uuid.UUID
    lineup_role: LineupRole
    position: Optional[PlayerPosition] = None
    tactical_formation: Optional[str] = None
    jersey_number: Optional[int] = None
    is_captain: bool
    minutes_played: Optional[int] = None
    sub_out_minute: Optional[int] = None
    is_verified: bool
    player: Optional[PlayerRead] = None


class MatchSubstituteRead(BaseSchema):
    id: uuid.UUID
    match_id: uuid.UUID
    team_id: uuid.UUID
    player_id: uuid.UUID
    jersey_number: Optional[int] = None
    position: Optional[PlayerPosition] = None
    is_used: bool
    sub_in_minute: Optional[int] = None
    sub_out_minute: Optional[int] = None
    replaced_player_id: Optional[uuid.UUID] = None
    minutes_played: Optional[int] = None
    is_verified: bool
    player: Optional[PlayerRead] = None
    replaced_player: Optional[PlayerRead] = None


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
    primary_player: Optional[PlayerRead] = None
    secondary_player: Optional[PlayerRead] = None


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


class FixtureImportResponse(BaseSchema):
    batch_id: str
    season_id: str
    total_processed: int
    published_count: int
    provisional_count: int
    discrepancies_flagged: int
    new_created: int
    updated: int
    status: str
    message: str
    timestamp: str


class PlayerMatchDetailItem(BaseSchema):
    player_id: uuid.UUID
    name: str
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    lineup_role: str = "STARTER"
    is_captain: bool = False
    minutes_played: Optional[int] = None
    sub_in_minute: Optional[int] = None
    sub_out_minute: Optional[int] = None
    replaced_player_id: Optional[uuid.UUID] = None
    replaced_player_name: Optional[str] = None
    tactical_formation: Optional[str] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    shots_total: Optional[int] = None
    shots_on_target: Optional[int] = None
    passes_total: Optional[int] = None
    passes_completed: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    tackles_won: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    blocks: Optional[int] = None
    saves: Optional[int] = None
    clean_sheet: Optional[bool] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    verification_status: str = "VERIFIED"
    is_verified: bool = True


class MatchPlayersResponse(BaseSchema):
    match_id: uuid.UUID
    formation: Optional[str] = None
    starting_xi: List[PlayerMatchDetailItem] = []
    substitutes: List[PlayerMatchDetailItem] = []
    bench_unused: List[PlayerMatchDetailItem] = []
    data_source: Optional[str] = None


