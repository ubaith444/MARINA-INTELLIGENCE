/**
 * MARINA INTELLIGENCE — Centralized Typed API Client
 * Interfacing directly with FastAPI backend on PostgreSQL
 */

import {
  AttackingAnalytics,
  Competition,
  DefensiveAnalytics,
  FixtureImportResponse,
  Match,
  MatchTacticalReport,
  PassingNetwork,
  Player,
  PlayerPerformance,
  PlayerMatchHistoryItem,
  PlayerUpdatePayload,
  Season,
  ShotMap,
  TerritorialMetrics,
  DefensiveActionsResponse,
  HeatmapResponse,
  SquadImportHistoryItem,
  SquadImportPreview,
  SquadMember,
  SquadSyncRequestPayload,
  SquadSyncResponse,
  Team,
  TeamSeasonPerformance,
  SeasonOverviewResponse,
  SeasonFormResponse,
  SeasonResultItem,
  SeasonHomeAwayResponse,
  SeasonScoringResponse,
  PlayerSeasonStatisticItem,
  TopScorerItem,
  DataQualityResponse,
  MatchPlayersResponse,
  PlayerMatchDetailItem,
  PlayerListAnalyticsResponse,
  PlayerMatchHistoryResponse,
  XgOverviewResponse,
  OppositionAnalysisResponse,
  MatchCompareResponse,
  MatchTacticalBreakdownResponse,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  try {
    const isFormData = options?.body instanceof FormData;
    const headers: Record<string, string> = {
      ...(options?.headers as Record<string, string>),
    };
    if (!isFormData && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(url, {
      cache: "no-store",
      headers,
      ...options,
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => "");
      throw new Error(
        `API request failed: ${res.status} ${res.statusText} (${endpoint}) ${errorText}`
      );
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`[MARINA API Error] ${endpoint}:`, err.message || err);
    throw err;
  }
}

// 1. Health
export async function fetchHealth(): Promise<{
  status: string;
  database: string;
  app_env: string;
  version: string;
  timestamp: string;
  focus_club: string;
  focus_season: string;
  focus_competition: string;
}> {
  return request("/health");
}

// 2. Seasons & Competitions
export async function fetchCompetitions(): Promise<Competition[]> {
  return request("/competitions");
}

export async function fetchSeasons(): Promise<Season[]> {
  return request("/seasons");
}

export async function fetchSeasonBySlug(slug: string): Promise<Season> {
  return request(`/seasons/${slug}`);
}

// 3. Teams
export async function fetchTeams(): Promise<Team[]> {
  return request("/teams");
}

export async function fetchTeamBySlug(slug: string): Promise<Team> {
  return request(`/teams/${slug}`);
}

// 4. Players
export async function fetchPlayers(): Promise<Player[]> {
  return request("/players");
}

export async function fetchPlayerById(id: string): Promise<Player> {
  const all = await fetchPlayers();
  const player = all.find((p) => p.id === id);
  if (!player) throw new Error(`Player ${id} not found`);
  return player;
}

// 5. Matches & Fixtures
export async function fetchMatches(params?: {
  season_id?: string;
  team_id?: string;
  status?: string;
  is_home?: boolean;
  matchweek?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  offset?: number;
  limit?: number;
}): Promise<Match[]> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.team_id) query.append("team_id", params.team_id);
  if (params?.status) query.append("status", params.status);
  if (params?.is_home !== undefined) query.append("is_home", String(params.is_home));
  if (params?.matchweek !== undefined) query.append("matchweek", String(params.matchweek));
  if (params?.start_date) query.append("start_date", params.start_date);
  if (params?.end_date) query.append("end_date", params.end_date);
  if (params?.search) query.append("search", params.search);
  if (params?.offset !== undefined) query.append("offset", String(params.offset));
  if (params?.limit !== undefined) query.append("limit", String(params.limit));

  const qs = query.toString();
  return request(`/matches${qs ? `?${qs}` : ""}`);
}

export async function fetchUpcomingMatches(params?: {
  season_id?: string;
  team_id?: string;
  is_home?: boolean;
  matchweek?: number;
  limit?: number;
}): Promise<Match[]> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.team_id) query.append("team_id", params.team_id);
  if (params?.is_home !== undefined) query.append("is_home", String(params.is_home));
  if (params?.matchweek !== undefined) query.append("matchweek", String(params.matchweek));
  if (params?.limit !== undefined) query.append("limit", String(params.limit));
  const qs = query.toString();
  return request(`/matches/upcoming${qs ? `?${qs}` : ""}`);
}

export async function fetchCompletedMatches(params?: {
  season_id?: string;
  team_id?: string;
  is_home?: boolean;
  matchweek?: number;
  limit?: number;
}): Promise<Match[]> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.team_id) query.append("team_id", params.team_id);
  if (params?.is_home !== undefined) query.append("is_home", String(params.is_home));
  if (params?.matchweek !== undefined) query.append("matchweek", String(params.matchweek));
  if (params?.limit !== undefined) query.append("limit", String(params.limit));
  const qs = query.toString();
  return request(`/matches/completed${qs ? `?${qs}` : ""}`);
}

export async function fetchMatchById(id: string): Promise<Match> {
  return request(`/matches/${id}`);
}

export async function fetchMatchPlayers(matchId: string): Promise<MatchPlayersResponse> {
  return request(`/matches/${matchId}/players`);
}

export async function fetchAnalyticsSeason(params?: {
  season_id?: string;
  team_id?: string;
}): Promise<SeasonOverviewResponse> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.team_id) query.append("team_id", params.team_id);
  const qs = query.toString();
  return request(`/analytics/season${qs ? `?${qs}` : ""}`);
}

export async function fetchAnalyticsForm(params?: {
  season_id?: string;
  team_id?: string;
}): Promise<SeasonFormResponse> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.team_id) query.append("team_id", params.team_id);
  const qs = query.toString();
  return request(`/analytics/form${qs ? `?${qs}` : ""}`);
}

// 5b. Chennaiyin FC 2026–27 Fixture Management
export async function fetchFixtures(params?: {
  season_id?: string;
  opponent?: string;
  home_away?: string;
  verification_status?: string;
  publication_status?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}): Promise<Match[]> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.opponent && params.opponent !== "ALL") query.append("opponent", params.opponent);
  if (params?.home_away && params.home_away !== "ALL") query.append("home_away", params.home_away);
  if (params?.verification_status && params.verification_status !== "ALL")
    query.append("verification_status", params.verification_status);
  if (params?.publication_status && params.publication_status !== "ALL")
    query.append("publication_status", params.publication_status);
  if (params?.date_from) query.append("date_from", params.date_from);
  if (params?.date_to) query.append("date_to", params.date_to);
  if (params?.limit) query.append("limit", params.limit.toString());
  if (params?.offset) query.append("offset", params.offset.toString());

  const qs = query.toString();
  return request(`/fixtures${qs ? `?${qs}` : ""}`);
}

export async function fetchSeasonFixtures(seasonSlug: string = "2026-27"): Promise<Match[]> {
  return request(`/fixtures/season/${seasonSlug}`);
}

export async function fetchFixtureById(id: string): Promise<Match> {
  return request(`/fixtures/${id}`);
}

export async function importFixtures(file?: File): Promise<FixtureImportResponse> {
  if (file) {
    const formData = new FormData();
    formData.append("file", file);
    return request("/fixtures/import", {
      method: "POST",
      body: formData,
    });
  }
  return request("/fixtures/import", {
    method: "POST",
  });
}

// 6. Analytics: Season Overview
export async function fetchSeasonAnalytics(params?: {
  team_id?: string;
  season_id?: string;
  form_window?: number;
}): Promise<TeamSeasonPerformance> {
  const query = new URLSearchParams();
  if (params?.team_id) query.append("team_id", params.team_id);
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.form_window) query.append("form_window", params.form_window.toString());

  const qs = query.toString();
  return request(`/analytics/season${qs ? `?${qs}` : ""}`);
}

// 7. Analytics: Team Performance, Attacking & Defensive
export async function fetchTeamPerformance(
  team_id: string,
  season_id?: string
): Promise<TeamSeasonPerformance> {
  if (season_id) {
    return request(`/analytics/teams/${team_id}/season/${season_id}`);
  }
  return request(`/analytics/team/${team_id}`);
}

export async function fetchTeamAttacking(
  team_id: string,
  season_id?: string
): Promise<AttackingAnalytics> {
  const qs = season_id ? `?season_id=${season_id}` : "";
  return request(`/analytics/teams/${team_id}/attacking${qs}`);
}

export async function fetchTeamDefensive(
  team_id: string,
  season_id?: string
): Promise<DefensiveAnalytics> {
  const qs = season_id ? `?season_id=${season_id}` : "";
  return request(`/analytics/teams/${team_id}/defensive${qs}`);
}

// 8. Analytics: Player Performance & Comparison
export async function fetchAllPlayersAnalytics(params?: {
  position?: string;
  min_minutes?: number;
  search?: string;
  sort_by?: string;
  order?: string;
}): Promise<PlayerListAnalyticsResponse> {
  const query = new URLSearchParams();
  if (params?.position && params.position !== "ALL") query.append("position", params.position);
  if (params?.min_minutes) query.append("min_minutes", params.min_minutes.toString());
  if (params?.search) query.append("search", params.search);
  if (params?.sort_by) query.append("sort_by", params.sort_by);
  if (params?.order) query.append("order", params.order);
  const qs = query.toString();
  return request(`/analytics/players${qs ? `?${qs}` : ""}`);
}

export async function fetchPlayerPerformance(
  player_id: string,
  season_id?: string,
  min_minutes: number = 45
): Promise<PlayerPerformance> {
  const query = new URLSearchParams();
  if (season_id) query.append("season_id", season_id);
  query.append("min_minutes", min_minutes.toString());

  return request(`/analytics/players/${player_id}/performance?${query.toString()}`);
}

export async function fetchPlayerMatches(player_id: string): Promise<PlayerMatchHistoryItem[]> {
  return request(`/players/${player_id}/matches`);
}

export async function fetchPlayerMatchHistory(player_id: string): Promise<PlayerMatchHistoryResponse> {
  return request(`/analytics/players/${player_id}/matches`);
}

// 9. Match Tactical Intelligence
export async function fetchMatchTacticalReport(match_id: string): Promise<MatchTacticalReport> {
  return request(`/analytics/matches/${match_id}/report`);
}

export async function fetchMatchTacticalBreakdown(match_id: string): Promise<MatchTacticalBreakdownResponse> {
  return request(`/analytics/tactical/${match_id}`);
}

export async function fetchPassingNetwork(
  match_id?: string,
  team_id?: string,
  player_id?: string,
  period?: string
): Promise<PassingNetwork> {
  const query = new URLSearchParams();
  if (match_id && match_id !== "ALL") query.append("match_id", match_id);
  if (player_id && player_id !== "ALL") query.append("player_id", player_id);
  if (period) query.append("period", period);
  const qs = query.toString();
  return request(`/analytics/tactical/passing-network${qs ? `?${qs}` : ""}`);
}

export async function fetchShotMap(
  match_id?: string,
  player_id?: string,
  outcome?: string
): Promise<ShotMap> {
  const query = new URLSearchParams();
  if (match_id && match_id !== "ALL") query.append("match_id", match_id);
  if (player_id && player_id !== "ALL") query.append("player_id", player_id);
  if (outcome && outcome !== "ALL") query.append("outcome", outcome);
  const qs = query.toString();
  return request(`/analytics/shots${qs ? `?${qs}` : ""}`);
}

export async function fetchXgAnalytics(params?: {
  season_id?: string;
  match_id?: string;
}): Promise<XgOverviewResponse> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.match_id && params.match_id !== "ALL") query.append("match_id", params.match_id);
  const qs = query.toString();
  return request(`/analytics/xg${qs ? `?${qs}` : ""}`);
}

export async function fetchOppositionAnalysis(opponent_id: string): Promise<OppositionAnalysisResponse> {
  return request(`/analytics/opposition/${opponent_id}`);
}

export async function fetchMatchCompare(match_a_id: string, match_b_id: string): Promise<MatchCompareResponse> {
  return request(`/analytics/matches/compare?match_a_id=${match_a_id}&match_b_id=${match_b_id}`);
}

export async function fetchTerritorialMetrics(params?: {
  match_id?: string;
  season_id?: string;
}): Promise<TerritorialMetrics> {
  const query = new URLSearchParams();
  if (params?.match_id && params.match_id !== "ALL") query.append("match_id", params.match_id);
  if (params?.season_id) query.append("season_id", params.season_id);
  const qs = query.toString();
  return request(`/analytics/tactical/territorial${qs ? `?${qs}` : ""}`);
}

export async function fetchDefensiveActions(params?: {
  match_id?: string;
  player_id?: string;
}): Promise<DefensiveActionsResponse> {
  const query = new URLSearchParams();
  if (params?.match_id && params.match_id !== "ALL") query.append("match_id", params.match_id);
  if (params?.player_id && params.player_id !== "ALL") query.append("player_id", params.player_id);
  const qs = query.toString();
  return request(`/analytics/tactical/defensive-actions${qs ? `?${qs}` : ""}`);
}

export async function fetchHeatmap(params?: {
  match_id?: string;
  player_id?: string;
}): Promise<HeatmapResponse> {
  const query = new URLSearchParams();
  if (params?.match_id && params.match_id !== "ALL") query.append("match_id", params.match_id);
  if (params?.player_id && params.player_id !== "ALL") query.append("player_id", params.player_id);
  const qs = query.toString();
  return request(`/analytics/tactical/heatmap${qs ? `?${qs}` : ""}`);
}

// -----------------------------------------------------------------------------
// 10. Squad Management & Synchronization
// -----------------------------------------------------------------------------

export async function fetchActiveSquad(params?: {
  include_inactive?: boolean;
  position?: string;
  nationality?: string;
}): Promise<SquadMember[]> {
  const query = new URLSearchParams();
  if (params?.include_inactive) query.append("include_inactive", "true");
  if (params?.position && params.position !== "ALL") query.append("position", params.position);
  if (params?.nationality && params.nationality !== "ALL") query.append("nationality", params.nationality);

  const qs = query.toString();
  return request(`/squads/chennaiyin-fc/2026-27${qs ? `?${qs}` : ""}`);
}

export async function previewSquadImportFile(file: File): Promise<SquadImportPreview> {
  const formData = new FormData();
  formData.append("file", file);

  return request("/squads/import", {
    method: "POST",
    body: formData,
  });
}

export async function previewSquadImportJson(players?: Record<string, any>[]): Promise<SquadImportPreview> {
  return request("/squads/import/json", {
    method: "POST",
    body: JSON.stringify(players || []),
  });
}

export async function syncSquad(payload: SquadSyncRequestPayload): Promise<SquadSyncResponse> {
  return request("/squads/sync", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchSquadImportHistory(limit: number = 50): Promise<SquadImportHistoryItem[]> {
  return request(`/squads/import/history?limit=${limit}`);
}

export async function updatePlayer(
  playerId: string,
  payload: PlayerUpdatePayload
): Promise<Player> {
  return request(`/players/${playerId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// ============================================================================
// Season Overview & Data Quality Dynamic APIs
// ============================================================================

export async function fetchSeasonOverview(seasonId?: string): Promise<SeasonOverviewResponse> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/season/overview${query}`);
}

export async function fetchSeasonForm(seasonId?: string): Promise<SeasonFormResponse> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/season/form${query}`);
}

export async function fetchSeasonResults(seasonId?: string): Promise<SeasonResultItem[]> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/season/results${query}`);
}

export async function fetchSeasonHomeAway(seasonId?: string): Promise<SeasonHomeAwayResponse> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/season/home-away${query}`);
}

export async function fetchSeasonScoring(seasonId?: string): Promise<SeasonScoringResponse> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/season/scoring${query}`);
}

export async function fetchPlayerSeasonStatistics(params?: {
  season_id?: string;
  is_indian?: boolean;
  position?: string;
  search?: string;
}): Promise<PlayerSeasonStatisticItem[]> {
  const query = new URLSearchParams();
  if (params?.season_id) query.append("season_id", params.season_id);
  if (params?.is_indian !== undefined) query.append("is_indian", String(params.is_indian));
  if (params?.position && params.position !== "ALL") query.append("position", params.position);
  if (params?.search) query.append("search", params.search);
  const qs = query.toString();
  return request(`/players/statistics${qs ? `?${qs}` : ""}`);
}

export async function fetchTopScorers(limit: number = 10): Promise<TopScorerItem[]> {
  return request(`/players/top-scorers?limit=${limit}`);
}

export async function fetchDataQualityReport(seasonId?: string): Promise<DataQualityResponse> {
  const query = seasonId ? `?season_id=${seasonId}` : "";
  return request(`/data-quality${query}`);
}

// ============================================================================
// Data Synchronization & Provenance APIs
// ============================================================================

export async function fetchSyncLogs(limit: number = 20): Promise<import("./types").DataSyncLogItem[]> {
  return request(`/sync/logs?limit=${limit}`);
}

export async function fetchDiscrepancies(disputedOnly: boolean = false, limit: number = 50): Promise<import("./types").DataVerificationItem[]> {
  return request(`/sync/discrepancies?disputed_only=${disputedOnly}&limit=${limit}`);
}

export async function triggerMatchSync(): Promise<import("./types").SyncTriggerResponse> {
  return request("/sync/matches", {
    method: "POST",
  });
}

export async function fetchDataSources(): Promise<any[]> {
  return request("/data-sources");
}

export async function fetchAverageLineup(params?: { team_id?: string; season_id?: string }): Promise<import("./types").AverageLineupResponse> {
  const query = new URLSearchParams();
  if (params?.team_id) query.set("team_id", params.team_id);
  if (params?.season_id) query.set("season_id", params.season_id);
  const qs = query.toString();
  return request(`/analytics/average-lineup${qs ? `?${qs}` : ""}`);
}

export async function fetchDefensiveIntelligence(params?: { team_id?: string; season_id?: string; match_id?: string; player_id?: string }): Promise<import("./types").DefensiveIntelligenceResponse> {
  const query = new URLSearchParams();
  if (params?.team_id) query.set("team_id", params.team_id);
  if (params?.season_id) query.set("season_id", params.season_id);
  if (params?.match_id) query.set("match_id", params.match_id);
  if (params?.player_id) query.set("player_id", params.player_id);
  const qs = query.toString();
  return request(`/analytics/defensive-intelligence${qs ? `?${qs}` : ""}`);
}

export async function askAiAnalyst(query: string): Promise<import("./types").AIAnalystDossierResponse> {
  return request("/analytics/ai-analyst/ask", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export async function fetchLeadershipGroup(params?: {
  team_id?: string;
  season_id?: string;
}): Promise<import("./types").LeadershipGroupResponse> {
  const query = new URLSearchParams();
  if (params?.team_id) query.set("team_id", params.team_id);
  if (params?.season_id) query.set("season_id", params.season_id);
  const qs = query.toString();
  return request(`/teams/leadership-group${qs ? `?${qs}` : ""}`);
}







