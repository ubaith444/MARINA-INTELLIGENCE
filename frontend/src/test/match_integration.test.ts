import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchSyncLogs,
  fetchDiscrepancies,
  triggerMatchSync,
} from "@/lib/api";

describe("Match Data Integration & Provenance API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchSyncLogs retrieves ingestion execution audit history", async () => {
    const mockLogs = [
      {
        id: "log-1",
        sync_type: "HISTORICAL_MATCH_SYNC",
        provider_name: "FBREF_VERIFIED",
        status: "SUCCESS",
        matches_synced: 5,
        records_updated: 41,
        discrepancy_count: 3,
        duration_ms: 180,
        created_at: "2026-11-18T09:09:12.819Z",
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockLogs,
    } as any);

    const logs = await fetchSyncLogs(10);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sync/logs?limit=10"),
      expect.any(Object)
    );
    expect(logs).toHaveLength(1);
    expect(logs[0].matches_synced).toBe(5);
    expect(logs[0].discrepancy_count).toBe(3);
  });

  it("fetchDiscrepancies retrieves disputed metric records", async () => {
    const mockDiscrepancies = [
      {
        id: "d-1",
        metric_name: "possession_pct",
        primary_source: "FBREF_VERIFIED",
        primary_value: "52.0%",
        secondary_source: "BADB_STATS",
        secondary_value: "48.0%",
        verification_status: "DISPUTED",
        is_disputed: true,
        notes: "Conflicting provider values",
        created_at: "2026-11-18T09:09:12.834Z",
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockDiscrepancies,
    } as any);

    const data = await fetchDiscrepancies(true, 50);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sync/discrepancies?disputed_only=true&limit=50"),
      expect.any(Object)
    );
    expect(data).toHaveLength(1);
    expect(data[0].metric_name).toBe("possession_pct");
    expect(data[0].is_disputed).toBe(true);
  });

  it("triggerMatchSync posts to sync matches endpoint", async () => {
    const mockResponse = {
      status: "SUCCESS",
      matches_synced: 5,
      discrepancies_flagged: 3,
      records_updated: 41,
      duration_ms: 195,
      message: "Successfully synchronized 5 completed fixtures",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as any);

    const result = await triggerMatchSync();
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/sync/matches"),
      expect.objectContaining({ method: "POST" })
    );
    expect(result.status).toBe("SUCCESS");
    expect(result.matches_synced).toBe(5);
  });
});
