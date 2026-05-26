const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_API_BASE.replace(/\/+$/, "");
const API_KEY = (import.meta.env.VITE_MELLY_API_KEY ?? "") as string;
const REQUEST_TIMEOUT_MS = 15_000;

export type PaperRunPreviewParams = {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  confidence: number;
  max_risk_pct: number;
};

type PaperPreviewSafetyFlags = {
  paper_only: true;
  dry_run: true;
  read_only: true;
  live_orders_blocked: true;
  requires_human_review: true;
  execution_enabled: false;
};

export type PaperRunPreviewOrder = PaperPreviewSafetyFlags & {
  paper_order_id: string;
  created_at: string;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  max_risk_pct: number;
  status: "pending" | "open" | "closed" | "cancelled" | "rejected";
  rejection_reason: string | null;
};

export type PaperRunPreviewFill = PaperPreviewSafetyFlags & {
  paper_fill_id: string;
  paper_order_ref: string;
  fill_timestamp: string;
  symbol: string;
  direction: "BUY" | "SELL";
  fill_price: number;
  quantity: number;
};

export type PaperRunPreviewPosition = PaperPreviewSafetyFlags & {
  paper_position_id: string;
  paper_order_ref: string;
  opened_at: string;
  closed_at: string | null;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  current_price: number;
  stop_loss: number;
  take_profit: number;
  unrealized_pnl: number;
  max_risk_pct: number;
  status: "open" | "closed";
};

export type PaperRunPreviewRun = PaperPreviewSafetyFlags & {
  run_id: string;
  started_at: string;
  ended_at: string | null;
  total_signals: number;
  accepted_signals: number;
  rejected_signals: number;
  open_positions_count: number;
  closed_positions_count: number;
  max_risk_pct: number;
  orders: PaperRunPreviewOrder[];
  fills: PaperRunPreviewFill[];
  positions: PaperRunPreviewPosition[];
};

export type PaperRunPreviewResponse = PaperPreviewSafetyFlags & {
  allowed: boolean;
  reason: string;
  paper_run: PaperRunPreviewRun | null;
};

function joinUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

function appendParam(
  params: URLSearchParams,
  key: string,
  value: string | number,
): void {
  params.append(key, String(value));
}

function safetyFlagsValid(payload: PaperRunPreviewResponse): boolean {
  return (
    payload.paper_only === true &&
    payload.dry_run === true &&
    payload.read_only === true &&
    payload.live_orders_blocked === true &&
    payload.requires_human_review === true &&
    payload.execution_enabled === false
  );
}

export async function getPaperRunPreview(
  params: PaperRunPreviewParams,
): Promise<PaperRunPreviewResponse> {
  const searchParams = new URLSearchParams();
  appendParam(searchParams, "symbol", params.symbol);
  appendParam(searchParams, "side", params.side);
  appendParam(searchParams, "quantity", params.quantity);
  appendParam(searchParams, "entry_price", params.entry_price);
  appendParam(searchParams, "stop_loss", params.stop_loss);
  appendParam(searchParams, "take_profit", params.take_profit);
  appendParam(searchParams, "confidence", params.confidence);
  appendParam(searchParams, "max_risk_pct", params.max_risk_pct);

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const headers: Record<string, string> = { Accept: "application/json" };
    if (API_KEY.trim().length > 0) {
      headers["X-API-Key"] = API_KEY;
    }

    const response = await fetch(
      `${joinUrl("/paper/run/preview")}?${searchParams.toString()}`,
      {
        method: "GET",
        headers,
        credentials: "same-origin",
        signal: controller.signal,
      },
    );

    if (!response.ok) {
      throw new Error(`Server returned ${response.status} ${response.statusText}`);
    }

    const payload = (await response.json()) as PaperRunPreviewResponse;
    if (!safetyFlagsValid(payload)) {
      throw new Error("Unsafe preview response rejected");
    }

    return payload;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`);
    }
    if (error instanceof TypeError) {
      throw new Error("Backend offline or unreachable");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}
