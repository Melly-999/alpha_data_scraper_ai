/**
 * Interaction tests for the Paper Run Preview panel.
 *
 * Mocks GET /paper/run/preview and exercises the full form-submit →
 * result-render flow. Runs on all three configured viewport projects:
 *   - ipad-portrait  768 × 1024
 *   - ipad-air       834 × 1194
 *   - mobile-narrow  390 × 844
 *
 * Verifies:
 *   - request method is GET (read-only, never a mutation)
 *   - allowed state: ALLOWED pill, reason text, order/fill/position cards
 *   - blocked state: BLOCKED pill, reason text, no order/fill/position created
 *   - safety chips persist after result renders
 *   - forbidden interactive controls are absent post-render
 *   - unsafe identifiers (broker_order_id, account_id, execution_id) never appear
 *   - no horizontal overflow after result renders
 *
 * Backend is NOT required. Route mocking intercepts the fetch before the
 * request reaches the network.
 *
 * Safety posture: read-only, dry-run, no broker execution.
 * No POST / PUT / PATCH / DELETE calls are made by these tests.
 */

import { expect, test, type Page } from "@playwright/test";

// ─── Constants ────────────────────────────────────────────────────────────────

const ROUTE = "/terminal/paper-run-preview";

/** Time allowed for the boot screen (~1 350 ms) + initial render. */
const PANEL_TIMEOUT = 10_000;

/** Time allowed for the mocked response to render after button click. */
const RESULT_TIMEOUT = 5_000;

/** URL glob that matches any request to the paper run preview endpoint. */
const API_PATTERN = "**/paper/run/preview**";

const SAFETY_CHIPS = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "HUMAN REVIEW REQUIRED",
  "EXECUTION OFF",
] as const;

const FORBIDDEN_BUTTONS = [
  { label: "Buy", pattern: /^Buy$/i },
  { label: "Sell", pattern: /^Sell$/i },
  { label: "Execute", pattern: /^Execute$/i },
  { label: "Place Order", pattern: /^Place Order$/i },
  { label: "Submit Order", pattern: /^Submit Order$/i },
  { label: "Live Order", pattern: /^Live Order$/i },
  { label: "Connect Live Broker", pattern: /^Connect Live Broker$/i },
] as const;

/** Strings that must never appear in page text (would indicate live broker data). */
const UNSAFE_ID_STRINGS = [
  "broker_order_id",
  "account_id",
  "execution_id",
] as const;

// ─── Safety flags (required in every mock payload) ────────────────────────────
//
// paperRunPreviewApi.ts#safetyFlagsValid() rejects the response and throws
// "Unsafe preview response rejected" if any of these are missing or wrong.
// All six flags must be present in the top-level response AND in every nested
// object (PaperRunPreviewRun, Order, Fill, Position) to match the backend shape.

const SAFETY_FLAGS = {
  paper_only: true as const,
  dry_run: true as const,
  read_only: true as const,
  live_orders_blocked: true as const,
  requires_human_review: true as const,
  execution_enabled: false as const,
};

// ─── Mock payloads ────────────────────────────────────────────────────────────

const MOCK_ALLOWED_RESPONSE = {
  ...SAFETY_FLAGS,
  allowed: true,
  reason: "All risk checks passed. Paper run simulation approved for display.",
  paper_run: {
    ...SAFETY_FLAGS,
    run_id: "test-run-001",
    started_at: "2026-05-26T12:00:00Z",
    ended_at: null,
    total_signals: 3,
    accepted_signals: 1,
    rejected_signals: 2,
    open_positions_count: 1,
    closed_positions_count: 0,
    max_risk_pct: 0.01,
    orders: [
      {
        ...SAFETY_FLAGS,
        paper_order_id: "order-test-001",
        created_at: "2026-05-26T12:00:01Z",
        symbol: "EURUSD",
        direction: "BUY",
        quantity: 1,
        entry_price: 1.1,
        stop_loss: 1.095,
        take_profit: 1.11,
        max_risk_pct: 0.01,
        status: "open",
        rejection_reason: null,
      },
    ],
    fills: [
      {
        ...SAFETY_FLAGS,
        paper_fill_id: "fill-test-001",
        paper_order_ref: "order-test-001",
        fill_timestamp: "2026-05-26T12:00:01Z",
        symbol: "EURUSD",
        direction: "BUY",
        fill_price: 1.1,
        quantity: 1,
      },
    ],
    positions: [
      {
        ...SAFETY_FLAGS,
        paper_position_id: "pos-test-001",
        paper_order_ref: "order-test-001",
        opened_at: "2026-05-26T12:00:01Z",
        closed_at: null,
        symbol: "EURUSD",
        direction: "BUY",
        quantity: 1,
        entry_price: 1.1,
        current_price: 1.1025,
        stop_loss: 1.095,
        take_profit: 1.11,
        unrealized_pnl: 25.0,
        max_risk_pct: 0.01,
        status: "open",
      },
    ],
  },
};

const MOCK_BLOCKED_RESPONSE = {
  ...SAFETY_FLAGS,
  allowed: false,
  reason:
    "Risk geometry check failed: stop-loss distance exceeds maximum permitted loss per trade.",
  paper_run: null,
};

// ─── Assertion helpers ────────────────────────────────────────────────────────

async function assertSafetyChipsVisible(page: Page): Promise<void> {
  const chipRow = page.locator('[aria-label="Paper run preview safety chips"]');
  for (const chip of SAFETY_CHIPS) {
    await expect(chipRow.getByText(chip, { exact: true })).toBeVisible();
  }
}

async function assertNoForbiddenButtons(page: Page): Promise<void> {
  for (const { pattern } of FORBIDDEN_BUTTONS) {
    await expect(page.getByRole("button", { name: pattern })).toHaveCount(0);
  }
}

async function assertNoUnsafeIds(page: Page): Promise<void> {
  const content = (await page.textContent("body")) ?? "";
  for (const id of UNSAFE_ID_STRINGS) {
    expect(content, `Page text must not contain "${id}"`).not.toContain(id);
  }
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1,
  );
  expect(hasOverflow, "horizontal overflow detected").toBe(false);
}

// ─── Suite ────────────────────────────────────────────────────────────────────

test.describe("Paper Run Preview — interaction (mocked API)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTE);
    await expect(
      page.locator('[aria-label="Paper run preview panel"]'),
    ).toBeVisible({ timeout: PANEL_TIMEOUT });
  });

  // ── 1. Allowed state ──────────────────────────────────────────────────────

  test("allowed state: GET request, result renders, safety preserved", async ({
    page,
  }) => {
    await page.route(API_PATTERN, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_ALLOWED_RESPONSE),
      });
    });

    const [request] = await Promise.all([
      page.waitForRequest(API_PATTERN),
      page
        .getByRole("button", { name: /Load Preview|Refresh Preview/ })
        .click(),
    ]);

    expect(request.method(), "request must be GET").toBe("GET");

    // Wait for the ALLOWED pill — confirms safetyFlagsValid() passed and
    // the component rendered RenderState with allowed=true.
    await expect(
      page.locator(".paper-run-preview-pill.is-allowed"),
    ).toBeVisible({ timeout: RESULT_TIMEOUT });

    // Reason text
    await expect(
      page.getByText("All risk checks passed.", { exact: false }),
    ).toBeVisible();

    // Order, fill, position detail cards
    await expect(page.getByText("Order preview")).toBeVisible();
    await expect(page.getByText("Fill preview")).toBeVisible();
    await expect(page.getByText("Position preview")).toBeVisible();

    // Safety contract section (paper_only / dry_run / … values rendered)
    await expect(page.locator(".paper-run-preview-contract")).toBeVisible();

    // Safety chips persist after result renders
    await assertSafetyChipsVisible(page);

    // No forbidden interactive controls
    await assertNoForbiddenButtons(page);

    // No horizontal overflow after result renders
    await assertNoHorizontalOverflow(page);

    // Unsafe broker/live identifiers absent from all page text
    await assertNoUnsafeIds(page);
  });

  // ── 2. Blocked state ──────────────────────────────────────────────────────

  test("blocked state: GET request, blocked pill renders, no order/fill/position created", async ({
    page,
  }) => {
    await page.route(API_PATTERN, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_BLOCKED_RESPONSE),
      });
    });

    const [request] = await Promise.all([
      page.waitForRequest(API_PATTERN),
      page
        .getByRole("button", { name: /Load Preview|Refresh Preview/ })
        .click(),
    ]);

    expect(request.method(), "request must be GET").toBe("GET");

    // Wait for the BLOCKED pill
    await expect(
      page.locator(".paper-run-preview-pill.is-blocked"),
    ).toBeVisible({ timeout: RESULT_TIMEOUT });

    // Blocked reason is displayed
    await expect(
      page.getByText("Risk geometry check failed", { exact: false }),
    ).toBeVisible();

    // paper_run is null — no order, fill, or position was created
    await expect(page.getByText("Order preview")).toHaveCount(0);
    await expect(page.getByText("Fill preview")).toHaveCount(0);
    await expect(page.getByText("Position preview")).toHaveCount(0);

    // Component-level explanation of the blocked state
    await expect(
      page.getByText("No order, fill, or position was created.", {
        exact: false,
      }),
    ).toBeVisible();

    // Safety chips persist in blocked state
    await assertSafetyChipsVisible(page);

    // No forbidden interactive controls
    await assertNoForbiddenButtons(page);

    // Unsafe broker/live identifiers absent from all page text
    await assertNoUnsafeIds(page);
  });
});
