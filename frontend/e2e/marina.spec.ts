import { test, expect } from "@playwright/test";

test.describe("MARINA INTELLIGENCE — Platform End-to-End Suite", () => {
  test("Season Dashboard loads successfully with KPI cards", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/MARINA INTELLIGENCE/);
    await expect(page.getByText("Season Performance Overview")).toBeVisible();
    await expect(page.getByText("Chennaiyin FC")).toBeVisible();
    await expect(page.getByText("Matches")).toBeVisible();
    await expect(page.getByText("Points")).toBeVisible();
  });

  test("Match Centre displays fixtures and supports status filtering", async ({ page }) => {
    await page.goto("/matches");
    await expect(page.getByText("Interactive Match Centre")).toBeVisible();

    // Default shows fixtures
    await expect(page.getByText("All Fixtures")).toBeVisible();
    await expect(page.getByText("Results (Finished)")).toBeVisible();

    // Filter by Finished
    await page.getByText("Results (Finished)").click();
    await expect(page.getByText("Full Time").first()).toBeVisible();
  });

  test("Tactical Pitch component renders SVG pitch and mode buttons", async ({ page }) => {
    await page.goto("/tactical");
    await expect(page.getByText("Tactical Performance & Spatial Intelligence")).toBeVisible();
    await expect(page.getByText("FORMATION")).toBeVisible();
    await expect(page.getByText("PASSING NETWORK")).toBeVisible();
    await expect(page.getByText("SHOT MAP")).toBeVisible();

    // Click Shot Map mode
    await page.getByText("SHOT MAP").click();
    await expect(page.getByText("Goal")).toBeVisible();
  });

  test("Player Directory lists players and supports search", async ({ page }) => {
    await page.goto("/players");
    await expect(page.getByText("Player Performance Directory")).toBeVisible();
    await expect(page.getByText("Wilmar Jordan Gil")).toBeVisible();

    // Filter by search
    const searchInput = page.getByPlaceholder("Search player name...");
    await searchInput.fill("Edwards");
    await expect(page.getByText("Ryan Edwards (C)")).toBeVisible();
  });

  test("Settings page displays API configuration and Data Provenance", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByText("FastAPI REST Backend Connection")).toBeVisible();
    await expect(page.getByText("Authoritative Data Provenance")).toBeVisible();
    await expect(page.getByText("ISL_OFFICIAL")).toBeVisible();
  });
});
