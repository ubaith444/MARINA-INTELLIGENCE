import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchPlayerSeasonStatistics,
  fetchPlayerPerformance,
  fetchPlayerMatches,
} from "../lib/api";

describe("Player Individual Statistics & Intelligence Contracts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches individual player statistics strictly reflecting verified matches", async () => {
    const mockStats = [
      {
        player_id: "p-yadwad",
        name: "Irfan Yadwad",
        jersey_number: 24,
        position: "Centre-Forward",
        primary_position: "CF",
        nationality: "India",
        appearances: 5,
        starts: 5,
        substitute_appearances: 0,
        minutes_played: 406,
        goals: 3,
        assists: 1,
        yellow_cards: 0,
        red_cards: 0,
        clean_sheets: null,
        goals_per_90: 0.67,
        has_sufficient_minutes: true,
      },
      {
        player_id: "p-mitra",
        name: "Samik Mitra",
        jersey_number: 1,
        position: "Goalkeeper",
        primary_position: "GK",
        nationality: "India",
        appearances: 0,
        starts: 0,
        substitute_appearances: 0,
        minutes_played: 0,
        goals: 0,
        assists: 0,
        yellow_cards: 0,
        red_cards: 0,
        clean_sheets: 0,
        goals_per_90: null,
        has_sufficient_minutes: false,
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockStats,
    } as any);

    const data = await fetchPlayerSeasonStatistics();
    expect(data.length).toBe(2);

    const yadwad = data.find((p) => p.name === "Irfan Yadwad");
    expect(yadwad).toBeDefined();
    expect(yadwad?.goals).toBe(3);
    expect(yadwad?.minutes_played).toBe(406);
    expect(yadwad?.goals_per_90).toBe(0.67);
    expect(yadwad?.clean_sheets).toBeNull();

    const mitra = data.find((p) => p.name === "Samik Mitra");
    expect(mitra).toBeDefined();
    expect(mitra?.appearances).toBe(0);
    expect(mitra?.minutes_played).toBe(0);
    expect(mitra?.goals_per_90).toBeNull();
  });

  it("fetches goalkeeper-specific metrics without conflating outfield roles", async () => {
    const mockNawazPerf = {
      player_id: "p-nawaz",
      slug: "mohammad-nawaz",
      name: "Mohammad Nawaz",
      primary_position: "GOALKEEPER",
      nationality: "India",
      appearances: 5,
      starts: 5,
      substitute_appearances: 0,
      minutes_played: 450,
      raw_totals: {
        goals: 0,
        assists: 0,
        goal_contributions: 0,
        saves: 19,
        clean_sheets: 1,
        goals_conceded: 7,
        save_percentage: 73.1,
        passes_completed: 100,
        pass_accuracy_pct: 76.9,
      },
      per_90: {
        has_sufficient_minutes: true,
        min_minutes_threshold: 45,
        goals_per_90: 0.0,
      },
      data_provenance: {
        data_source: "Official Indian Super League Match Records",
        verification_status: "VERIFIED",
        matches_logged: 5,
        has_optical_tracking: false,
        has_event_data: true,
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockNawazPerf,
    } as any);

    const perf = await fetchPlayerPerformance("p-nawaz");
    expect(perf.name).toBe("Mohammad Nawaz");
    expect(perf.raw_totals.saves).toBe(19);
    expect(perf.raw_totals.clean_sheets).toBe(1);
    expect(perf.raw_totals.save_percentage).toBe(73.1);
    expect(perf.data_provenance?.verification_status).toBe("VERIFIED");
  });
});
