import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchFixtures,
  fetchSeasonFixtures,
  fetchFixtureById,
  importFixtures,
} from "@/lib/api";

describe("Fixture Management & Season Schedule API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchSeasonFixtures fetches full season 2026–27 fixtures", async () => {
    const mockFixtures = [
      {
        id: "fix-1",
        match_number: 1,
        scheduled_kickoff: "2026-10-10T19:30:00+05:30",
        kickoff_time_ist: "7:30 PM",
        publication_status: "PUBLISHED",
        verification_status: "PUBLISHED",
        home_team: { name: "FC Goa", slug: "fc-goa" },
        away_team: { name: "Chennaiyin FC", slug: "chennaiyin-fc" },
      },
      {
        id: "fix-24",
        match_number: 24,
        scheduled_kickoff: null,
        kickoff_time_ist: null,
        venue: null,
        publication_status: "PROVISIONAL",
        verification_status: "PENDING",
        venue_verification_status: "TBC",
        home_team: { name: "Inter Kashi", slug: "inter-kashi" },
        away_team: { name: "Chennaiyin FC", slug: "chennaiyin-fc" },
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFixtures,
    } as any);

    const fixtures = await fetchSeasonFixtures("2026-27");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/fixtures/season/2026-27"),
      expect.any(Object)
    );
    expect(fixtures).toHaveLength(2);
    expect(fixtures[0].match_number).toBe(1);
    expect(fixtures[1].scheduled_kickoff).toBeNull();
    expect(fixtures[1].venue_verification_status).toBe("TBC");
  });

  it("fetchFixtures applies opponent, home/away and status query filters", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    } as any);

    await fetchFixtures({
      opponent: "Kerala Blasters",
      home_away: "HOME",
      verification_status: "PUBLISHED",
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/fixtures?opponent=Kerala+Blasters&home_away=HOME&verification_status=PUBLISHED"),
      expect.any(Object)
    );
  });

  it("importFixtures sends POST request to /fixtures/import", async () => {
    const mockResponse = {
      batch_id: "fix-sync-123",
      season_id: "s-123",
      total_processed: 24,
      published_count: 12,
      provisional_count: 12,
      discrepancies_flagged: 1,
      new_created: 0,
      updated: 24,
      status: "COMPLETED",
      message: "Successfully imported 24 fixtures for Chennaiyin FC ISL 2026–27.",
      timestamp: "2026-11-18T12:00:00Z",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as any);

    const res = await importFixtures();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/fixtures/import"),
      expect.objectContaining({ method: "POST" })
    );
    expect(res.total_processed).toBe(24);
    expect(res.published_count).toBe(12);
    expect(res.discrepancies_flagged).toBe(1);
  });
});
