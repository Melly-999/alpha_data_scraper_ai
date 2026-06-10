// Read-only Alpaca Paper order preview client — ALPACA-PAPER-ORDER-PREVIEW-003.
//
// GET-only. Calls only GET /api/alpaca-paper/order-preview. No POST/PUT/PATCH/DELETE.
// Never carries credentials, API keys, tokens, account IDs, order IDs, or
// broker_order_id — the backend preview response exposes only boolean safety
// flags, a paper-scoped order preview, and a label/reason.
//
// The preview is never submitted to any broker. submitted is always false.
// paper_order_id always starts with "paper-alpaca-".
// run_id always starts with "paper-alpaca-run-".
//
// When the backend / CORS / availability fails, fetchAlpacaPaperOrderPreview
// resolves to a safe, clearly-degraded fallback rather than rejecting, so the
// UI always renders a read-only, paper-only, execution-disabled state.

import { apiGet } from "./api";

// ---------------------------------------------------------------------------
// Safety-typed interfaces
// ---------------------------------------------------------------------------

/**
 * A paper-only, never-submitted Alpaca order preview from the backend.
 *
 * All six safety fields are typed as TypeScript literals so the compiler
 * enforces the same invariants the backend enforces:
 *   paper_only             : true   (always)
 *   dry_run                : true   (always)
 *   read_only              : true   (always)
 *   live_orders_blocked    : true   (always)
 *   execution_enabled      : false  (always)
 *   requires_human_review  : true   (always)
 *   submitted              : false  (always)
 *
 * paper_order_id always starts with "paper-alpaca-".
 * run_id always starts with "paper-alpaca-run-".
 * No credential, account, live position, or broker order fields exist here.
 */
export interface AlpacaPaperPreviewOrder {
  paper_order_id: string; // "paper-alpaca-*"
  run_id: string; // "paper-alpaca-run-*"
  created_at: string;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  max_risk_pct: number;
  status: "preview";
  fill_type: "simulated";
  broker: "alpaca-paper-demo";
  submitted: false;
  label: "Preview only — not submitted";
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  execution_enabled: false;
  requires_human_review: true;
}

/**
 * Top-level response from GET /api/alpaca-paper/order-preview.
 *
 * When allowed=true, order contains the paper order preview.
 * When allowed=false, order is null and reason explains why.
 * All safety flags are always present regardless of allowed state.
 */
export interface AlpacaPaperOrderPreview {
  allowed: boolean;
  reason: string;
  order: AlpacaPaperPreviewOrder | null;
  submitted: false;
  label: "Preview only — not submitted";
  broker: "alpaca-paper-demo";
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  execution_enabled: false;
  requires_human_review: true;
}

/** Parameters for the order preview request. */
export interface AlpacaPaperOrderPreviewParams {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  max_risk_pct: number;
}

/** Client-derived connection state — not a backend field. */
export type AlpacaPaperOrderPreviewConnectionState = "connected" | "unavailable";

export interface AlpacaPaperOrderPreviewView {
  /** Derived: "connected" when the GET succeeds, "unavailable" on fallback. */
  status: AlpacaPaperOrderPreviewConnectionState;
  /** Where the data came from. */
  source: "backend" | "fallback";
  data: AlpacaPaperOrderPreview;
}

// ---------------------------------------------------------------------------
// Fallback constants
// ---------------------------------------------------------------------------

/**
 * Safe, read-only fallback used when the backend/CORS is unavailable.
 *
 * Preserves every safety flag. allowed=false indicates the preview could not
 * be generated. No credentials, account IDs, or order IDs are carried.
 */
export const ALPACA_ORDER_PREVIEW_FALLBACK: AlpacaPaperOrderPreview = {
  allowed: false,
  reason:
    "Alpaca paper order preview unavailable — showing safe read-only fallback. " +
    "No order routing. No credentials exposed.",
  order: null,
  submitted: false,
  label: "Preview only — not submitted",
  broker: "alpaca-paper-demo",
  paper_only: true,
  dry_run: true,
  read_only: true,
  live_orders_blocked: true,
  execution_enabled: false,
  requires_human_review: true,
};

// ---------------------------------------------------------------------------
// Fetch function
// ---------------------------------------------------------------------------

/**
 * Fetch the Alpaca paper order preview (GET-only) for the given params.
 *
 * Always resolves: on any failure (offline, CORS, validation, non-2xx),
 * returns the safe degraded fallback so the card never surfaces a raw error
 * and never loses its safety posture.
 *
 * The backend validates geometry and risk; allowed=false in the response
 * means the preview was blocked (not a network error).
 */
export async function fetchAlpacaPaperOrderPreview(
  params: AlpacaPaperOrderPreviewParams,
): Promise<AlpacaPaperOrderPreviewView> {
  try {
    const qs = new URLSearchParams({
      symbol: params.symbol,
      side: params.side,
      quantity: String(params.quantity),
      entry_price: String(params.entry_price),
      stop_loss: String(params.stop_loss),
      take_profit: String(params.take_profit),
      max_risk_pct: String(params.max_risk_pct),
    }).toString();
    const data = await apiGet<AlpacaPaperOrderPreview>(
      `/alpaca-paper/order-preview?${qs}`,
    );
    return { status: "connected", source: "backend", data };
  } catch {
    return {
      status: "unavailable",
      source: "fallback",
      data: ALPACA_ORDER_PREVIEW_FALLBACK,
    };
  }
}
