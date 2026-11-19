"""Pydantic schemas for Season Performance Overview and Data Quality."""

from typing import List, Optional
from pydantic import BaseModel, Field

from marina.schemas.common import BaseSchema


class SeasonOverviewResponse(BaseSchema):
    season_id: str
    season_name: str
    team_id: str
    team_name: str
    short_name: str
    matches_played: int
    matches_remaining: int
    total_fixtures: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_scored: int
    goals_conceded: int
    goal_difference: int
    win_percentage: float
    points_per_match: float
    clean_sheets: int
    failed_to_score: int
    is_season_active: bool
    verification_status: str
    recent_form: List[str]
    calculated_at: str


class SeasonFormMatch(BaseSchema):
    match_id: str
    match_number: int
    date: Optional[str] = None
    opponent_name: str
    opponent_short_name: str
    is_home: bool
    score_cfc: Optional[int] = None
    score_opponent: Optional[int] = None
    result: str  # "W", "D", "L"


class SeasonFormResponse(BaseSchema):
    sequence: List[str]
    form_points: int
    form_ppm: float
    matches: List[SeasonFormMatch]


class SeasonResultItem(BaseSchema):
    match_id: str
    match_number: int
    date: Optional[str] = None
    home_team: str
    away_team: str
    opponent_name: Optional[str] = None
    opponent_short: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    cfc_score: Optional[int] = None
    opponent_score: Optional[int] = None
    is_home: bool
    outcome: str  # "WIN", "DRAW", "LOSS"
    venue: Optional[str] = None
    kickoff_time: Optional[str] = None


class SeasonHomeAwaySplit(BaseSchema):
    matches_played: int
    matches_scheduled: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_scored: int
    goals_conceded: int
    goal_difference: int
    win_percentage: float
    points_per_match: float
    clean_sheets: int


class SeasonHomeAwayResponse(BaseSchema):
    home: SeasonHomeAwaySplit
    away: SeasonHomeAwaySplit


class SeasonScoringResponse(BaseSchema):
    total_goals_scored: int
    total_goals_conceded: int
    goals_per_match: float
    goals_conceded_per_match: float
    home_goals_scored: int
    home_goals_conceded: int
    away_goals_scored: int
    away_goals_conceded: int
    clean_sheets: int
    clean_sheet_percentage: float
    scoring_records_available: bool


class PlayerSeasonStatisticItem(BaseSchema):
    player_id: str
    name: str
    jersey_number: Optional[int] = None
    position: str
    primary_position: str
    nationality: str
    is_indian: bool = False
    appearances: int = 0
    starts: int = 0
    substitute_appearances: int = 0
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    clean_sheets: Optional[int] = None
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
    goals_conceded: Optional[int] = None
    save_percentage: Optional[float] = None
    goals_per_90: Optional[float] = None
    assists_per_90: Optional[float] = None
    shots_per_90: Optional[float] = None
    passes_completed_per_90: Optional[float] = None
    tackles_per_90: Optional[float] = None
    has_sufficient_minutes: bool = False
    is_leadership_group: bool = False
    leadership_role: Optional[str] = None


class TopScorerItem(BaseSchema):
    player_id: str
    name: str
    jersey_number: Optional[int] = None
    position: str
    goals: int
    assists: int
    minutes_played: int


class DataQualityCheckItem(BaseSchema):
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str


class DataQualityResponse(BaseSchema):
    total_players: int
    duplicate_players_count: int
    total_fixtures: int
    duplicate_fixtures_count: int
    scheduled_matches_count: int
    completed_matches_count: int
    discrepant_matches_count: int
    unplayed_matches_with_scores: int
    finished_matches_without_scores: int
    orphan_events_count: int
    season_contamination_detected: bool
    data_integrity_score_pct: float
    checks: List[DataQualityCheckItem]
