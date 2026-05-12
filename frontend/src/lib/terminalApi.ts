export type TerminalSummary = {
  terminal: string;
  mode: "read-only";
  backend: "online" | "fallback";
  safety: SafetyState;
  broker: IBKRStatus;
  updated_at: string;
};

export type SafetyState = {
  read_only: true;
  dry_run: true;
  auto_trade: false;
  live_orders_blocked: true;
};

export type MarketItem = {
  symbol: string;
  price: number;
  change_pct: number;
  signal: "BUY" | "SELL" | "HOLD" | "WATCH";
  confidence: number;
};

export type SignalItem = {
  id: string;
  symbol: string;
  direction: "BUY" | "SELL" | "HOLD";
  confidence: number;
  timeframe: string;
  reason: string;
};

export type RiskStatus = {
  max_risk_per_trade_pct: number;
  dry_run: true;
  auto_trade: false;
  read_only: true;
  stop_loss_required: true;
  take_profit_required: true;
  live_orders_blocked: true;
};

export type RiskPolicy = {
  min_confidence: number;
  daily_loss_cap_pct: number;
  open_position_cap: number;
  execution_enabled: false;
};

export type BacktestSummary = {
  win_rate: number;
  max_drawdown_pct: number;
  profit_factor: number;
  sample_size: number;
};

export type NewsItem = {
  id: string;
  headline: string;
  source: string;
  sentiment: "positive" | "negative" | "neutral";
  impact: "high" | "medium" | "low";
  time: string;
};

export type PositionItem = {
  id: string;
  symbol: string;
  side: "long" | "short" | "flat";
  quantity: number;
  pnl: number;
  source: "paper" | "fallback";
  average_price?: number | null;
  market_price?: number | null;
  currency?: string | null;
};

export type MT5Status = {
  connected: boolean;
  mode: "synthetic" | "paper" | "offline";
  data_freshness: string;
};

export type TerminalEvent = {
  id: string;
  event: string;
  severity: "info" | "warning" | "success";
  time: string;
};

export type IBKRStatus = {
  name: "IBKR Paper";
  status: "connected" | "disconnected" | "degraded" | "paper" | "read-only";
  read_only: true;
  execution_enabled: false;
  data_freshness: string;
  latency_ms: number;
  diagnostics: string[];
  permissions: {
    market_data: "allowed";
    account_read: "allowed";
    positions_read: "allowed";
    orders: "denied";
    live_execution: "denied";
  };
};

const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_API_BASE.replace(/\/+$/, "");

const safety: SafetyState = {
  read_only: true,
  dry_run: true,
  auto_trade: false,
  live_orders_blocked: true,
};

export const fallbackIBKRStatus: IBKRStatus = {
  name: "IBKR Paper",
  status: "degraded",
  read_only: true,
  execution_enabled: false,
  data_freshness: "fallback",
  latency_ms: 0,
  diagnostics: [
    "Paper adapter is read-only",
    "Execution endpoints are disabled",
    "Fallback diagnostics active",
  ],
  permissions: {
    market_data: "allowed",
    account_read: "allowed",
    positions_read: "allowed",
    orders: "denied",
    live_execution: "denied",
  },
};

type BrokerStatusResponse = {
  connected: boolean;
  degraded: boolean;
  degraded_reason: string | null;
  read_only: true;
  execution_enabled: false;
  live_orders_blocked: true;
  latency_ms: number | null;
  safety_note: string;
};

type BrokerAccountResponse = {
  currency: string;
  cash: number;
  equity: number;
  buying_power: number;
  read_only: true;
  safety_note: string;
};

type BrokerPositionResponse = {
  symbol: string;
  quantity: number;
  average_price: number | null;
  market_price: number | null;
  unrealized_pnl: number | null;
  currency: string | null;
  read_only: true;
};

export async function getIBKRBrokerStatus(): Promise<IBKRStatus> {
  const status = await getJson<BrokerStatusResponse | null>(
    "/brokers/ibkr-paper/status",
    null,
  );

  if (!status) {
    return fallbackIBKRStatus;
  }

  return {
    name: "IBKR Paper",
    status: status.connected
      ? "connected"
      : status.degraded
        ? "degraded"
        : "disconnected",
    read_only: true,
    execution_enabled: false,
    data_freshness: status.connected ? "paper-read" : "safe-degraded",
    latency_ms: status.latency_ms ?? 0,
    diagnostics: [
      status.safety_note,
      status.degraded_reason ?? "Read-only broker status returned by GET endpoint.",
      "No order, cancel, modify, or live execution controls are exposed.",
    ],
    permissions: {
      market_data: "allowed",
      account_read: "allowed",
      positions_read: "allowed",
      orders: "denied",
      live_execution: "denied",
    },
  };
}

function joinUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(joinUrl(path), {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      return fallback;
    }

    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function getTerminalSummary(): Promise<TerminalSummary> {
  return getJson("/terminal/summary", {
    terminal: "MellyTrade V1 Terminal",
    mode: "read-only",
    backend: "fallback",
    safety,
    broker: fallbackIBKRStatus,
    updated_at: new Date().toISOString(),
  });
}

export function getMarketOverview(): Promise<MarketItem[]> {
  return getJson("/market/overview", [
    { symbol: "EURUSD", price: 1.0784, change_pct: 0.18, signal: "HOLD", confidence: 61 },
    { symbol: "GBPUSD", price: 1.2532, change_pct: -0.11, signal: "WATCH", confidence: 55 },
    { symbol: "USDJPY", price: 156.42, change_pct: 0.24, signal: "HOLD", confidence: 58 },
    { symbol: "XAUUSD", price: 2318.8, change_pct: -0.32, signal: "WATCH", confidence: 63 },
  ]);
}

export function getWatchlist(): Promise<MarketItem[]> {
  return getJson("/watchlist", [
    { symbol: "EURUSD", price: 1.0784, change_pct: 0.18, signal: "HOLD", confidence: 61 },
    { symbol: "GBPUSD", price: 1.2532, change_pct: -0.11, signal: "WATCH", confidence: 55 },
    { symbol: "USDJPY", price: 156.42, change_pct: 0.24, signal: "HOLD", confidence: 58 },
  ]);
}

export function getSignalFeed(): Promise<SignalItem[]> {
  return getJson("/signals/feed", [
    {
      id: "sig-eurusd-hold",
      symbol: "EURUSD",
      direction: "HOLD",
      confidence: 61,
      timeframe: "M5/H1",
      reason: "Mixed momentum; risk gate remains conservative.",
    },
    {
      id: "sig-xauusd-watch",
      symbol: "XAUUSD",
      direction: "HOLD",
      confidence: 63,
      timeframe: "M15/H1",
      reason: "Volatility elevated; waiting for confirmation.",
    },
  ]);
}

export function getRiskStatus(): Promise<RiskStatus> {
  return getJson("/risk/status", {
    max_risk_per_trade_pct: 1,
    dry_run: true,
    auto_trade: false,
    read_only: true,
    stop_loss_required: true,
    take_profit_required: true,
    live_orders_blocked: true,
  });
}

export function getRiskPolicy(): Promise<RiskPolicy> {
  return getJson("/risk/policy", {
    min_confidence: 70,
    daily_loss_cap_pct: 3,
    open_position_cap: 3,
    execution_enabled: false,
  });
}

export function getBacktestSummary(): Promise<BacktestSummary> {
  return getJson("/backtest/summary", {
    win_rate: 0,
    max_drawdown_pct: 0,
    profit_factor: 0,
    sample_size: 0,
  });
}

export function getNewsSentiment(): Promise<NewsItem[]> {
  return getJson("/news/sentiment", [
    {
      id: "news-fallback-1",
      headline: "Fallback sentiment active; live news unavailable.",
      source: "MellyTrade",
      sentiment: "neutral",
      impact: "low",
      time: "now",
    },
  ]);
}

export function getPositions(): Promise<PositionItem[]> {
  return getJson<BrokerPositionResponse[]>("/brokers/ibkr-paper/positions", []).then(
    (positions) =>
      positions.length > 0
        ? positions.map((position) => ({
            id: `ibkr-${position.symbol}`,
            symbol: position.symbol,
            side:
              position.quantity > 0
                ? "long"
                : position.quantity < 0
                  ? "short"
                  : "flat",
            quantity: position.quantity,
            pnl: position.unrealized_pnl ?? 0,
            source: "paper",
            average_price: position.average_price,
            market_price: position.market_price,
            currency: position.currency,
          }))
        : [
            {
              id: "flat-eurusd",
              symbol: "EURUSD",
              side: "flat",
              quantity: 0,
              pnl: 0,
              source: "fallback",
            },
          ],
  );
}

export function getMT5Status(): Promise<MT5Status> {
  return getJson("/mt5/status", {
    connected: false,
    mode: "synthetic",
    data_freshness: "fallback",
  });
}

export function getTerminalEvents(): Promise<TerminalEvent[]> {
  return getJson<{
    events: Array<{
      id: string;
      type: string;
      severity: "info" | "warning" | "success" | "error" | "safety";
      timestamp: string;
    }>;
  } | null>("/terminal/events?limit=12", null).then((feed) => {
    if (feed?.events) {
      return feed.events.map((event) => ({
        id: event.id,
        event: event.type,
        severity:
          event.severity === "error" || event.severity === "safety"
            ? "warning"
            : event.severity,
        time: new Date(event.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      }));
    }

    return [
      { id: "backend_started", event: "backend_started", severity: "success", time: "boot" },
      { id: "dry_run_active", event: "dry_run_active", severity: "success", time: "boot" },
      {
        id: "read_only_mode_confirmed",
        event: "read_only_mode_confirmed",
        severity: "success",
        time: "boot",
      },
      { id: "autotrade_disabled", event: "autotrade_disabled", severity: "success", time: "boot" },
      { id: "live_orders_blocked", event: "live_orders_blocked", severity: "success", time: "boot" },
      { id: "broker_disconnected", event: "broker_disconnected", severity: "warning", time: "boot" },
      {
        id: "ibkr_paper_disconnected",
        event: "ibkr_paper_disconnected",
        severity: "warning",
        time: "boot",
      },
      {
        id: "fallback_data_active",
        event: "fallback_data_active",
        severity: "warning",
        time: "boot",
      },
      { id: "smoke_passed", event: "smoke_passed", severity: "success", time: "boot" },
    ];
  });
}

export async function getBrokerAccountSnapshot(): Promise<BrokerAccountResponse> {
  return getJson("/brokers/ibkr-paper/account", {
    currency: "USD",
    cash: 0,
    equity: 0,
    buying_power: 0,
    read_only: true,
    safety_note: "Safe zero-valued fallback account snapshot.",
  });
}
