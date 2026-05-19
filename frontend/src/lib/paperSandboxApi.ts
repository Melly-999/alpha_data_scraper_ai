// PAPER-001C / PAPER-002C — Paper sandbox preview and history API client.
//
// Wraps:
//   GET /api/paper/sandbox/preview — PAPER-001B endpoint
//   GET /api/paper/sandbox/history — PAPER-002B endpoint
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
// Types — mirror app/schemas/paper_sandbox_history.py  (PAPER-002C)
// ---------------------------------------------------------------------------

export type AuditEventType =
  | "sandbox_preview_requested"
  | "sandbox_state_created"
  | "sandbox_state_reset"
  | "ticket_draft_observed"
  | "safety_flags_checked"
  | "human_review_required"
  | "degraded_fallback_used"
  | "unknown_paper_event";

export type AuditSeverity = "info" | "warning" | "blocked";

export type PaperAuditEvent = {
  event_id: string;
  timestamp: string; // ISO 8601 UTC
  event_type: AuditEventType;
  source: string;
  severity: AuditSeverity;
  message: string;
  metadata: Record<string, unknown>;
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

export type PaperAuditHistory = {
  events: PaperAuditEvent[];
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

export type PaperHistoryApiResult =
  | { ok: true; history: PaperAuditHistory }
  | { ok: false; error: PaperSandboxApiError; fallback: PaperAuditHistory };

// ---------------------------------------------------------------------------
// Fallback history — returned when the history endpoint cannot be reached.
// All safety flags remain locked to safe values even in the fallback.
// ---------------------------------------------------------------------------

export function createFallbackAuditHistory(): PaperAuditHistory {
  return {
    events: [],
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

// ---------------------------------------------------------------------------
// GET /api/paper/sandbox/history  (PAPER-002C)
// ---------------------------------------------------------------------------

export async function getPaperSandboxHistory(): Promise<PaperHistoryApiResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}/paper/sandbox/history`, {
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
        fallback: createFallbackAuditHistory(),
      };
    }

    const history = (await response.json()) as PaperAuditHistory;
    return { ok: true, history };
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return {
        ok: false,
        error: {
          type: "timeout",
          message: `Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`,
        },
        fallback: createFallbackAuditHistory(),
      };
    }
    if (err instanceof TypeError) {
      return {
        ok: false,
        error: { type: "network", message: "Backend offline or unreachable" },
        fallback: createFallbackAuditHistory(),
      };
    }
    return {
      ok: false,
      error: {
        type: "server",
        message: err instanceof Error ? err.message : String(err),
      },
      fallback: createFallbackAuditHistory(),
    };
  } finally {
    clearTimeout(timeoutId);
  }
}
