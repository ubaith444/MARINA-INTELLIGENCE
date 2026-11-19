/**
 * MARINA INTELLIGENCE — Domain Types & Data Contracts
 * Mirroring FastAPI Pydantic Schemas for Chennaiyin FC & ISL 2026–27
 */

export type MatchStatus =
  | "SCHEDULED"
  | "TIMED"
  | "IN_PLAY"
  | "PAUSED"
  | "FINISHED"
  | "POSTPONED"
  | "SUSPENDED"
  | "CANCELLED";

export type EventType =
  | "GOAL"
  | "PENALTY_GOAL"
  | "OWN_GOAL"
  | "SHOT"
  | "SHOT_ON_TARGET"
  | "SAVE"
  | "YELLOW_CARD"
  | "RED_CARD"
  | "SECOND_YELLOW"
  | "SUBSTITUTION"
  | "FOUL"
  | "OFFSIDE"
  | "CORNER"
  | "PENALTY_AWARDED"
  | "VAR_DECISION";

export type PlayerPosition =
  | "GOALKEEPER"
  | "CENTRE_BACK"
  | "LEFT_BACK"
  | "RIGHT_BACK"
  | "LEFT_WING_BACK"
  | "RIGHT_WING_BACK"
  | "DEFENSIVE_MIDFIELDER"
  | "CENTRAL_MIDFIELDER"
  | "ATTACKING_MIDFIELDER"
  | "LEFT_MIDFIELDER"
  | "RIGHT_MIDFIELDER"
  | "LEFT_WINGER"
  | "RIGHT_WINGER"
  | "STRIKER"
  | "CENTRE_FORWARD";

export interface Competition {
  id: string;
  code: string;
  name: string;
  country: string;
  federation: string;
  tier: number;
  competition_type: string;
  is_active: boolean;
}

export interface Season {
  id: string;
  competition_id: string;
  name: string;
  slug: string;
  start_date?: string | null;
  end_date?: string | null;
  is_current: boolean;
  competition?: Competition;
}

export interface Venue {
  id: string;
  name: string;
  city: string;
  state?: string | null;
  capacity?: number | null;
  surface_type?: string | null;
}

export interface Team {
  id: string;
  name: string;
  short_name: string;
  slug: string;
  founded_year?: number | null;
  city?: string | null;
  primary_venue_id?: string | null;
  primary_venue?: Venue | null;
  primary_color?: string | null;
  secondary_color?: string | null;
}

export interface Player {
  id: string;
  slug: string;
  first_name: string;
  last_name: string;
  known_name?: string | null;
  date_of_birth?: string | null;
  nationality: string;
  primary_position?: PlayerPosition | string | null;
  secondary_position?: PlayerPosition | string | null;
  preferred_foot?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  is_active: boolean;
  jersey_number?: number | null;
  is_leadership_group?: boolean;
  leadership_role?: string | null;
}

export interface SquadRegistration {
  id: string;
  team_id: string;
  season_id: string;
  player_id: string;
  jersey_number?: number | null;
  squad_status: string;
  registered_at: string;
  player?: Player;
  team?: Team;
}

export interface MatchEvent {
  id: string;
  minute: number;
  stoppage_minute?: number | null;
  period: string;
  event_type: EventType | string;
  team_id?: string | null;
  primary_player_id?: string | null;
  secondary_player_id?: string | null;
  description?: string | null;
  primary_player?: Player | null;
  secondary_player?: Player | null;
}

export interface Lineup {
  id: string;
  team_id: string;
  player_id: string;
  lineup_role: "STARTER" | "BENCH" | "RESERVE";
  position_assigned?: string | null;
  position?: string | null;
  tactical_formation?: string | null;
  jersey_number?: number | null;
  is_captain: boolean;
  minutes_played?: number | null;
  is_substitute_in: boolean;
  sub_in_minute?: number | null;
  sub_out_minute?: number | null;
  player?: Player | null;
}

export interface TeamMatchStats {
  possession_pct?: number | null;
  shots_total?: number | null;
  shots_on_target?: number | null;
  shots_off_target?: number | null;
  blocked_shots?: number | null;
  expected_goals?: number | null;
  shooting_accuracy_pct?: number | null;
  passes_total?: number | null;
  passes_completed?: number | null;
  pass_accuracy_pct?: number | null;
  tackles_total?: number | null;
  tackles_won?: number | null;
  interceptions?: number | null;
  clearances?: number | null;
  corners?: number | null;
  fouls_committed?: number | null;
  yellow_cards?: number | null;
  red_cards?: number | null;
  saves?: number | null;
}

export interface Match {
  id: string;
  season_id: string;
  home_team_id: string;
  away_team_id: string;
  venue_id?: string | null;
  scheduled_kickoff?: string | null;
  actual_kickoff?: string | null;
  match_status: MatchStatus;
  match_number?: number | null;
  matchweek?: number | null;
  fixture_leg?: "FIRST_LEG" | "SECOND_LEG" | string | null;
  publication_status?: "PUBLISHED" | "PROVISIONAL" | string;
  verification_status?: "PUBLISHED" | "PROVISIONAL" | "DISCREPANCY_FLAGGED" | "PENDING" | "VERIFIED" | string;
  venue_verification_status?: "CONFIRMED" | "INFERRED" | "TBC" | string | null;
  has_discrepancy?: boolean;
  discrepancy_notes?: string | null;
  source_url?: string | null;
  last_verified_at?: string | null;
  kickoff_time_ist?: string | null;
  home_score?: number | null;
  away_score?: number | null;
  half_time_home_score?: number | null;
  half_time_away_score?: number | null;
  attendance?: number | null;
  referee?: string | null;
  home_team: Team;
  away_team: Team;
  venue?: Venue | null;
  events?: MatchEvent[];
  lineups?: Lineup[];
  team_statistics?: any[];
}

export interface FixtureImportResponse {
  batch_id: string;
  season_id: string;
  total_processed: number;
  published_count: number;
  provisional_count: number;
  discrepancies_flagged: number;
  new_created: number;
  updated: number;
  status: string;
  message: string;
  timestamp: string;
}

export interface VenuePerformanceRecord {
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  clean_sheets: number;
  win_percentage?: number | null;
}

export interface RecentFormMatch {
  match_id: string;
  match_number?: number | null;
  kickoff: string;
  opponent_name: string;
  opponent_short: string;
  is_home: boolean;
  score: string;
  outcome: string;
  points: number;
}

export interface RecentForm {
  sequence: string[];
  sequence_str: string;
  form_points: number;
  form_ppm?: number | null;
  matches?: RecentFormMatch[];
}

export interface TeamSeasonPerformance {
  team_id: string;
  team_name: string;
  short_name?: string;
  season_id?: string;
  season_name?: string;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  points_per_match?: number | null;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  goals_for_per_match?: number | null;
  goals_against_per_match?: number | null;
  goals_per_match?: number | null;
  goals_conceded_per_match?: number | null;
  clean_sheets: number;
  clean_sheet_percentage?: number | null;
  win_percentage?: number | null;
  home_record: VenuePerformanceRecord;
  away_record: VenuePerformanceRecord;
  recent_form: RecentForm | string[];
  data_coverage?: any;
}

export interface AttackingAnalytics {
  team_id: string;
  team_name: string;
  matches_analyzed: number;
  goals_scored: number;
  goals_per_match?: number | null;
  shots_total: number;
  shots_per_match?: number | null;
  shots_on_target: number;
  shots_off_target: number;
  blocked_shots: number;
  shooting_accuracy_pct?: number | null;
  conversion_rate_pct?: number | null;
  expected_goals?: number | null;
  expected_goals_per_match?: number | null;
  shot_efficiency?: number | null;
  big_chances_created?: number | null;
  big_chances_missed?: number | null;
  half_breakdown: {
    first_half_goals: number;
    second_half_goals: number;
    first_half_pct?: number | null;
    second_half_pct?: number | null;
  };
  top_contributors: Array<{
    player_id: string;
    player_name: string;
    goals: number;
    assists: number;
    goal_contributions: number;
  }>;
}

export interface DefensiveAnalytics {
  team_id: string;
  team_name: string;
  matches_analyzed: number;
  goals_conceded: number;
  goals_conceded_per_match?: number | null;
  clean_sheets: number;
  clean_sheet_percentage?: number | null;
  expected_goals_conceded?: number | null;
  expected_goals_conceded_per_match?: number | null;
  tackles_total?: number | null;
  tackles_won?: number | null;
  tackle_success_pct?: number | null;
  interceptions?: number | null;
  clearances?: number | null;
  saves?: number | null;
  blocked_shots?: number | null;
  total_defensive_actions?: number | null;
  defensive_actions_per_match?: number | null;
  fouls_committed?: number | null;
  yellow_cards: number;
  red_cards: number;
  discipline_index: number;
}

export interface PlayerPerformance {
  player_id: string;
  slug: string;
  name: string;
  primary_position: string;
  nationality: string;
  is_indian?: boolean;
  is_leadership_group?: boolean;
  leadership_role?: string | null;
  appearances: number;
  starts: number;
  substitute_appearances: number;
  minutes_played: number;
  raw_totals: {
    goals: number;
    assists: number;
    goal_contributions: number;
    shots_total?: number | null;
    shots_on_target?: number | null;
    expected_goals?: number | null;
    expected_assists?: number | null;
    key_passes?: number | null;
    passes_total?: number | null;
    passes_completed?: number | null;
    pass_accuracy_pct?: number | null;
    tackles_total?: number | null;
    tackles_won?: number | null;
    tackle_success_pct?: number | null;
    interceptions?: number | null;
    clearances?: number | null;
    blocks?: number | null;
    yellow_cards?: number;
    red_cards?: number;
    fouls_committed?: number | null;
    saves?: number | null;
    goals_conceded?: number | null;
    clean_sheets?: number | null;
    save_percentage?: number | null;
    distance_covered_km?: number | null;
  };
  per_90: {
    has_sufficient_minutes: boolean;
    min_minutes_threshold: number;
    goals_per_90?: number | null;
    assists_per_90?: number | null;
    goal_contributions_per_90?: number | null;
    shots_per_90?: number | null;
    shots_on_target_per_90?: number | null;
    expected_goals_per_90?: number | null;
    expected_assists_per_90?: number | null;
    passes_completed_per_90?: number | null;
    tackles_per_90?: number | null;
    interceptions_per_90?: number | null;
  };
  rankings?: Record<string, { rank: number; total: number; percentile?: number }> | null;
  last_five_matches?: PlayerMatchLog[];
  data_provenance?: {
    data_source: string;
    verification_status: string;
    matches_logged: number;
    has_optical_tracking: boolean;
    has_event_data: boolean;
    audit_timestamp: string;
  };
}

export interface PlayerMatchLog {
  match_id: string;
  match_number?: number | null;
  kickoff: string;
  opponent_name: string;
  opponent_short: string;
  is_home: boolean;
  started: boolean;
  minutes_played: number;
  goals: number;
  assists: number;
  shots?: number | null;
  passes_completed?: number | null;
  tackles?: number | null;
  yellow_cards: number;
  red_cards: number;
  clean_sheet?: boolean | null;
  score: string;
}

export interface PlayerListAnalyticsItem {
  player_id: string;
  slug: string;
  name: string;
  jersey_number?: number | null;
  primary_position: string;
  nationality: string;
  is_indian?: boolean;
  appearances: number;
  starts: number;
  substitute_appearances: number;
  minutes_played: number;
  goals: number;
  assists: number;
  goal_contributions: number;
  shots_total?: number | null;
  shots_on_target?: number | null;
  passes_completed?: number | null;
  pass_accuracy_pct?: number | null;
  tackles_total?: number | null;
  tackles_won?: number | null;
  interceptions?: number | null;
  clearances?: number | null;
  saves?: number | null;
  clean_sheets?: number | null;
  goals_per_90?: number | null;
  assists_per_90?: number | null;
  goal_contributions_per_90?: number | null;
  shots_per_90?: number | null;
  passes_completed_per_90?: number | null;
  tackles_per_90?: number | null;
  squad_rank_goals?: number | null;
  squad_rank_minutes?: number | null;
}

export interface PlayerListAnalyticsResponse {
  total_players: number;
  active_players: number;
  filter_position?: string | null;
  min_minutes_filter: number;
  players: PlayerListAnalyticsItem[];
}

export interface PlayerMatchHistoryResponse {
  player_id: string;
  player_name: string;
  primary_position: string;
  total_appearances: number;
  total_minutes: number;
  matches: PlayerMatchLog[];
}

export interface XgPlayerItem {
  player_name: string;
  squad_number?: number | null;
  shots: number;
  goals: number;
  expected_goals: number;
  xg_difference: number;
  conversion_rate_pct?: number | null;
  xg_per_shot?: number | null;
}

export interface XgMatchItem {
  match_id: string;
  match_number: number;
  date?: string | null;
  opponent_name: string;
  opponent_short?: string | null;
  venue?: string | null;
  is_home?: boolean | null;
  goals: number;
  goals_conceded?: number | null;
  result?: string | null;
  expected_goals: number;
  opponent_expected_goals?: number | null;
  xg_difference?: number | null;
  shots: number;
  shots_on_target?: number | null;
  shots_off_target?: number | null;
  blocked_shots?: number | null;
  opponent_shots?: number | null;
  opponent_shots_on_target?: number | null;
  opponent_shots_off_target?: number | null;
  opponent_blocked_shots?: number | null;
  conversion_rate_pct?: number | null;
  has_shot_coordinates?: boolean;
}

export interface XgOverviewResponse {
  team_name: string;
  total_shots: number;
  total_goals: number;
  total_xg: number;
  xg_difference: number;
  conversion_rate_pct?: number | null;
  xg_per_shot?: number | null;
  methodology: string;
  shot_distribution?: {
    home: {
      matches: number;
      shots: number;
      goals: number;
      expected_goals: number;
      shots_on_target: number;
      shots_off_target: number;
      blocked: number;
      opponent_shots?: number;
      opponent_goals?: number;
      opponent_expected_goals?: number;
      conversion_rate_pct?: number;
    };
    away: {
      matches: number;
      shots: number;
      goals: number;
      expected_goals: number;
      shots_on_target: number;
      shots_off_target: number;
      blocked: number;
      opponent_shots?: number;
      opponent_goals?: number;
      opponent_expected_goals?: number;
      conversion_rate_pct?: number;
    };
  } | null;
  players_xg: XgPlayerItem[];
  matches_xg: XgMatchItem[];
}

export interface OppositionMatchItem {
  match_id: string;
  match_number: number;
  kickoff: string;
  is_home: boolean;
  cfc_score?: number | null;
  opponent_score?: number | null;
  outcome?: string | null;
  status: string;
}

export interface OppositionH2H {
  matches_played: number;
  cfc_wins: number;
  draws: number;
  opponent_wins: number;
  cfc_goals: number;
  opponent_goals: number;
  clean_sheets: number;
}

export interface OppositionAnalysisResponse {
  opponent_id: string;
  opponent_name: string;
  short_name: string;
  slug: string;
  head_to_head: OppositionH2H;
  completed_fixtures: OppositionMatchItem[];
  upcoming_fixtures: OppositionMatchItem[];
  tactical_profile: {
    formation: string;
    tactical_style: string;
    strengths: string[];
    vulnerabilities: string[];
    key_player: string;
    possession_tendency_pct?: number;
    avg_shots_per_game?: number;
  };
}

export interface MatchCompareMetricItem {
  metric_name: string;
  label: string;
  match_a_value: any;
  match_b_value: any;
  delta: any;
  unit?: string | null;
}

export interface MatchCompareResponse {
  match_a: {
    match_id: string;
    match_number: number;
    opponent_name: string;
    opponent_short: string;
    is_home: boolean;
    score: string;
    kickoff: string;
    formation?: string;
    venue?: string;
  };
  match_b: {
    match_id: string;
    match_number: number;
    opponent_name: string;
    opponent_short: string;
    is_home: boolean;
    score: string;
    kickoff: string;
    formation?: string;
    venue?: string;
  };
  comparisons: MatchCompareMetricItem[];
}

export interface MatchTacticalBreakdownResponse {
  match_id: string;
  match_number?: number | null;
  opponent_name: string;
  score: string;
  is_home: boolean;
  formation: string;
  territorial: TerritorialMetrics;
  passing_network: PassingNetwork;
  shot_efficiency: {
    total_shots: number;
    shots_on_target?: number | null;
    goals: number;
    conversion_rate_pct?: number | null;
    expected_goals_total?: number | null;
  };
  defensive_resilience: {
    clean_sheet: boolean;
    goals_conceded: number;
  };
}

export interface RadarComparisonItem {
  dimension: string;
  player_a_score: number;
  player_b_score: number;
}

export interface PlayerCompareResponse {
  player_a: PlayerPerformance;
  player_b: PlayerPerformance;
  radar_comparison: RadarComparisonItem[];
}

export interface MatchTacticalReport {
  match_id: string;
  match_number?: number | null;
  match_status: string;
  kickoff: string;
  venue: string;
  attendance?: number | null;
  referee?: string | null;
  home_team: {
    id: string;
    name: string;
    short_name: string;
    score?: number | null;
    statistics: TeamMatchStats;
  };
  away_team: {
    id: string;
    name: string;
    short_name: string;
    score?: number | null;
    statistics: TeamMatchStats;
  };
  half_by_half: {
    first_half: {
      score: string;
      home_goals: number;
      away_goals: number;
      events_count: number;
    };
    second_half: {
      score: string;
      home_goals: number;
      away_goals: number;
      events_count: number;
    };
  };
  timeline: Array<{
    minute: number;
    stoppage_minute?: number | null;
    period: string;
    event_type: string;
    team_name: string;
    primary_player?: string | null;
    secondary_player?: string | null;
    description?: string | null;
  }>;
}

export interface PassingNetworkNode {
  player_id: string;
  player_name: string;
  jersey_number?: number | null;
  position?: string | null;
  avg_x: number;
  avg_y: number;
  touches: number;
  passes_made?: number | null;
  passes_received?: number | null;
  pass_accuracy_pct?: number | null;
  in_degree?: number | null;
  out_degree?: number | null;
  weighted_degree?: number | null;
  degree_centrality?: number | null;
}

export interface PassingNetworkEdge {
  passer_id: string;
  passer_name: string;
  recipient_id: string;
  recipient_name: string;
  pass_count: number;
}

export interface SelectedPlayerTacticalSummary {
  player_id: string;
  player_name: string;
  position: string;
  jersey_number: number;
  passes_made: number;
  passes_received: number;
  pass_accuracy_pct: number;
  connected_edges_count: number;
}

export interface PassingNetwork {
  nodes_count: number;
  edges_count: number;
  network_density?: number | null;
  directed_density?: number | null;
  degree_centrality?: Record<string, number> | null;
  period?: string | null;
  data_available?: boolean;
  coverage_status?: string | null;
  message?: string | null;
  selected_player?: SelectedPlayerTacticalSummary | null;
  nodes: PassingNetworkNode[];
  edges: PassingNetworkEdge[];
}

export interface ShotEvent {
  shot_id: string;
  match_number?: number | null;
  opponent_name?: string | null;
  minute: number;
  player_name: string;
  team_name: string;
  x: number;
  y: number;
  distance_meters: number;
  angle_degrees: number;
  outcome: "GOAL" | "SAVED" | "MISSED" | "BLOCKED" | string;
  expected_goals?: number | null;
  body_part?: string | null;
}

export interface ShotMap {
  match_id?: string | null;
  player_id?: string | null;
  player_name?: string | null;
  match_metadata?: {
    match_id: string;
    match_number: number;
    date?: string | null;
    competition: string;
    venue: string;
    home_team: string;
    away_team: string;
    opponent_name: string;
    opponent_short: string;
    is_home: boolean;
    cfc_score?: number | null;
    opponent_score?: number | null;
    result?: string | null;
    match_status: string;
  } | null;
  data_available?: boolean;
  coverage_status?: string;
  telemetry_disclosure?: string | null;
  total_shots: number;
  shots_on_target?: number | null;
  shots_off_target?: number | null;
  blocked_shots?: number | null;
  goals: number;
  conversion_rate_pct?: number | null;
  expected_goals_total?: number | null;
  xg_per_shot?: number | null;
  pitch_dimensions: {
    length: number;
    width: number;
  };
  shot_distribution?: {
    home: any;
    away: any;
  } | null;
  shots: ShotEvent[];
}

export interface TerritorialFinalThird {
  chennaiyin_fc: number;
  opponent: number;
  total: number;
}

export interface TerritorialProgressivePasses {
  count: number;
  definition: string;
}

export interface TerritorialNetworkDensity {
  value: number;
  status: string;
  definition: string;
  observed_links: number;
  possible_links: number;
}

export interface TerritorialMetrics {
  match_id?: string | null;
  season_id?: string | null;
  field_tilt_pct: number;
  field_tilt_status: string;
  field_tilt_description: string;
  field_tilt_calculation: string;
  final_third_passes: TerritorialFinalThird;
  progressive_passes: TerritorialProgressivePasses;
  network_density: TerritorialNetworkDensity;
  source_verified: boolean;
}

export interface DefensiveActionMarker {
  id: string;
  player_name: string;
  minute: number;
  action_type: "TACKLE_WON" | "TACKLE_LOST" | "INTERCEPTION" | "CLEARANCE" | "BLOCK" | "RECOVERY" | string;
  x: number;
  y: number;
  outcome: string;
}

export interface DefensiveActionsResponse {
  match_id?: string | null;
  player_id?: string | null;
  player_name?: string | null;
  total_actions: number;
  tackles: number;
  interceptions: number;
  clearances: number;
  blocks: number;
  recoveries: number;
  spatial_coverage: string;
  actions: DefensiveActionMarker[];
}

export interface HeatmapZone {
  x: number;
  y: number;
  intensity: number;
}

export interface HeatmapResponse {
  match_id?: string | null;
  player_id?: string | null;
  player_name?: string | null;
  data_available: boolean;
  coverage_status: string;
  message: string;
  legend: {
    low: string;
    moderate: string;
    high: string;
  };
  zones: HeatmapZone[];
}

export type PitchMode =
  | "FORMATION"
  | "PASSING NETWORK"
  | "SHOT MAP"
  | "DEFENSIVE ACTIONS"
  | "HEATMAP";

export type PitchView = "FULL" | "HALF";

export interface PitchPlayerMarker {
  id: string;
  name: string;
  jersey_number?: number | string;
  position: string;
  x: number; // 0-100 or metric (0-105)
  y: number; // 0-100 or metric (0-68)
  role?: "STARTER" | "BENCH";
  is_captain?: boolean;
  stats?: Record<string, any>;
}

// -----------------------------------------------------------------------------
// Squad Synchronization & Roster Management Types
// -----------------------------------------------------------------------------

export interface SquadMember {
  id: string;
  player_id: string;
  name: string;
  known_name?: string | null;
  squad_number?: number | null;
  position: string;
  pos_group: "GK" | "DEF" | "MID" | "FWD" | string;
  nationality: string;
  secondary_nationality?: string | null;
  is_domestic: boolean;
  date_of_birth?: string | null;
  age?: number | null;
  height_m?: number | null;
  height_cm?: number | null;
  preferred_foot?: string | null;
  joined_date?: string | null;
  previous_club?: string | null;
  contract_expiry?: string | null;
  market_value_inr?: number | null;
  market_value_original?: string | null;
  is_active: boolean;
}

export interface SquadImportPreviewWarning {
  field?: string;
  player_name?: string;
  warning?: string;
  message?: string;
  level?: "info" | "warning" | "error";
}

export interface SquadImportPreview {
  team_id: string;
  season_id: string;
  batch_id: string;
  total_incoming: number;
  new_players: Record<string, any>[];
  updated_players: Record<string, any>[];
  leaving_players: Record<string, any>[];
  retained_players: Record<string, any>[];
  warnings: SquadImportPreviewWarning[];
  missing_fields_summary: Record<string, number>;
  requires_confirmation: boolean;
}

export interface SquadSyncRequestPayload {
  team_id?: string;
  season_id?: string;
  batch_id?: string;
  players?: Record<string, any>[];
  confirmed: boolean;
  deactivate_absent?: boolean;
}

export interface SquadSyncResponse {
  batch_id: string;
  team_id: string;
  season_id: string;
  total_processed: number;
  new_created: number;
  updated: number;
  deactivated: number;
  retained: number;
  active_squad_count: number;
  status: string;
  message: string;
  timestamp: string;
}

export interface SquadImportHistoryItem {
  id: string;
  batch_id: string;
  team_id: string;
  season_id: string;
  source_name: string;
  total_incoming: number;
  new_players: number;
  updated_players: number;
  deactivated_players: number;
  retained_players: number;
  status: string;
  report_summary?: string | null;
  imported_by?: string | null;
  created_at: string;
}

export interface PlayerUpdatePayload {
  first_name?: string;
  last_name?: string;
  known_name?: string;
  primary_position?: string;
  nationality?: string;
  secondary_nationality?: string;
  preferred_foot?: string;
  height_m?: number;
  squad_number?: number;
  joined_date?: string;
  contract_expiry?: string;
  previous_club?: string;
  market_value_inr?: number;
  market_value_original?: string;
  is_active?: boolean;
}

export interface SeasonOverviewResponse {
  season_id: string;
  season_name: string;
  team_id: string;
  team_name: string;
  short_name: string;
  matches_played: number;
  matches_remaining: number;
  total_fixtures: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  goals_scored: number;
  goals_conceded: number;
  goal_difference: number;
  win_percentage: number;
  points_per_match: number;
  clean_sheets: number;
  failed_to_score: number;
  is_season_active: boolean;
  verification_status: string;
  recent_form: string[];
  calculated_at: string;
}

export interface SeasonFormMatch {
  match_id: string;
  match_number: number;
  date?: string | null;
  opponent_name: string;
  opponent_short_name: string;
  is_home: boolean;
  score_cfc?: number | null;
  score_opponent?: number | null;
  result: "W" | "D" | "L";
}

export interface SeasonFormResponse {
  sequence: string[];
  form_points: number;
  form_ppm: number;
  matches: SeasonFormMatch[];
}

export interface SeasonResultItem {
  match_id: string;
  match_number: number;
  date?: string | null;
  home_team: string;
  away_team: string;
  opponent_name?: string | null;
  opponent_short?: string | null;
  home_score?: number | null;
  away_score?: number | null;
  cfc_score?: number | null;
  opponent_score?: number | null;
  is_home: boolean;
  outcome: "WIN" | "DRAW" | "LOSS";
  venue?: string | null;
  kickoff_time?: string | null;
}

export interface SeasonHomeAwaySplit {
  matches_played: number;
  matches_scheduled: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  goals_scored: number;
  goals_conceded: number;
  goal_difference: number;
  win_percentage: number;
  points_per_match: number;
  clean_sheets: number;
}

export interface SeasonHomeAwayResponse {
  home: SeasonHomeAwaySplit;
  away: SeasonHomeAwaySplit;
}

export interface SeasonScoringResponse {
  total_goals_scored: number;
  total_goals_conceded: number;
  goals_per_match: number;
  goals_conceded_per_match: number;
  home_goals_scored: number;
  home_goals_conceded: number;
  away_goals_scored: number;
  away_goals_conceded: number;
  clean_sheets: number;
  clean_sheet_percentage: number;
  scoring_records_available: boolean;
}

export interface PlayerSeasonStatisticItem {
  player_id: string;
  name: string;
  jersey_number?: number | null;
  position: string;
  primary_position: string;
  nationality: string;
  is_indian?: boolean;
  appearances: number;
  starts: number;
  substitute_appearances?: number;
  minutes_played: number;
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  clean_sheets?: number | null;
  shots_total?: number | null;
  shots_on_target?: number | null;
  passes_total?: number | null;
  passes_completed?: number | null;
  pass_accuracy_pct?: number | null;
  tackles_won?: number | null;
  interceptions?: number | null;
  clearances?: number | null;
  blocks?: number | null;
  saves?: number | null;
  goals_conceded?: number | null;
  save_percentage?: number | null;
  goals_per_90?: number | null;
  assists_per_90?: number | null;
  shots_per_90?: number | null;
  passes_completed_per_90?: number | null;
  tackles_per_90?: number | null;
  has_sufficient_minutes?: boolean;
  is_leadership_group?: boolean;
  leadership_role?: string | null;
}

export interface TopScorerItem {
  player_id: string;
  name: string;
  jersey_number?: number | null;
  position: string;
  goals: number;
  assists: number;
  minutes_played: number;
}

export interface DataQualityCheckItem {
  name: string;
  status: "PASS" | "WARN" | "FAIL";
  message: string;
}

export interface DataQualityResponse {
  total_players: number;
  duplicate_players_count: number;
  total_fixtures: number;
  duplicate_fixtures_count: number;
  scheduled_matches_count: number;
  completed_matches_count: number;
  discrepant_matches_count: number;
  unplayed_matches_with_scores: number;
  finished_matches_without_scores: number;
  orphan_events_count: number;
  season_contamination_detected: boolean;
  data_integrity_score_pct: number;
  checks: DataQualityCheckItem[];
}

export interface DataSyncLogItem {
  id: string;
  sync_type: string;
  provider_name: string;
  status: string;
  matches_synced: number;
  records_updated: number;
  discrepancy_count: number;
  details?: string | null;
  error_message?: string | null;
  duration_ms: number;
  created_at: string;
}

export interface DataVerificationItem {
  id: string;
  match_id?: string | null;
  entity_type: string;
  entity_id?: string | null;
  metric_name: string;
  primary_source: string;
  primary_value?: string | null;
  secondary_source?: string | null;
  secondary_value?: string | null;
  verification_status: string;
  is_disputed: boolean;
  notes?: string | null;
  created_at: string;
}

export interface SyncTriggerResponse {
  status: string;
  matches_synced: number;
  discrepancies_flagged: number;
  records_updated: number;
  duration_ms: number;
  message: string;
}

export interface PlayerMatchHistoryItem {
  match_id: string;
  match_number?: number | null;
  match_date?: string | null;
  match_status: string;
  opponent_name: string;
  opponent_short_name?: string | null;
  is_home: boolean;
  cfc_score?: number | null;
  opponent_score?: number | null;
  result?: "W" | "D" | "L" | null;
  lineup_role: string;
  position?: string | null;
  jersey_number?: number | null;
  is_captain: boolean;
  minutes_played: number;
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  shots_total?: number | null;
  shots_on_target?: number | null;
  passes_total?: number | null;
  passes_completed?: number | null;
  tackles_won?: number | null;
  saves?: number | null;
  goals_conceded?: number | null;
  clean_sheet?: boolean | null;
}

export interface PlayerMatchDetailItem {
  player_id: string;
  name: string;
  jersey_number?: number | null;
  position?: string | null;
  lineup_role: "STARTER" | "SUBSTITUTE" | string;
  is_captain: boolean;
  minutes_played?: number | null;
  sub_in_minute?: number | null;
  sub_out_minute?: number | null;
  replaced_player_id?: string | null;
  replaced_player_name?: string | null;
  tactical_formation?: string | null;
  goals?: number | null;
  assists?: number | null;
  shots_total?: number | null;
  shots_on_target?: number | null;
  passes_total?: number | null;
  passes_completed?: number | null;
  pass_accuracy_pct?: number | null;
  tackles_won?: number | null;
  interceptions?: number | null;
  clearances?: number | null;
  blocks?: number | null;
  saves?: number | null;
  clean_sheet?: boolean | null;
  yellow_cards?: number | null;
  red_cards?: number | null;
  verification_status: string;
  is_verified: boolean;
}

export interface MatchPlayersResponse {
  match_id: string;
  formation?: string | null;
  starting_xi: PlayerMatchDetailItem[];
  substitutes: PlayerMatchDetailItem[];
  bench_unused: PlayerMatchDetailItem[];
  data_source?: string | null;
}

// =============================================================================
// AVERAGE LINEUP & FORMATION
// =============================================================================
export interface AverageLineupStarter {
  player_id: string;
  name: string;
  jersey_number?: number | null;
  tactical_position: string;
  registered_position: string;
  matches_included: number;
  starts: number;
  sub_appearances: number;
  total_appearances: number;
  minutes_played: number;
  start_rate_pct: number;
  x: number;
  y: number;
}

export interface AverageLineupSubstitute {
  player_id: string;
  name: string;
  jersey_number?: number | null;
  position: string;
  sub_appearances: number;
  sub_minutes: number;
  starts: number;
  total_appearances: number;
  total_minutes: number;
}

export interface AverageLineupResponse {
  team_id: string;
  team_name: string;
  matches_analyzed: number;
  formation: string;
  formation_breakdown: Record<string, number>;
  starters: AverageLineupStarter[];
  substitutes: AverageLineupSubstitute[];
  verification_status: string;
  confidence_score: number;
}

// =============================================================================
// DEFENSIVE INTELLIGENCE
// =============================================================================
export interface PlayerDefensiveLeaderboardItem {
  player_id?: string | null;
  player_name: string;
  jersey_number?: number | null;
  position: string;
  nationality?: string;
  is_indian?: boolean;
  tackles_total: number;
  tackles_won: number;
  tackle_success_pct?: number | null;
  interceptions: number;
  clearances: number;
  blocks: number;
  recoveries: number;
  aerial_duels_won?: number | null;
  aerial_duels_total?: number | null;
  ground_duels_won?: number | null;
  ground_duels_attempted?: number | null;
  defensive_errors?: number | null;
  fouls_committed: number;
  yellow_cards: number;
  red_cards: number;
  minutes_played: number;
  appearances: number;
  starts: number;
  has_sufficient_minutes?: boolean;
  is_leadership_group?: boolean;
  leadership_role?: string | null;
  tackles_per_90?: number | null;
  interceptions_per_90?: number | null;
  clearances_per_90?: number | null;
  blocks_per_90?: number | null;
  recoveries_per_90?: number | null;
  total_defensive_actions: number;
  actions_per_90?: number | null;
  coverage_status: string;
}

export interface TeamDefensiveKpis {
  matches_played: number;
  goals_conceded: number;
  goals_conceded_per_match: number;
  clean_sheets: number;
  clean_sheet_percentage: number;
  tackles_total: number;
  tackles_won: number;
  tackle_success_pct: number;
  interceptions: number;
  clearances: number;
  blocked_shots: number;
  recoveries: number;
  total_defensive_actions: number;
  actions_per_match: number;
  saves: number;
  fouls_committed: number;
  yellow_cards: number;
  red_cards: number;
  discipline_index: number;
  opponent_shots?: number | null;
  opponent_shots_on_target?: number | null;
  opponent_expected_goals?: number | null;
  opponent_shots_per_match?: number | null;
  aerial_duels_attempted?: number | null;
  aerial_duels_won?: number | null;
  ground_duels_attempted?: number | null;
  ground_duels_won?: number | null;
  defensive_errors?: number | null;
}

export interface MatchDefensiveItem {
  match_id: string;
  match_number: number;
  date?: string | null;
  opponent_name: string;
  opponent_short?: string | null;
  venue?: string | null;
  is_home: boolean;
  result: string;
  goals_conceded: number;
  clean_sheet: boolean;
  tackles_total: number;
  tackles_won: number;
  tackle_success_pct: number;
  interceptions: number;
  clearances: number;
  blocks: number;
  recoveries: number;
  total_actions: number;
  saves: number;
  fouls_committed: number;
  opponent_shots?: number | null;
  opponent_shots_on_target?: number | null;
  opponent_expected_goals?: number | null;
}

export interface DefensiveIntelligenceResponse {
  team_id: string;
  team_name: string;
  matches_analyzed: number;
  team_defensive_kpis: TeamDefensiveKpis;
  matches_defensive?: MatchDefensiveItem[];
  player_leaderboard: PlayerDefensiveLeaderboardItem[];
  spatial_defensive_actions: any[];
  telemetry_provenance: Record<string, any>;
}

// =============================================================================
// AI FOOTBALL ANALYST
// =============================================================================
export interface AIAnalystKeyMetric {
  metric: string;
  value: string | number;
  context?: string;
}

export interface AIAnalystDossierResponse {
  query: string;
  archetype: string;
  title: string;
  executive_summary: string;
  key_statistics?: AIAnalystKeyMetric[];
  performance_evidence?: string[];
  football_interpretation: string;
  limitations?: string[];
  final_assessment: string;
  confidence_score?: number;
  verification_status?: string;
  verified_facts?: string[];
  calculated_metrics?: Record<string, any>;
  interpretation?: string;
  unavailable_data?: string[];
}

// =============================================================================
// SEASON LEADERSHIP GROUP
// =============================================================================
export interface LeadershipMember {
  id: string;
  player_id: string;
  player_name: string;
  jersey_number?: number | null;
  position: string;
  primary_position: string;
  nationality: string;
  is_indian: boolean;
  leadership_role: string;
  is_captain: boolean;
  is_vice_captain: boolean;
  image_url?: string | null;
  notes?: string | null;
}

export interface LeadershipGroupResponse {
  team_id: string;
  team_name: string;
  team_short_name: string;
  season_id: string;
  season_name: string;
  role_title: string;
  total_members: number;
  members: LeadershipMember[];
}






