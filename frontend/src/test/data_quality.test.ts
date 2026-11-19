import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchDataQualityReport, fetchDataSources } from "@/lib/api";

describe("Data Quality & Sources API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchDataQualityReport queries /data-quality endpoint", async () => {
    const mockReport = {
      total_players: 28,
      duplicate_players_count: 0,
      total_fixtures: 24,
      duplicate_fixtures_count: 0,
      scheduled_matches_count: 19,
      completed_matches_count: 5,
      discrepant_matches_count: 0,
      unplayed_matches_with_scores: 0,
      finished_matches_without_scores: 0,
      orphan_events_count: 0,
      season_contamination_detected: false,
      data_integrity_score_pct: 100,
      checks: [
        {
          name: "Season 2026–27 Fixture Count",
          status: "PASS",
          message: "Exactly 24 fixtures found matching ISL 2026–27 schedule.",
        },
        {
          name: "Unplayed Match Score Safety",
          status: "PASS",
          message: "All 19 scheduled fixtures have strictly null scores.",
        },
      ],
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockReport,
    } as any);

    const report = await fetchDataQualityReport("2026-27");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/data-quality?season_id=2026-27"),
      expect.any(Object)
    );
    expect(report.data_integrity_score_pct).toBe(100);
    expect(report.checks).toHaveLength(2);
    expect(report.unplayed_matches_with_scores).toBe(0);
  });

  it("fetchDataSources queries /data-sources endpoint", async () => {
    const mockSources = [
      {
        code: "ISL_OFFICIAL",
        name: "Indian Super League Official Match Center",
        provider_type: "OFFICIAL_LEAGUE",
        trust_score: 100,
      },
      {
        code: "CHENNAIYIN_FC_OFFICIAL",
        name: "Chennaiyin FC Official Club Portal",
        provider_type: "CLUB_COMMUNICATIONS",
        trust_score: 100,
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockSources,
    } as any);

    const sources = await fetchDataSources();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/data-sources"),
      expect.any(Object)
    );
    expect(sources).toHaveLength(2);
    expect(sources[0].trust_score).toBe(100);
  });
});
