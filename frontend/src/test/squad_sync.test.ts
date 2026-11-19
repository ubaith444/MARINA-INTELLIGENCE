import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchActiveSquad,
  previewSquadImportJson,
  syncSquad,
  fetchSquadImportHistory,
  updatePlayer,
} from "@/lib/api";

describe("Squad Management & Synchronization API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchActiveSquad queries active squad endpoint with filter query params", async () => {
    const mockSquad = [
      {
        id: "m-1",
        player_id: "p-1",
        name: "Samik Mitra",
        squad_number: 1,
        position: "Goalkeeper",
        pos_group: "GK",
        nationality: "India",
        secondary_nationality: null,
        is_domestic: true,
        market_value_inr: 5500000,
        market_value_original: "₹55 L",
        is_active: true,
      },
      {
        id: "m-2",
        player_id: "p-2",
        name: "Nuno Rice",
        squad_number: 4,
        position: "Centre-Back",
        pos_group: "DEF",
        nationality: "Portugal",
        secondary_nationality: "Switzerland",
        is_domestic: false,
        market_value_inr: 5500000,
        market_value_original: "₹55 L",
        is_active: true,
      },
    ];

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockSquad,
    } as any);

    const result = await fetchActiveSquad({
      include_inactive: true,
      position: "DEF",
      nationality: "OVERSEAS",
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/squads/chennaiyin-fc/2026-27?include_inactive=true&position=DEF&nationality=OVERSEAS"),
      expect.any(Object)
    );
    expect(result).toHaveLength(2);
    expect(result[1].secondary_nationality).toBe("Switzerland");
    expect(result[1].is_domestic).toBe(false);
  });

  it("previewSquadImportJson sends player records and returns audit breakdown", async () => {
    const mockPreview = {
      team_id: "team-123",
      season_id: "season-123",
      batch_id: "batch-test-1",
      total_incoming: 27,
      new_players: [{ name: "Player A" }],
      updated_players: [{ name: "Samik Mitra" }],
      leaving_players: [{ name: "Ryan Edwards" }],
      retained_players: [],
      warnings: [],
      missing_fields_summary: { height_m: 14, preferred_foot: 15 },
      requires_confirmation: true,
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreview,
    } as any);

    const preview = await previewSquadImportJson([]);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/squads/import/json"),
      expect.objectContaining({
        method: "POST",
      })
    );
    expect(preview.total_incoming).toBe(27);
    expect(preview.new_players).toHaveLength(1);
    expect(preview.leaving_players).toHaveLength(1);
    expect(preview.requires_confirmation).toBe(true);
  });

  it("syncSquad executes squad synchronization with explicit confirmation", async () => {
    const mockSyncResponse = {
      batch_id: "batch-101",
      team_id: "team-1",
      season_id: "season-1",
      total_processed: 27,
      new_created: 22,
      updated: 5,
      deactivated: 3,
      retained: 0,
      active_squad_count: 27,
      status: "COMPLETED",
      message: "Squad roster synchronized successfully.",
      timestamp: "2026-11-18T12:00:00Z",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockSyncResponse,
    } as any);

    const res = await syncSquad({
      batch_id: "batch-101",
      confirmed: true,
      deactivate_absent: true,
    });

    expect(res.status).toBe("COMPLETED");
    expect(res.active_squad_count).toBe(27);
    expect(res.deactivated).toBe(3);
  });

  it("updatePlayer issues PATCH request with updated profile", async () => {
    const mockUpdatedPlayer = {
      id: "p-samik",
      slug: "samik-mitra",
      first_name: "Samik",
      last_name: "Mitra",
      known_name: "Samik Mitra",
      nationality: "India",
      is_active: true,
      squad_number: 1,
      contract_expiry: "2028-05-31",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockUpdatedPlayer,
    } as any);

    const updated = await updatePlayer("p-samik", {
      contract_expiry: "2028-05-31",
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/players/p-samik"),
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ contract_expiry: "2028-05-31" }),
      })
    );
    expect(updated.contract_expiry).toBe("2028-05-31");
  });
});
