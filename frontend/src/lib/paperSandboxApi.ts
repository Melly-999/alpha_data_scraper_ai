// PAPER-001C — Paper sandbox preview API client.
//
// Wraps GET /api/paper/sandbox/preview — the PAPER-001B endpoint.
//
// Safety contract (always enforced by the backend, mirrored here for clarity):
//   paper_only=true, dry_run=true, read_only=true, live_orders_blocked=true,
//   requires_human_review=true, risk_allowed=false,
//   broker_execution_allowed=false, execution_mode="dry_run_only"
//
// This module must NEVER call broker adapters, MT5, IBKR, or any live
// execution surface.  It only issues GET requests and returns read-only
// advisory display data.
//
// No POST, PUT, PATCH, or DELETE helpers exist in this file.
// No submit/execute/order functions exist in this file.

const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_API_BASE.replace(/\/+$/, "");
const REQUEST_TIMEOUT_MS = 10_000;

// ---------------------------------------------------------------------------
// Types — mirror app/schemas/paper_sandbox.py
// ---------------------------------------------------------------------------

export type TradeSide = "long" | "short";

export type EntryType =
  | "market_simulated"
  | "limit"
  | "breakout"
  | "reversal"
  | "manual";

export type PaperSandboxEntry = {
  sandbox_entry_id: string;
  ticket_id: string;
  symbol: string;
  side: TradeSide;
  entry_type: EntryType;
  timeframe: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number | null;
  risk_pct: number;
  confidence: number;
  reason: string;
  source: string;
  submitted_at: string;
  // Safety flags — always true/false from backend
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  requires_human_review: true;
  risk_allowed: false;
  broker_execution_allowed: false;
  execution_mode: "dry_run_only";
};

export type PaperSandboxState = {
  entries: PaperSandboxEntry[];
  count: number;
  // Safety flags — always locked to safe values
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  execution_mode: "dry_run_only";
  requires_human_review: true;
  risk_allowed: false;
  broker_execution_allowed: false;
};

export type PaperSandboxApiError = {
  type: "network" | "timeout" | "server";
  message: string;
};

export type PaperSandboxApiResult =
  | { ok: true; state: PaperSandboxState }
  | { ok: false; error: PaperSandboxApiError; fallback: PaperSandboxState };

// ---------------------------------------------------------------------------
// Fallback state — returned when the endpoint cannot be reached.
// All safety flags remain locked to safe values even in the fallback.
// ---------------------------------------------------------------------------

export function createFallbackSandboxState(): PaperSandboxState {
  return {
    entries: [],
    count: 0,
    paper_only: true,
    dry_run: true,
    read_only: true,
    live_orders_blocked: true,
    execution_mode: "dry_run_only",
    requires_human_review: true,
    risk_allowed: false,
    broker_execution_allowed: false,
  };
}

// ---------------------------------------------------------------------------
// GET /api/paper/sandbox/preview
// ---------------------------------------------------------------------------

export async function getPaperSandboxPreview(): Promise<PaperSandboxApiResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}/paper/sandbox/preview`, {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "same-origin",
      signal: controller.signal,
    });

    if (!response.ok) {
      return {
        ok: false,
        error: {
          type: "server",
          message: `Server returned ${response.status} ${response.statusText}`,
        },
        fallback: createFallbackSandboxState(),
      };
    }

    const state = (await response.json()) as PaperSandboxState;
    return { ok: true, state };
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return {
        ok: false,
        error: {
          type: "timeout",
          message: `Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`,
        },
        fallback: createFallbackSandboxState(),
      };
    }
    if (err instanceof TypeError) {
      return {
        ok: false,
        error: { type: "network", message: "Backend offline or unreachable" },
        fallback: createFallbackSandboxState(),
      };
    }
    return {
      ok: false,
      error: {
        type: "server",
        message: err instanceof Error ? err.message : String(err),
      },
      fallback: createFallbackSandboxState(),
    };
  } finally {
    clearTimeout(timeoutId);
  }
}
