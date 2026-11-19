import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchMatches,
  fetchUpcomingMatches,
  fetchCompletedMatches,
  fetchMatchPlayers,
  fetchAnalyticsSeason,
  fetchAnalyticsForm,
} from "@/lib/api";

describe("Match Centre API Client & Endpoint Suite", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchMatches passes query filters correctly", async () => {
    const mockMatches = [
      {
        id: "match-1",
        match_number: 1,
        match_status: "FINISHED",
        home_score: 1,
        away_score: 1,
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockMatches,
    } as any);

    const result = await fetchMatches({
      status: "FINISHED",
      is_home: true,
      matchweek: 1,
      search: "Goa",
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/matches\?status=FINISHED&is_home=true&matchweek=1&search=Goa/),
      expect.any(Object)
    );
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("match-1");
  });

  it("fetchUpcomingMatches queries /matches/upcoming endpoint", async () => {
    const mockUpcoming = [
      {
        id: "match-6",
        match_number: 6,
        match_status: "SCHEDULED",
        home_score: null,
        away_score: null,
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockUpcoming,
    } as any);

    const result = await fetchUpcomingMatches({ limit: 10 });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/matches/upcoming?limit=10"),
      expect.any(Object)
    );
    expect(result).toHaveLength(1);
    expect(result[0].home_score).toBeNull();
  });

  it("fetchCompletedMatches queries /matches/completed endpoint", async () => {
    const mockCompleted = [
      {
        id: "match-5",
        match_number: 5,
        match_status: "FINISHED",
        home_score: 5,
        away_score: 3,
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockCompleted,
    } as any);

    const result = await fetchCompletedMatches({ limit: 5 });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/matches/completed?limit=5"),
      expect.any(Object)
    );
    expect(result).toHaveLength(1);
    expect(result[0].match_status).toBe("FINISHED");
  });

  it("fetchMatchPlayers queries /matches/{id}/players with starting XI and substitutes", async () => {
    const mockPlayers = {
      match_id: "match-1",
      formation: "4-3-3",
      starting_xi: [
        {
          player_id: "p-1",
          name: "Ramon Tanque",
          jersey_number: 7,
          position: "CF",
          lineup_role: "STARTER",
          is_captain: false,
          minutes_played: 90,
          goals: 1,
          assists: 0,
        },
      ],
      substitutes: [
        {
          player_id: "p-2",
          name: "Lalhriatpuia Chawngthu",
          jersey_number: 17,
          position: "CM",
          lineup_role: "SUBSTITUTE",
          is_captain: false,
          minutes_played: 25,
          sub_in_minute: 65,
          replaced_player_name: "Ramon Tanque",
        },
      ],
      bench_unused: [],
      data_source: "Official ISL Match Centre",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockPlayers,
    } as any);

    const result = await fetchMatchPlayers("match-1");

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/matches/match-1/players"),
      expect.any(Object)
    );
    expect(result.starting_xi).toHaveLength(1);
    expect(result.starting_xi[0].name).toBe("Ramon Tanque");
    expect(result.substitutes[0].sub_in_minute).toBe(65);
  });

  it("fetchAnalyticsSeason and fetchAnalyticsForm query analytics endpoints", async () => {
    const mockSeason = {
      season_id: "s-1",
      matches_played: 5,
      total_fixtures: 24,
      points: 5,
      goals_scored: 6,
      goals_conceded: 7,
      goal_difference: -1,
      clean_sheets: 1,
      wins: 1,
      draws: 2,
      losses: 2,
    };

    const mockForm = {
      matches: [],
      sequence: ["D", "L", "L", "D", "W"],
    };

    vi.spyOn(global, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSeason,
      } as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockForm,
      } as any);

    const seasonRes = await fetchAnalyticsSeason();
    expect(seasonRes.matches_played).toBe(5);
    expect(seasonRes.points).toBe(5);

    const formRes = await fetchAnalyticsForm();
    expect(formRes.sequence).toEqual(["D", "L", "L", "D", "W"]);
  });
});
