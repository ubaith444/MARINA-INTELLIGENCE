"""Automated Tests for Pandera Validation and Cross-Source Conflict Detection."""

from datetime import datetime, timezone
import pandas as pd
import pandera as pa
import pytest
from pydantic import ValidationError

from marina.ingestion.validators.conflict_detector import ConflictDetector
from marina.ingestion.validators.schemas import (
    FixturesDataFrameSchema,
    IngestedFixtureRecord,
    SquadDataFrameSchema,
)
from marina.models.common import MatchStatus, VerificationStatus


def test_pandera_fixtures_validation():
    """Verify Pandera validates tabular fixtures dataframe."""
    valid_df = pd.DataFrame([
        {
            "home_team": "Chennaiyin FC",
            "away_team": "Kerala Blasters FC",
            "scheduled_kickoff": pd.to_datetime("2026-11-28 19:30:00"),
            "match_status": "SCHEDULED",
            "home_score": None,
            "away_score": None,
        }
    ])
    # Should validate without error
    FixturesDataFrameSchema.validate(valid_df)

    # Identical home and away teams must fail
    invalid_df = pd.DataFrame([
        {
            "home_team": "Chennaiyin FC",
            "away_team": "Chennaiyin FC",
            "scheduled_kickoff": pd.to_datetime("2026-11-28 19:30:00"),
            "match_status": "SCHEDULED",
            "home_score": None,
            "away_score": None,
        }
    ])
    with pytest.raises(pa.errors.SchemaError):
        FixturesDataFrameSchema.validate(invalid_df)


def test_conflict_detector_score_discrepancy():
    """CRITICAL RULE: Conflicting match score reports must be flagged DISPUTED, never overwritten."""
    detector = ConflictDetector()

    # Existing official result: 5-3
    # Incoming report claims: 4-3
    is_conflict, v_status = detector.check_match_score_conflict(
        match_id="test-match-123",
        existing_status=MatchStatus.FINISHED,
        existing_home=5,
        existing_away=3,
        incoming_status=MatchStatus.FINISHED,
        incoming_home=4,  # Conflicting score!
        incoming_away=3,
        source_code="SECONDARY_REPORT",
    )

    assert is_conflict is True
    assert v_status == VerificationStatus.DISPUTED
    assert len(detector.conflicts) == 1
    assert detector.conflicts[0].conflict_type == "SCORE_DISCREPANCY"
    assert detector.conflicts[0].existing_value == "5-3"
    assert detector.conflicts[0].incoming_value == "4-3"


def test_pydantic_rejects_scores_on_scheduled_fixture():
    """Verify Pydantic model rejects fixture records with scores when status is SCHEDULED."""
    with pytest.raises(ValidationError):
        IngestedFixtureRecord(
            match_number=8,
            scheduled_kickoff="2026-11-28T19:30:00Z",
            home_team="Chennaiyin FC",
            away_team="Kerala Blasters FC",
            match_status="SCHEDULED",
            home_score=2,  # Invalid: scores cannot exist on scheduled fixtures!
            away_score=1,
        )
