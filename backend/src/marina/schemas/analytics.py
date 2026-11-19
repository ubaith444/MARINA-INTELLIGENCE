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
    goals_for_per_match: Optional[float] = None
    goals_against_per_match: Optional[float] = None


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
    average_possession_pct: Optional[float] = None
    home_record: RecordSplitSchema
    away_record: RecordSplitSchema
    recent_form: RecentFormSchema
    data_coverage: DataCoverageSchema
    calculated_at: Optional[str] = None


class HomeAwayComparisonSchema(BaseSchema):
    point_ratio_home_to_away: Optional[float] = None
    win_pct_delta: Optional[float] = None
    home_advantage_index: Optional[float] = None


class HomeAwayAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    season_id: Optional[str] = None
    home_record: Dict[str, Any]
    away_record: Dict[str, Any]
    comparison: HomeAwayComparisonSchema
    calculated_at: str


class AttackingAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    season_id: Optional[str] = None
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
    total_assists: Optional[int] = None
    big_chances_created: Optional[int] = None
    big_chances_missed: Optional[int] = None
    half_breakdown: Dict[str, Any]
    goals_by_competition_phase: Dict[str, Any] = {}
    goals_by_match: List[Dict[str, Any]] = []
    goals_by_player: List[Dict[str, Any]] = []
    top_contributors: List[Dict[str, Any]]
    data_coverage: DataCoverageSchema
    calculated_at: Optional[str] = None


class DefensiveAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    season_id: Optional[str] = None
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
    defensive_by_match: List[Dict[str, Any]] = []
    data_coverage: DataCoverageSchema
    calculated_at: Optional[str] = None


class PassingByMatchSchema(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    opponent_name: str
    opponent_short: str
    is_home: bool
    passes_total: Optional[int] = None
    passes_completed: Optional[int] = None
    failed_passes: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    possession_pct: Optional[float] = None


class PassingAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    season_id: Optional[str] = None
    matches_analyzed: int
    total_passes: Optional[int] = None
    successful_passes: Optional[int] = None
    failed_passes: Optional[int] = None
    passing_accuracy_pct: Optional[float] = None
    average_possession_pct: Optional[float] = None
    passing_by_match: List[PassingByMatchSchema] = []
    data_coverage: DataCoverageSchema
    calculated_at: str


class MatchTrendItemSchema(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    date: str
    opponent_name: str
    opponent_short: str
    is_home: bool
    score: str
    outcome: str
    points: int
    goals_for: int
    goals_against: int


class PointsProgressionItemSchema(BaseSchema):
    match_number: Optional[int] = None
    date: str
    opponent: str
    points_earned: int
    cumulative_points: int


class RollingTrendItemSchema(BaseSchema):
    match_number: Optional[int] = None
    match_id: str
    date: str
    rolling_goals_for_avg: Optional[float] = None
    rolling_goals_against_avg: Optional[float] = None
    rolling_points_per_match: Optional[float] = None


class PerformanceTrendsResponse(BaseSchema):
    team_id: str
    team_name: str
    season_id: Optional[str] = None
    matches_analyzed: int
    last_five_matches: List[MatchTrendItemSchema] = []
    match_by_match_results: List[MatchTrendItemSchema] = []
    monthly_goals_scored: Dict[str, int] = {}
    monthly_goals_conceded: Dict[str, int] = {}
    points_progression: List[PointsProgressionItemSchema] = []
    rolling_trends: List[RollingTrendItemSchema] = []
    data_coverage: DataCoverageSchema
    calculated_at: str


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
    rankings: Optional[Dict[str, Any]] = None
    last_five_matches: List[Dict[str, Any]] = []
    data_provenance: Optional[Dict[str, Any]] = None
    is_leadership_group: bool = False
    leadership_role: Optional[str] = None


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
    match_number: Optional[int] = None
    opponent_name: Optional[str] = None
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
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    match_metadata: Optional[Dict[str, Any]] = None
    data_available: bool = True
    coverage_status: str = "VERIFIED_EVENTS"
    telemetry_disclosure: Optional[str] = None
    total_shots: int
    shots_on_target: Optional[int] = None
    shots_off_target: Optional[int] = None
    blocked_shots: Optional[int] = None
    goals: int
    conversion_rate_pct: Optional[float] = None
    expected_goals_total: Optional[float] = None
    xg_per_shot: Optional[float] = None
    pitch_dimensions: Dict[str, float]
    shot_distribution: Optional[Dict[str, Any]] = None
    shots: List[ShotEventSchema]


class PassingNetworkNode(BaseSchema):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    avg_x: float
    avg_y: float
    touches: int
    passes_made: Optional[int] = None
    passes_received: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    in_degree: Optional[int] = None
    out_degree: Optional[int] = None
    weighted_degree: Optional[int] = None
    degree_centrality: Optional[float] = None


class PassingNetworkEdge(BaseSchema):
    passer_id: Optional[str] = None
    passer_name: Optional[str] = None
    recipient_id: Optional[str] = None
    recipient_name: Optional[str] = None
    pass_count: int


class SelectedPlayerTacticalSummary(BaseSchema):
    player_id: str
    player_name: str
    position: str
    jersey_number: int
    passes_made: int
    passes_received: int
    pass_accuracy_pct: float
    connected_edges_count: int


class PassingNetworkResponse(BaseSchema):
    nodes_count: int
    edges_count: int
    network_density: Optional[float] = None
    degree_centrality: Optional[Dict[str, float]] = None
    period: Optional[str] = "FULL_MATCH"
    data_available: bool = True
    coverage_status: Optional[str] = None
    message: Optional[str] = None
    selected_player: Optional[SelectedPlayerTacticalSummary] = None
    nodes: List[PassingNetworkNode]
    edges: List[PassingNetworkEdge]


# -----------------------------------------------------------------------------
# Player Analytics Extended Schemas
# -----------------------------------------------------------------------------

class PlayerMatchLogSchema(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    kickoff: str
    opponent_name: str
    opponent_short: str
    is_home: bool
    started: bool
    minutes_played: int
    goals: int
    assists: int
    shots: Optional[int] = None
    passes_completed: Optional[int] = None
    tackles: Optional[int] = None
    yellow_cards: int
    red_cards: int
    clean_sheet: Optional[bool] = None
    score: str


class PlayerListItemSchema(BaseSchema):
    player_id: str
    slug: str
    name: str
    jersey_number: Optional[int] = None
    primary_position: str
    nationality: str
    appearances: int
    starts: int
    substitute_appearances: int
    minutes_played: int
    goals: int
    assists: int
    goal_contributions: int
    shots_total: Optional[int] = None
    shots_on_target: Optional[int] = None
    passes_completed: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    tackles_total: Optional[int] = None
    tackles_won: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    saves: Optional[int] = None
    clean_sheets: Optional[int] = None
    goals_per_90: Optional[float] = None
    assists_per_90: Optional[float] = None
    goal_contributions_per_90: Optional[float] = None
    shots_per_90: Optional[float] = None
    passes_completed_per_90: Optional[float] = None
    tackles_per_90: Optional[float] = None
    squad_rank_goals: Optional[int] = None
    squad_rank_minutes: Optional[int] = None


class PlayerListAnalyticsResponse(BaseSchema):
    total_players: int
    active_players: int
    filter_position: Optional[str] = None
    min_minutes_filter: int = 0
    players: List[PlayerListItemSchema]


class PlayerMatchHistoryResponse(BaseSchema):
    player_id: str
    player_name: str
    primary_position: str
    total_appearances: int
    total_minutes: int
    matches: List[PlayerMatchLogSchema]


# -----------------------------------------------------------------------------
# Expected Goals (xG) Schemas
# -----------------------------------------------------------------------------

class XgPlayerItem(BaseSchema):
    player_name: str
    squad_number: Optional[int] = None
    shots: int
    goals: int
    expected_goals: float
    xg_difference: float
    conversion_rate_pct: Optional[float] = None
    xg_per_shot: Optional[float] = None


class XgMatchItem(BaseSchema):
    match_id: str
    match_number: int
    date: Optional[str] = None
    opponent_name: str
    opponent_short: Optional[str] = None
    venue: Optional[str] = None
    is_home: Optional[bool] = None
    goals: int
    goals_conceded: Optional[int] = None
    result: Optional[str] = None
    expected_goals: float
    opponent_expected_goals: Optional[float] = None
    xg_difference: Optional[float] = None
    shots: int
    shots_on_target: Optional[int] = None
    shots_off_target: Optional[int] = None
    blocked_shots: Optional[int] = None
    opponent_shots: Optional[int] = None
    opponent_shots_on_target: Optional[int] = None
    opponent_shots_off_target: Optional[int] = None
    opponent_blocked_shots: Optional[int] = None
    conversion_rate_pct: Optional[float] = None
    has_shot_coordinates: bool = True


class XgOverviewResponse(BaseSchema):
    team_name: str = "Chennaiyin FC"
    total_shots: int
    total_goals: int
    total_xg: float
    xg_difference: float
    conversion_rate_pct: Optional[float] = None
    xg_per_shot: Optional[float] = None
    methodology: str = "Documented Baseline Logistic Regression: logit = -1.50 - (0.10 * distance) + (1.25 * angle_rad)"
    shot_distribution: Optional[Dict[str, Any]] = None
    players_xg: List[XgPlayerItem]
    matches_xg: List[XgMatchItem]


# -----------------------------------------------------------------------------
# Opposition & Match Comparison Schemas
# -----------------------------------------------------------------------------

class OppositionMatchItem(BaseSchema):
    match_id: str
    match_number: int
    kickoff: str
    is_home: bool
    cfc_score: Optional[int] = None
    opponent_score: Optional[int] = None
    outcome: Optional[str] = None
    status: str


class OppositionH2HSchema(BaseSchema):
    matches_played: int
    cfc_wins: int
    draws: int
    opponent_wins: int
    cfc_goals: int
    opponent_goals: int
    clean_sheets: int


class OppositionAnalysisResponse(BaseSchema):
    opponent_id: str
    opponent_name: str
    short_name: str
    slug: str
    head_to_head: OppositionH2HSchema
    completed_fixtures: List[OppositionMatchItem]
    upcoming_fixtures: List[OppositionMatchItem]
    tactical_profile: Dict[str, Any]


class MatchCompareMetricItem(BaseSchema):
    metric_name: str
    label: str
    match_a_value: Any
    match_b_value: Any
    delta: Any
    unit: Optional[str] = None


class MatchCompareResponse(BaseSchema):
    match_a: Dict[str, Any]
    match_b: Dict[str, Any]
    comparisons: List[MatchCompareMetricItem]


# -----------------------------------------------------------------------------
# Territorial Dominance & Build-up Metrics Schemas
# -----------------------------------------------------------------------------

class TerritorialFinalThirdSchema(BaseSchema):
    chennaiyin_fc: int
    opponent: int
    total: int


class TerritorialProgressivePassesSchema(BaseSchema):
    count: int
    definition: str


class TerritorialNetworkDensitySchema(BaseSchema):
    value: float
    status: str
    definition: str
    observed_links: int
    possible_links: int


class TerritorialMetricsResponse(BaseSchema):
    match_id: Optional[str] = None
    season_id: Optional[str] = None
    field_tilt_pct: float
    field_tilt_status: str
    field_tilt_description: str
    field_tilt_calculation: str
    final_third_passes: TerritorialFinalThirdSchema
    progressive_passes: TerritorialProgressivePassesSchema
    network_density: TerritorialNetworkDensitySchema
    source_verified: bool = True


class MatchTacticalBreakdownResponse(BaseSchema):
    match_id: str
    match_number: Optional[int] = None
    opponent_name: str
    score: str
    is_home: bool
    formation: str
    territorial: TerritorialMetricsResponse
    passing_network: PassingNetworkResponse
    shot_efficiency: Dict[str, Any]
    defensive_resilience: Dict[str, Any]


# -----------------------------------------------------------------------------
# Defensive Actions & Heatmap Schemas
# -----------------------------------------------------------------------------

class DefensiveActionMarkerSchema(BaseSchema):
    id: str
    player_name: str
    minute: int
    action_type: str
    x: float
    y: float
    outcome: str


class DefensiveActionsResponse(BaseSchema):
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    total_actions: int
    tackles: int
    interceptions: int
    clearances: int
    blocks: int
    recoveries: int
    spatial_coverage: str = "VERIFIED_EVENTS"
    actions: List[DefensiveActionMarkerSchema]


class HeatmapLegendSchema(BaseSchema):
    low: str
    moderate: str
    high: str


class HeatmapZoneSchema(BaseSchema):
    x: float
    y: float
    intensity: float


class HeatmapResponse(BaseSchema):
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    data_available: bool = False
    coverage_status: str = "DATA_UNAVAILABLE"
    message: str
    legend: HeatmapLegendSchema
    zones: List[HeatmapZoneSchema] = []


# V3 Platform Reorganisation & Intelligence Schemas

class AverageLineupStarterSchema(BaseSchema):
    player_id: str
    name: str
    jersey_number: Optional[int] = None
    tactical_position: str
    registered_position: str
    matches_included: int
    starts: int
    sub_appearances: int
    total_appearances: int
    minutes_played: int
    start_rate_pct: float
    x: float
    y: float


class AverageLineupSubstituteSchema(BaseSchema):
    player_id: str
    name: str
    jersey_number: Optional[int] = None
    position: str
    sub_appearances: int
    sub_minutes: int
    starts: int
    total_appearances: int
    total_minutes: int


class AverageLineupResponse(BaseSchema):
    team_id: str
    team_name: str
    matches_analyzed: int
    formation: str
    formation_breakdown: Dict[str, int]
    starters: List[AverageLineupStarterSchema]
    substitutes: List[AverageLineupSubstituteSchema]
    verification_status: str
    confidence_score: float


class SubstitutePerformerSchema(BaseSchema):
    player_id: str
    name: str
    jersey_number: Optional[int] = None
    position: str
    starts: int
    sub_appearances: int
    total_appearances: int
    unused_bench_appearances: int
    starter_minutes: int
    sub_minutes: int
    total_minutes: int
    starter_goals: int
    sub_goals: int
    total_goals: int
    starter_assists: int
    sub_assists: int
    total_assists: int
    yellow_cards: int
    red_cards: int
    per_90_sub_goals: Optional[float] = None
    per_90_sub_assists: Optional[float] = None
    impact_score: float


class StarterVsSubSummarySchema(BaseSchema):
    starter_minutes: int
    sub_minutes: int
    sub_minute_percentage: float
    starter_goals: int
    sub_goals: int
    starter_goals_per_90: float
    sub_goals_per_90: float
    total_substitutions_made: int
    avg_substitutions_per_match: float
    most_common_sub_window: str


class MatchSubstitutionLogSchema(BaseSchema):
    match_number: int
    opponent: str
    is_home: bool
    sub_in_minute: Optional[int] = None
    minutes_played: int
    player_in: str
    player_in_id: str
    jersey_number: Optional[int] = None
    player_out: str
    player_out_id: Optional[str] = None
    score_at_sub: str
    score_at_ft: str
    impact_label: str


class SubstituteAnalyticsResponse(BaseSchema):
    team_id: str
    team_name: str
    matches_analyzed: int
    total_squad_players: int
    active_substitutes_count: int
    substitute_performers: List[SubstitutePerformerSchema]
    starter_vs_sub_summary: StarterVsSubSummarySchema
    match_substitution_log: List[MatchSubstitutionLogSchema]
    bench_rules_applied: Dict[str, bool]


class PlayerDefensiveLeaderboardSchema(BaseSchema):
    player_id: Optional[str] = None
    player_name: str
    jersey_number: Optional[int] = None
    position: str
    nationality: Optional[str] = "India"
    is_indian: Optional[bool] = True
    tackles_total: int
    tackles_won: int
    tackle_success_pct: Optional[float] = None
    interceptions: int
    clearances: int
    blocks: int
    recoveries: int
    aerial_duels_won: Optional[int] = None
    aerial_duels_total: Optional[int] = None
    ground_duels_won: Optional[int] = None
    ground_duels_attempted: Optional[int] = None
    defensive_errors: Optional[int] = None
    fouls_committed: int
    yellow_cards: int
    red_cards: int
    minutes_played: int
    appearances: int
    starts: int
    has_sufficient_minutes: bool = False
    tackles_per_90: Optional[float] = None
    interceptions_per_90: Optional[float] = None
    clearances_per_90: Optional[float] = None
    blocks_per_90: Optional[float] = None
    recoveries_per_90: Optional[float] = None
    total_defensive_actions: int
    actions_per_90: Optional[float] = None
    coverage_status: str


class TeamDefensiveKpisSchema(BaseSchema):
    matches_played: int
    goals_conceded: int
    goals_conceded_per_match: float
    clean_sheets: int
    clean_sheet_percentage: float
    tackles_total: int
    tackles_won: int
    tackle_success_pct: float
    interceptions: int
    clearances: int
    blocked_shots: int
    recoveries: int
    total_defensive_actions: int
    actions_per_match: float
    saves: int
    fouls_committed: int
    yellow_cards: int
    red_cards: int
    discipline_index: int
    opponent_shots: Optional[int] = None
    opponent_shots_on_target: Optional[int] = None
    opponent_expected_goals: Optional[float] = None
    opponent_shots_per_match: Optional[float] = None
    aerial_duels_attempted: Optional[int] = None
    aerial_duels_won: Optional[int] = None
    ground_duels_attempted: Optional[int] = None
    ground_duels_won: Optional[int] = None
    defensive_errors: Optional[int] = None


class DefensiveIntelligenceResponse(BaseSchema):
    team_id: str
    team_name: str
    matches_analyzed: int
    team_defensive_kpis: TeamDefensiveKpisSchema
    matches_defensive: Optional[List[Dict[str, Any]]] = None
    player_leaderboard: List[PlayerDefensiveLeaderboardSchema]
    spatial_defensive_actions: List[Dict[str, Any]]
    telemetry_provenance: Dict[str, Any]


class SquadCoveragePlayerSchema(BaseSchema):
    player_id: str
    name: str
    squad_number: Optional[int] = None
    position: str
    nationality: str
    starts: int
    sub_appearances: int
    total_appearances: int
    unused_bench_appearances: int
    total_minutes: int
    status_label: str
    coverage_matrix: Dict[str, str]
    verified_metrics: Dict[str, Optional[int]]


class SquadCoverageAuditResponse(BaseSchema):
    total_squad_players: int
    matches_analyzed: int
    summary_breakdown: Dict[str, Any]
    players: List[SquadCoveragePlayerSchema]
    data_rules: List[str]


class AIAnalystQueryRequest(BaseSchema):
    query: str


class AIAnalystDossierResponse(BaseSchema):
    query: str
    archetype: str
    title: str
    executive_summary: str = ""
    key_statistics: List[Dict[str, Any]] = []
    performance_evidence: List[str] = []
    football_interpretation: str = ""
    limitations: List[str] = []
    final_assessment: str = ""
    verified_facts: List[str] = []
    calculated_metrics: Dict[str, Any] = {}
    interpretation: str = ""
    unavailable_data: List[str] = []
