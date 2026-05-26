/**
 * Viewport regression for the Paper Run Preview panel.
 *
 * Runs across three viewport sizes matching the iPad smoke test targets:
 *   - ipad-portrait  768 x 1024
 *   - ipad-air       834 x 1194
 *   - mobile-narrow  390 x 844
 *
 * Backend is NOT required. All terminal API functions return fallback data
 * when the backend is offline, and the panel renders EmptyRunState until
 * the user explicitly clicks "Load Preview".
 *
 * Safety posture: read-only, dry-run, no broker execution.
 * No POST / PUT / PATCH / DELETE calls are made by this test.
 */

import { expect, test } from "@playwright/test";

// ─── Constants ────────────────────────────────────────────────────────────────

const ROUTE = "/terminal/paper-run-preview";

/** Time allowed for the boot screen (~1 350 ms) + initial render. */
const PANEL_TIMEOUT = 10_000;

const SAFETY_CHIPS = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "HUMAN REVIEW REQUIRED",
  "EXECUTION OFF",
] as const;

/**
 * Interactive controls that must NOT appear on this read-only panel.
 * Verified as absent via getByRole("button") to avoid false positives on
 * static text (e.g. field labels that mention "Side").
 */
const FORBIDDEN_BUTTONS = [
  { label: "Buy", pattern: /^Buy$/i },
  { label: "Sell", pattern: /^Sell$/i },
  { label: "Execute", pattern: /^Execute$/i },
  { label: "Place Order", pattern: /^Place Order$/i },
  { label: "Live Order", pattern: /^Live Order$/i },
  { label: "Connect Live Broker", pattern: /^Connect Live Broker$/i },
] as const;

// ─── Suite ────────────────────────────────────────────────────────────────────

test.describe("Paper Run Preview — viewport regression", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTE);
    // Wait for boot screen to clear and the panel section to enter the DOM.
    await expect(
      page.locator('[aria-label="Paper run preview panel"]'),
    ).toBeVisible({ timeout: PANEL_TIMEOUT });
  });

  // ── 1. Page loads without crash ──────────────────────────────────────────

  test("panel renders without crash", async ({ page }) => {
    await expect(
      page.locator('[aria-label="Paper run preview panel"]'),
    ).toBeVisible();
  });

  // ── 2. Safety chips ──────────────────────────────────────────────────────

  for (const chip of SAFETY_CHIPS) {
    test(`safety chip visible: ${chip}`, async ({ page }) => {
      const chipRow = page.locator(
        '[aria-label="Paper run preview safety chips"]',
      );
      await expect(chipRow.getByText(chip, { exact: true })).toBeVisible();
    });
  }

  // ── 3. Form fields ───────────────────────────────────────────────────────

  test("symbol input is visible", async ({ page }) => {
    await expect(page.getByLabel("Symbol")).toBeVisible();
  });

  test("side select is visible", async ({ page }) => {
    await expect(page.getByLabel("Side")).toBeVisible();
  });

  // ── 4. Action row ────────────────────────────────────────────────────────

  test("Load Preview button is visible", async ({ page }) => {
    await expect(
      page.getByRole("button", { name: /Load Preview|Refresh Preview/ }),
    ).toBeVisible();
  });

  // ── 5. No horizontal overflow ────────────────────────────────────────────

  test("no horizontal overflow", async ({ page }) => {
    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth + 1,
    );
    expect(hasOverflow, "horizontal overflow detected").toBe(false);
  });

  // ── 6. No forbidden controls ─────────────────────────────────────────────

  for (const { label, pattern } of FORBIDDEN_BUTTONS) {
    test(`no forbidden button: "${label}"`, async ({ page }) => {
      await expect(page.getByRole("button", { name: pattern })).toHaveCount(0);
    });
  }
});
