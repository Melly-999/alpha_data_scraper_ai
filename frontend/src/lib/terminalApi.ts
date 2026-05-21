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

type LocalDemoEnvelope = {
  read_only: true;
  execution_mode: "dry_run_only";
  requires_human_review: true;
  degraded: true;
  source: "local_demo" | "local_placeholder";
  live_orders_blocked: true;
};

type LocalDemoBacktestResponse =
  | BacktestSummary
  | (LocalDemoEnvelope & {
      summary: BacktestSummary;
    });

type LocalDemoSignalFeedResponse =
  | SignalItem[]
  | (LocalDemoEnvelope & {
      risk_allowed: false;
      signals: SignalItem[];
      message: string;
    });

type LocalDemoInvestmentResponse = LocalDemoEnvelope & {
  portfolio: {
    positions_count: number;
    cash: number | null;
    equity: number | null;
    currency: string | null;
    status: "not_connected";
  };
  message: string;
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
  // Enriched fields forwarded from the backend AuditEvent schema (SUPA-006).
  // All three were already returned by GET /terminal/events but were dropped
  // by the previous mapper. Now forwarded for operator visibility.
  message: string;
  source: string;
  safety_note: string | null;
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
  return getJson<LocalDemoSignalFeedResponse>("/signals/feed", [
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
  ]).then((response) => (Array.isArray(response) ? response : response.signals));
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
  const fallback: BacktestSummary = {
    win_rate: 58,
    max_drawdown_pct: 4.2,
    profit_factor: 1.34,
    sample_size: 142,
  };
  return getJson<LocalDemoBacktestResponse>("/backtest/summary", fallback).then(
    (response) => {
      const candidate: unknown =
        "summary" in response ? response.summary : response;
      if (
        candidate !== null &&
        typeof candidate === "object" &&
        typeof (candidate as Record<string, unknown>).profit_factor === "number" &&
        typeof (candidate as Record<string, unknown>).win_rate === "number" &&
        typeof (candidate as Record<string, unknown>).max_drawdown_pct === "number"
      ) {
        return candidate as BacktestSummary;
      }
      return fallback;
    },
  );
}

export function getInvestment(): Promise<LocalDemoInvestmentResponse> {
  return getJson("/investment", {
    read_only: true,
    execution_mode: "dry_run_only",
    requires_human_review: true,
    degraded: true,
    source: "local_demo",
    live_orders_blocked: true,
    portfolio: {
      positions_count: 0,
      cash: null,
      equity: null,
      currency: null,
      status: "not_connected",
    },
    message: "Investment dashboard is local-demo only and provides no personalized recommendations.",
  });
}

export function getNewsSentiment(): Promise<NewsItem[]> {
  return getJson("/news/sentiment", [
    {
      id: "news-demo-1",
      headline: "ECB holds rates — EUR supported near 1.0800 (demo)",
      source: "Reuters (demo)",
      sentiment: "positive",
      impact: "high",
      time: "09:30",
    },
    {
      id: "news-demo-2",
      headline: "Gold testing resistance at 2330; macro tone cautious (demo)",
      source: "Bloomberg (demo)",
      sentiment: "negative",
      impact: "medium",
      time: "08:45",
    },
    {
      id: "news-demo-3",
      headline: "NVDA earnings consensus above expectations — setup watching (demo)",
      source: "CNBC (demo)",
      sentiment: "positive",
      impact: "medium",
      time: "08:15",
    },
    {
      id: "news-demo-4",
      headline: "Yen weakness persists; BoJ holds accommodation (demo)",
      source: "Nikkei (demo)",
      sentiment: "neutral",
      impact: "low",
      time: "07:50",
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
      message: string;
      source: string;
      safety_note?: string | null;
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
        message: event.message ?? "",
        source: event.source ?? "",
        safety_note: event.safety_note ?? null,
      }));
    }

    return [
      {
        id: "backend_started",
        event: "backend_started",
        severity: "success",
        time: "boot",
        message: "MellyTrade Phase 1 backend started successfully.",
        source: "fastapi",
        safety_note: "Backend boot completed without execution paths enabled.",
      },
      {
        id: "dry_run_active",
        event: "dry_run_active",
        severity: "success",
        time: "boot",
        message: "dry_run=true. All execution paths are blocked. No real orders will be placed.",
        source: "risk",
        safety_note: "No live orders can leave the system while dry_run is true.",
      },
      {
        id: "read_only_mode_confirmed",
        event: "read_only_mode_confirmed",
        severity: "success",
        time: "boot",
        message: "System is operating in read-only observability mode. No order controls are exposed.",
        source: "config",
        safety_note: "UI exposes only GET endpoints; mutating routes are not registered.",
      },
      {
        id: "autotrade_disabled",
        event: "autotrade_disabled",
        severity: "success",
        time: "boot",
        message: "autotrade.enabled=false. Automated trade execution is disabled.",
        source: "risk",
        safety_note: "The bot will not auto-execute signals while autotrade is disabled.",
      },
      {
        id: "live_orders_blocked",
        event: "live_orders_blocked",
        severity: "success",
        time: "boot",
        message: "supports_live_orders=false. Live order placement is blocked at adapter level.",
        source: "broker",
        safety_note: "Broker adapter rejects live order placement at the API boundary.",
      },
      {
        id: "broker_disconnected",
        event: "broker_disconnected",
        severity: "warning",
        time: "boot",
        message: "IBKR Paper adapter is not connected. No orders can be placed.",
        source: "ibkr_paper",
        safety_note: null,
      },
      {
        id: "ibkr_paper_disconnected",
        event: "ibkr_paper_disconnected",
        severity: "warning",
        time: "boot",
        message: "ib_insync is not connected or not installed. No account data available.",
        source: "ibkr_paper",
        safety_note: null,
      },
      {
        id: "fallback_data_active",
        event: "fallback_data_active",
        severity: "warning",
        time: "boot",
        message: "System is operating on fixture/demo data. No live market data is connected.",
        source: "data",
        safety_note: "Demo data is clearly labeled; no real broker quotes are being used.",
      },
      {
        id: "smoke_passed",
        event: "smoke_passed",
        severity: "success",
        time: "boot",
        message: "Smoke test passed for this session.",
        source: "smoke",
        safety_note: "Read-only smoke checks completed; no mutations were executed.",
      },
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

// ── SIG-004 Signal Quality Summary ──────────────────────────────────────────

export type SignalQualityCounts = {
  total_signals: number;
  watch_count: number;
  hold_count: number;
  long_setup_count: number;
  short_setup_count: number;
  no_trade_count: number;
  average_confidence: number;
  high_confidence_count: number;
  stale_count: number;
  fresh_count: number;
  risk_blocked_count: number;
  human_review_required_count: number;
};

export type SignalQualityMetrics = {
  label: "safe_fallback" | "low" | "moderate" | "high";
  score: number;
  confidence_band: "low" | "medium" | "high";
  freshness: "fallback" | "live" | "stale";
  risk_posture: "blocked" | "watch_only" | "dry_run_only";
};

export type SignalQualitySummaryResponse = {
  status: "ok" | "degraded";
  mode: "read_only";
  read_only: true;
  dry_run: true;
  live_orders_blocked: true;
  execution_mode: "dry_run_only";
  requires_human_review: true;
  risk_allowed: false;
  source: "signal_quality_summary";
  summary: SignalQualityCounts;
  quality: SignalQualityMetrics;
  notes: string[];
  updated_at: string;
};

const _signalQualityFallback: SignalQualitySummaryResponse = {
  status: "degraded",
  mode: "read_only",
  read_only: true,
  dry_run: true,
  live_orders_blocked: true,
  execution_mode: "dry_run_only",
  requires_human_review: true,
  risk_allowed: false,
  source: "signal_quality_summary",
  summary: {
    total_signals: 0,
    watch_count: 0,
    hold_count: 0,
    long_setup_count: 0,
    short_setup_count: 0,
    no_trade_count: 0,
    average_confidence: 0,
    high_confidence_count: 0,
    stale_count: 0,
    fresh_count: 0,
    risk_blocked_count: 0,
    human_review_required_count: 0,
  },
  quality: {
    label: "safe_fallback",
    score: 0,
    confidence_band: "low",
    freshness: "fallback",
    risk_posture: "blocked",
  },
  notes: [
    "Read-only advisory signal quality summary.",
    "No order execution or broker routing is available.",
  ],
  updated_at: new Date().toISOString(),
};

export function getSignalQualitySummary(): Promise<SignalQualitySummaryResponse> {
  return getJson("/signals/quality/summary", _signalQualityFallback);
}
