// Read-only Alpaca Paper status client — ALPACA-PAPER-READONLY-CARD-001.
//
// GET-only. Calls only GET /api/alpaca-paper/status. No POST/PUT/PATCH/DELETE.
// Never carries credentials, API keys, tokens, account IDs, order IDs, or
// broker_order_id — the backend status response intentionally exposes only
// boolean safety flags plus a message/version/feature list.
//
// When the hosted backend / CORS / availability fails, fetchAlpacaPaperStatusView
// resolves to a safe, clearly-degraded fallback rather than rejecting, so the
// UI always renders a read-only, paper-only, execution-disabled state.

import { apiGet } from "./api";

/**
 * Safe status snapshot from the backend Alpaca Paper demo endpoint.
 *
 * Mirrors the AlpacaPaperStatus Pydantic schema in
 * app/schemas/alpaca_paper.py. The six safety fields are typed as TypeScript
 * literals so the compiler enforces the same invariants the backend enforces:
 *   paper_only             : true   (always)
 *   dry_run                : true   (always)
 *   read_only              : true   (always)
 *   live_orders_blocked    : true   (always)
 *   execution_enabled      : false  (always)
 *   requires_human_review  : true   (always)
 *
 * No credential, account, position, or order fields exist on this shape.
 */
export interface AlpacaPaperStatus {
  message: string;
  version: string;
  features: string[];
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  execution_enabled: false;
  requires_human_review: true;
}

/** Client-derived connection state — not a backend field. */
export type AlpacaPaperConnectionState = "connected" | "unavailable";

export interface AlpacaPaperStatusView {
  /** Derived: "connected" when the GET succeeds, "unavailable" on fallback. */
  status: AlpacaPaperConnectionState;
  /** Where the data came from. */
  source: "backend" | "fallback";
  data: AlpacaPaperStatus;
}

/**
 * Safe, read-only fallback used when the backend/CORS is unavailable.
 *
 * Preserves every safety flag. Carries no credentials, account IDs, order IDs,
 * positions, or buying power. This is mock-safe demo status only.
 */
export const ALPACA_PAPER_FALLBACK: AlpacaPaperStatus = {
  message:
    "Alpaca Paper status unavailable — showing safe read-only fallback. " +
    "No order routing. No credentials exposed.",
  version: "0.0.0",
  features: [],
  paper_only: true,
  dry_run: true,
  read_only: true,
  live_orders_blocked: true,
  execution_enabled: false,
  requires_human_review: true,
};

/**
 * Fetch the Alpaca Paper status (GET-only) and wrap it in a view model.
 *
 * Always resolves: on any failure (offline, CORS, stale/old hosted backend,
 * non-2xx), it returns the safe degraded fallback so the card never surfaces
 * a raw error and never loses its safety posture.
 */
export async function fetchAlpacaPaperStatusView(): Promise<AlpacaPaperStatusView> {
  try {
    const data = await apiGet<AlpacaPaperStatus>("/alpaca-paper/status");
    return { status: "connected", source: "backend", data };
  } catch {
    return { status: "unavailable", source: "fallback", data: ALPACA_PAPER_FALLBACK };
  }
}
