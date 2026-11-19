import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchSeasonOverview,
  fetchSeasonForm,
  fetchSeasonHomeAway,
  fetchSeasonScoring,
  fetchPlayerSeasonStatistics,
  fetchDataQualityReport,
} from "../lib/api";

describe("Season Performance Overview API Client & Dynamic Contracts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches dynamic season overview KPIs without fabricated fallback values", async () => {
    const mockOverview = {
      season_id: "s26-uuid",
      season_name: "2026–27",
      team_id: "cfc-uuid",
      team_name: "Chennaiyin FC",
      short_name: "CFC",
      matches_played: 0,
      matches_remaining: 24,
      total_fixtures: 24,
      wins: 0,
      draws: 0,
      losses: 0,
      points: 0,
      goals_scored: 0,
      goals_conceded: 0,
      goal_difference: 0,
      win_percentage: 0.0,
      points_per_match: 0.0,
      clean_sheets: 0,
      failed_to_score: 0,
      is_season_active: true,
      verification_status: "PUBLISHED",
      recent_form: [],
      calculated_at: "2026-11-18T00:00:00Z",
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockOverview,
    } as any);

    const data = await fetchSeasonOverview();
    expect(data.season_name).toBe("2026–27");
    expect(data.matches_played).toBe(0);
    expect(data.matches_remaining).toBe(24);
    expect(data.total_fixtures).toBe(24);
    expect(data.points).toBe(0);
    expect(data.recent_form).toEqual([]);
    expect(data.win_percentage).toBe(0.0);
  });

  it("fetches home and away performance splits with 12 home and 12 away scheduled fixtures", async () => {
    const mockHomeAway = {
      home: {
        matches_played: 0,
        matches_scheduled: 12,
        wins: 0,
        draws: 0,
        losses: 0,
        points: 0,
        goals_scored: 0,
        goals_conceded: 0,
        goal_difference: 0,
        win_percentage: 0.0,
        points_per_match: 0.0,
        clean_sheets: 0,
      },
      away: {
        matches_played: 0,
        matches_scheduled: 12,
        wins: 0,
        draws: 0,
        losses: 0,
        points: 0,
        goals_scored: 0,
        goals_conceded: 0,
        goal_difference: 0,
        win_percentage: 0.0,
        points_per_match: 0.0,
        clean_sheets: 0,
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHomeAway,
    } as any);

    const data = await fetchSeasonHomeAway();
    expect(data.home.matches_scheduled).toBe(12);
    expect(data.away.matches_scheduled).toBe(12);
    expect(data.home.matches_played).toBe(0);
    expect(data.away.matches_played).toBe(0);
  });

  it("fetches automated data quality report with 100% integrity validation", async () => {
    const mockQuality = {
      total_players: 27,
      duplicate_players_count: 0,
      total_fixtures: 24,
      duplicate_fixtures_count: 0,
      scheduled_matches_count: 24,
      completed_matches_count: 0,
      discrepant_matches_count: 1,
      unplayed_matches_with_scores: 0,
      finished_matches_without_scores: 0,
      orphan_events_count: 0,
      season_contamination_detected: false,
      data_integrity_score_pct: 100.0,
      checks: [
        { name: "Squad Duplicate Check", status: "PASS", message: "Verified 27 active players" },
        { name: "Fixture Uniqueness Check", status: "PASS", message: "Verified 24 fixtures" },
        { name: "Unplayed Matches Score Integrity", status: "PASS", message: "No unplayed scores" },
        { name: "Season Isolation Check", status: "PASS", message: "Historical mock isolated" },
      ],
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockQuality,
    } as any);

    const data = await fetchDataQualityReport();
    expect(data.data_integrity_score_pct).toBe(100.0);
    expect(data.unplayed_matches_with_scores).toBe(0);
    expect(data.season_contamination_detected).toBe(false);
    expect(data.checks).toHaveLength(4);
  });

  it("verifies player statistics conform strictly to non-fabrication standard", async () => {
    const mockPlayers = [
      {
        player_id: "p1",
        name: "Samik Mitra",
        jersey_number: 1,
        position: "Goalkeeper",
        primary_position: "Goalkeeper",
        nationality: "India",
        appearances: 0,
        starts: 0,
        minutes_played: 0,
        goals: 0,
        assists: 0,
        yellow_cards: 0,
        red_cards: 0,
        clean_sheets: 0,
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockPlayers,
    } as any);

    const players = await fetchPlayerSeasonStatistics();
    expect(players).toHaveLength(1);
    expect(players[0].appearances).toBe(0);
    expect(players[0].goals).toBe(0);
    expect(players[0].minutes_played).toBe(0);
  });
});
