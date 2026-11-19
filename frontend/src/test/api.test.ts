import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchHealth,
  fetchMatches,
  fetchSeasonAnalytics,
  fetchTeamAttacking,
} from "@/lib/api";

describe("API Client Layer", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchHealth calls /health and parses JSON", async () => {
    const mockHealth = {
      status: "healthy",
      database: "connected",
      app_env: "testing",
      version: "0.1.0",
      timestamp: "2026-11-18T00:00:00Z",
      focus_club: "Chennaiyin FC",
      focus_season: "2026–27",
      focus_competition: "Indian Super League",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealth,
    } as any);

    const result = await fetchHealth();
    expect(result.status).toBe("healthy");
    expect(result.focus_club).toBe("Chennaiyin FC");
  });

  it("fetchMatches constructs query parameters properly", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    } as any);

    await fetchMatches({ season_id: "s-123", status: "FINISHED" });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/matches?season_id=s-123&status=FINISHED"),
      expect.any(Object)
    );
  });
});
