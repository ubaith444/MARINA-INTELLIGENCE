"""Pydantic v2 Schemas for Football Analytics Contracts."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from marina.schemas.common import BaseSchema


class DataCoverageSchema(BaseSchema):
    sample_matches_count: int
    minutes_tracked: int
    data_source_codes: List[str]
    has_event_level_data: bool
    has_tracking_gps_data: bool
    coverage_notes: str


class RecordSplitSchema(BaseSchema):
    matches_played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int
    clean_sheets: int
    win_percentage: Optional[float] = None
    points_per_match: Optional[float] = None


class RecentFormMatchSchema(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    kickoff: str
    opponent_name: str
    opponent_short: str
    is_home: bool
    score: str
    outcome: str
    points: int


class RecentFormSchema(BaseSchema):
    sequence: List[str]
    sequence_str: str
    form_points: int
    form_ppm: Optional[float] = None
    matches: List[RecentFormMatchSchema] = []


class TeamSeasonPerformanceResponse(BaseSchema):
    team_id: str
    team_name: str
    short_name: str
    season_id: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int
    win_percentage: Optional[float] = None
    points_per_match: Optional[float] = None
    clean_sheets: int
    clean_sheet_percentage: Optional[float] = None
    goals_for_per_match: Optional[float] = None
    goals_against_per_match: Optional[float] = None
    home_record: RecordSplitSchema
    away_record: RecordSplitSchema
    recent_form: RecentFormSchema
    data_coverage: DataCoverageSchema


class AttackingAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    matches_analyzed: int
    goals_scored: int
    goals_per_match: Optional[float] = None
    shots_total: int
    shots_per_match: Optional[float] = None
    shots_on_target: int
    shots_off_target: int
    blocked_shots: int
    shooting_accuracy_pct: Optional[float] = None
    conversion_rate_pct: Optional[float] = None
    expected_goals: Optional[float] = None
    expected_goals_per_match: Optional[float] = None
    shot_efficiency: Optional[float] = None
    big_chances_created: Optional[int] = None
    big_chances_missed: Optional[int] = None
    half_breakdown: Dict[str, Any]
    top_contributors: List[Dict[str, Any]]
    data_coverage: DataCoverageSchema


class DefensiveAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    matches_analyzed: int
    goals_conceded: int
    goals_conceded_per_match: Optional[float] = None
    clean_sheets: int
    clean_sheet_percentage: Optional[float] = None
    expected_goals_conceded: Optional[float] = None
    expected_goals_conceded_per_match: Optional[float] = None
    tackles_total: Optional[int] = None
    tackles_won: Optional[int] = None
    tackle_success_pct: Optional[float] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    saves: Optional[int] = None
    blocked_shots: Optional[int] = None
    total_defensive_actions: Optional[int] = None
    defensive_actions_per_match: Optional[float] = None
    fouls_committed: Optional[int] = None
    fouls_per_match: Optional[float] = None
    yellow_cards: int
    red_cards: int
    discipline_index: int
    data_coverage: DataCoverageSchema


class PlayerPer90Schema(BaseSchema):
    has_sufficient_minutes: bool
    min_minutes_threshold: int
    goals_per_90: Optional[float] = None
    assists_per_90: Optional[float] = None
    goal_contributions_per_90: Optional[float] = None
    shots_per_90: Optional[float] = None
    shots_on_target_per_90: Optional[float] = None
    expected_goals_per_90: Optional[float] = None
    expected_assists_per_90: Optional[float] = None
    passes_completed_per_90: Optional[float] = None
    tackles_per_90: Optional[float] = None
    interceptions_per_90: Optional[float] = None


class PlayerPerformanceResponse(BaseSchema):
    player_id: str
    slug: str
    name: str
    primary_position: str
    nationality: str
    appearances: int
    starts: int
    substitute_appearances: int
    minutes_played: int
    raw_totals: Dict[str, Any]
    per_90: PlayerPer90Schema


class PlayerCompareRequest(BaseModel):
    player_a_id: str
    player_b_id: str
    season_id: Optional[str] = None


class RadarDimensionSchema(BaseSchema):
    dimension: str
    player_a_score: float
    player_b_score: float


class PlayerCompareResponse(BaseSchema):
    player_a: PlayerPerformanceResponse
    player_b: PlayerPerformanceResponse
    radar_comparison: List[RadarDimensionSchema]


class MatchTacticalReportResponse(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    match_status: str
    kickoff: str
    venue: str
    attendance: Optional[int] = None
    referee: Optional[str] = None
    home_team: Dict[str, Any]
    away_team: Dict[str, Any]
    half_by_half: Dict[str, Any]
    timeline: List[Dict[str, Any]]


class ShotEventSchema(BaseSchema):
    shot_id: str
    minute: int
    player_name: str
    team_name: str
    x: float
    y: float
    distance_meters: float
    angle_degrees: float
    outcome: str
    expected_goals: Optional[float] = None
    body_part: str = "RIGHT_FOOT"


class ShotMapResponse(BaseSchema):
    total_shots: int
    goals: int
    conversion_rate_pct: Optional[float] = None
    expected_goals_total: Optional[float] = None
    pitch_dimensions: Dict[str, float]
    shots: List[ShotEventSchema]


class PassingNetworkNode(BaseSchema):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    jersey_number: Optional[int] = None
    avg_x: float
    avg_y: float
    touches: int


class PassingNetworkEdge(BaseSchema):
    passer_id: Optional[str] = None
    passer_name: Optional[str] = None
    recipient_id: Optional[str] = None
    recipient_name: Optional[str] = None
    pass_count: int


class PassingNetworkResponse(BaseSchema):
    nodes_count: int
    edges_count: int
    network_density: Optional[float] = None
    nodes: List[PassingNetworkNode]
    edges: List[PassingNetworkEdge]
