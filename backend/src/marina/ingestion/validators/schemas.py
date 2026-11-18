"""Pandera and Pydantic Ingestion Validation Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
try:
    import pandera.pandas as pa
except ImportError:
    import pandera as pa
from pydantic import BaseModel, Field, field_validator


class IngestedFixtureRecord(BaseModel):
    """Pydantic contract for raw fixture records."""
    match_number: Optional[int] = Field(default=None, ge=1)
    scheduled_kickoff: str
    home_team: str = Field(min_length=2)
    away_team: str = Field(min_length=2)
    venue: Optional[str] = None
    city: Optional[str] = None
    match_status: str = Field(default="SCHEDULED")
    home_score: Optional[int] = None
    away_score: Optional[int] = None

    @field_validator("away_team")
    @classmethod
    def check_distinct_teams(cls, v: str, info) -> str:
        home = info.data.get("home_team")
        if home and home.strip().lower() == v.strip().lower():
            raise ValueError("Home team and away team cannot be identical.")
        return v

    @field_validator("home_score", "away_score")
    @classmethod
    def check_no_scores_on_scheduled(cls, v: Optional[int], info) -> Optional[int]:
        status = info.data.get("match_status", "SCHEDULED").upper()
        if status in ("SCHEDULED", "TIMED", "POSTPONED", "CANCELLED") and v is not None:
            raise ValueError(f"Fixture in '{status}' status must not contain scores.")
        return v


class IngestedPlayerRecord(BaseModel):
    """Pydantic contract for squad player records."""
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    known_name: Optional[str] = None
    jersey_number: Optional[int] = Field(default=None, ge=1, le=99)
    position: Optional[str] = None
    nationality: str = Field(default="India")
    date_of_birth: Optional[str] = None
    squad_status: str = Field(default="FIRST_TEAM")


# ------------------------------------------------------------------------------
# Pandera DataFrame Schema Validators
# ------------------------------------------------------------------------------

FixturesDataFrameSchema = pa.DataFrameSchema(
    columns={
        "home_team": pa.Column(str, nullable=False),
        "away_team": pa.Column(str, nullable=False),
        "scheduled_kickoff": pa.Column(pa.DateTime, nullable=False),
        "match_status": pa.Column(str, checks=pa.Check.isin(["SCHEDULED", "TIMED", "IN_PLAY", "FINISHED", "POSTPONED", "CANCELLED"])),
        "home_score": pa.Column(float, nullable=True, required=False),
        "away_score": pa.Column(float, nullable=True, required=False),
    },
    checks=[
        pa.Check(lambda df: df["home_team"] != df["away_team"], error="Home and away teams must differ")
    ],
    coerce=True,
)

SquadDataFrameSchema = pa.DataFrameSchema(
    columns={
        "first_name": pa.Column(str, nullable=False),
        "last_name": pa.Column(str, nullable=False),
        "jersey_number": pa.Column(float, nullable=True, required=False, checks=pa.Check.greater_than_or_equal_to(1)),
        "position": pa.Column(str, nullable=True),
        "nationality": pa.Column(str, nullable=False),
    },
    coerce=True,
)
