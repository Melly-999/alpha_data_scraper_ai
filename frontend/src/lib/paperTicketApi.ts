// PDS-004 — Paper-only ticket draft API client.
//
// Wraps POST /api/paper/tickets/draft — the PDS-003 endpoint.
//
// Safety contract (always enforced by the backend, mirrored here for clarity):
//   paper_only=true, dry_run=true, read_only=true, live_orders_blocked=true,
//   requires_human_review=true, risk_allowed=false,
//   broker_execution_allowed=false, max_risk_pct<=1.0
//
// This module must NEVER call broker adapters, MT5, IBKR, or any live
// execution surface.  It sends one POST to the paper-only sandbox endpoint
// and returns the advisory validation result.

const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_API_BASE.replace(/\/+$/, "");
const REQUEST_TIMEOUT_MS = 15_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type TradeSide = "long" | "short";

export type EntryType =
  | "market_simulated"
  | "limit"
  | "breakout"
  | "reversal"
  | "manual";

export type PaperTicketInput = {
  symbol: string;
  side: TradeSide;
  entry_type: EntryType;
  timeframe: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2?: number;
  risk_pct: number;
  confidence: number;
  reason: string;
  source?: string;
  setup_notes?: string;
};

export type PaperTicketDraft = {
  ticket_id: string;
  symbol: string;
  side: TradeSide;
  entry_type: EntryType;
  timeframe: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2?: number | null;
  risk_pct: number;
  confidence: number;
  reason: string;
  // Safety fields — always true/false from backend
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  requires_human_review: true;
  risk_allowed: false;
  broker_execution_allowed: false;
  execution_mode: "paper_only_draft";
};

export type PaperTicketSafetyContract = {
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  requires_human_review: true;
  risk_allowed: false;
  broker_execution_allowed: false;
  execution_mode: "paper_only_draft";
  max_risk_pct: number;
};

export type PaperTicketDraftResult = {
  accepted: boolean;
  draft: PaperTicketDraft | null;
  rejection_reasons: string[];
  warnings: string[];
  safety_contract: PaperTicketSafetyContract;
};

export type PaperTicketApiError = {
  type: "network" | "timeout" | "validation" | "server";
  message: string;
};

export type PaperTicketApiResult =
  | { ok: true; result: PaperTicketDraftResult }
  | { ok: false; error: PaperTicketApiError };

// ---------------------------------------------------------------------------
// Fallback safety contract — returned when the call cannot be completed
// ---------------------------------------------------------------------------

export function createFallbackSafetyContract(): PaperTicketSafetyContract {
  return {
    paper_only: true,
    dry_run: true,
    read_only: true,
    live_orders_blocked: true,
    requires_human_review: true,
    risk_allowed: false,
    broker_execution_allowed: false,
    execution_mode: "paper_only_draft",
    max_risk_pct: 1.0,
  };
}

// ---------------------------------------------------------------------------
// POST /api/paper/tickets/draft
// ---------------------------------------------------------------------------

export async function createPaperTicketDraft(
  input: PaperTicketInput,
): Promise<PaperTicketApiResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}/paper/tickets/draft`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify(input),
      signal: controller.signal,
    });

    if (response.status === 422) {
      let detail = "Validation error";
      try {
        const body = (await response.json()) as { detail?: unknown };
        if (Array.isArray(body.detail) && body.detail.length > 0) {
          const first = body.detail[0] as { msg?: string };
          detail = typeof first.msg === "string" ? first.msg : detail;
        }
      } catch {
        // ignore parse errors
      }
      return {
        ok: false,
        error: { type: "validation", message: detail },
      };
    }

    if (!response.ok) {
      return {
        ok: false,
        error: {
          type: "server",
          message: `Server returned ${response.status} ${response.statusText}`,
        },
      };
    }

    const result = (await response.json()) as PaperTicketDraftResult;
    return { ok: true, result };
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return {
        ok: false,
        error: {
          type: "timeout",
          message: `Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`,
        },
      };
    }
    if (err instanceof TypeError) {
      return {
        ok: false,
        error: { type: "network", message: "Backend offline or unreachable" },
      };
    }
    return {
      ok: false,
      error: {
        type: "server",
        message: err instanceof Error ? err.message : String(err),
      },
    };
  } finally {
    clearTimeout(timeoutId);
  }
}
