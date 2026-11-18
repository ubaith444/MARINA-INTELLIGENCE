"""Schemas for Team and Player Match Statistics.
Integrity rules:
- Strictly nullable fields (None indicates unmeasured/unavailable).
- Explicit data source ID and verification status required.
- No artificial zero-casting for missing statistical metrics.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator

from marina.models.common import VerificationStatus
from marina.schemas.common import BaseSchema


class TeamMatchStatisticBase(BaseSchema):
    match_id: uuid.UUID
    team_id: uuid.UUID
    data_source_id: uuid.UUID
    verification_status: VerificationStatus = Field(default=VerificationStatus.PROVISIONAL)
    is_verified: bool = Field(default=False)

    # Possession & Territory (Nullable)
    possession_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)

    # Shooting & Attacking
    shots_total: Optional[int] = Field(default=None, ge=0)
    shots_on_target: Optional[int] = Field(default=None, ge=0)
    shots_off_target: Optional[int] = Field(default=None, ge=0)
    blocked_shots: Optional[int] = Field(default=None, ge=0)
    expected_goals: Optional[float] = Field(default=None, ge=0.0)
    expected_goals_conceded: Optional[float] = Field(default=None, ge=0.0)
    big_chances_created: Optional[int] = Field(default=None, ge=0)
    big_chances_missed: Optional[int] = Field(default=None, ge=0)

    # Passing & Distribution
    passes_total: Optional[int] = Field(default=None, ge=0)
    passes_completed: Optional[int] = Field(default=None, ge=0)
    pass_accuracy_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    touches: Optional[int] = Field(default=None, ge=0)

    # Defending & Disciplinary
    tackles_total: Optional[int] = Field(default=None, ge=0)
    tackles_won: Optional[int] = Field(default=None, ge=0)
    interceptions: Optional[int] = Field(default=None, ge=0)
    clearances: Optional[int] = Field(default=None, ge=0)
    saves: Optional[int] = Field(default=None, ge=0)
    corners: Optional[int] = Field(default=None, ge=0)
    offsides: Optional[int] = Field(default=None, ge=0)
    fouls_committed: Optional[int] = Field(default=None, ge=0)
    yellow_cards: Optional[int] = Field(default=None, ge=0)
    red_cards: Optional[int] = Field(default=None, ge=0)


class TeamMatchStatisticCreate(TeamMatchStatisticBase):
    pass


class TeamMatchStatisticRead(TeamMatchStatisticBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlayerMatchStatisticBase(BaseSchema):
    match_id: uuid.UUID
    player_id: uuid.UUID
    team_id: uuid.UUID
    data_source_id: uuid.UUID
    verification_status: VerificationStatus = Field(default=VerificationStatus.PROVISIONAL)
    is_verified: bool = Field(default=False)

    # Participation
    minutes_played: Optional[int] = Field(default=None, ge=0, le=130)

    # Attacking
    goals: Optional[int] = Field(default=None, ge=0)
    assists: Optional[int] = Field(default=None, ge=0)
    shots_total: Optional[int] = Field(default=None, ge=0)
    shots_on_target: Optional[int] = Field(default=None, ge=0)
    expected_goals: Optional[float] = Field(default=None, ge=0.0)
    expected_assists: Optional[float] = Field(default=None, ge=0.0)
    key_passes: Optional[int] = Field(default=None, ge=0)
    dribbles_attempted: Optional[int] = Field(default=None, ge=0)
    dribbles_succeeded: Optional[int] = Field(default=None, ge=0)

    # Distribution
    passes_total: Optional[int] = Field(default=None, ge=0)
    passes_completed: Optional[int] = Field(default=None, ge=0)
    pass_accuracy_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    crosses_total: Optional[int] = Field(default=None, ge=0)
    crosses_successful: Optional[int] = Field(default=None, ge=0)

    # Defending & Duels
    tackles_total: Optional[int] = Field(default=None, ge=0)
    tackles_won: Optional[int] = Field(default=None, ge=0)
    interceptions: Optional[int] = Field(default=None, ge=0)
    clearances: Optional[int] = Field(default=None, ge=0)
    blocks: Optional[int] = Field(default=None, ge=0)
    aerial_duels_total: Optional[int] = Field(default=None, ge=0)
    aerial_duels_won: Optional[int] = Field(default=None, ge=0)
    ground_duels_total: Optional[int] = Field(default=None, ge=0)
    ground_duels_won: Optional[int] = Field(default=None, ge=0)

    # Discipline & Goalkeeping
    fouls_committed: Optional[int] = Field(default=None, ge=0)
    fouls_drawn: Optional[int] = Field(default=None, ge=0)
    yellow_cards: Optional[int] = Field(default=None, ge=0)
    red_cards: Optional[int] = Field(default=None, ge=0)
    saves: Optional[int] = Field(default=None, ge=0)
    goals_conceded: Optional[int] = Field(default=None, ge=0)
    clean_sheet: Optional[bool] = None

    # Physical / Tracking
    distance_covered_km: Optional[float] = Field(default=None, ge=0.0)
    sprints_count: Optional[int] = Field(default=None, ge=0)
    top_speed_kmh: Optional[float] = Field(default=None, ge=0.0)


class PlayerMatchStatisticCreate(PlayerMatchStatisticBase):
    pass


class PlayerMatchStatisticRead(PlayerMatchStatisticBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
