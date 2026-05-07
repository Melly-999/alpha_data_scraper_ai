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

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

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

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
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
  return getJson("/api/terminal/summary", {
    terminal: "MellyTrade V1 Terminal",
    mode: "read-only",
    backend: "fallback",
    safety,
    broker: fallbackIBKRStatus,
    updated_at: new Date().toISOString(),
  });
}

export function getMarketOverview(): Promise<MarketItem[]> {
  return getJson("/api/market/overview", [
    { symbol: "EURUSD", price: 1.0784, change_pct: 0.18, signal: "HOLD", confidence: 61 },
    { symbol: "GBPUSD", price: 1.2532, change_pct: -0.11, signal: "WATCH", confidence: 55 },
    { symbol: "USDJPY", price: 156.42, change_pct: 0.24, signal: "HOLD", confidence: 58 },
    { symbol: "XAUUSD", price: 2318.8, change_pct: -0.32, signal: "WATCH", confidence: 63 },
  ]);
}

export function getWatchlist(): Promise<MarketItem[]> {
  return getJson("/api/watchlist", [
    { symbol: "EURUSD", price: 1.0784, change_pct: 0.18, signal: "HOLD", confidence: 61 },
    { symbol: "GBPUSD", price: 1.2532, change_pct: -0.11, signal: "WATCH", confidence: 55 },
    { symbol: "USDJPY", price: 156.42, change_pct: 0.24, signal: "HOLD", confidence: 58 },
  ]);
}

export function getSignalFeed(): Promise<SignalItem[]> {
  return getJson("/api/signals/feed", [
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
  return getJson("/api/risk/status", {
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
  return getJson("/api/risk/policy", {
    min_confidence: 70,
    daily_loss_cap_pct: 3,
    open_position_cap: 3,
    execution_enabled: false,
  });
}

export function getBacktestSummary(): Promise<BacktestSummary> {
  return getJson("/api/backtest/summary", {
    win_rate: 0,
    max_drawdown_pct: 0,
    profit_factor: 0,
    sample_size: 0,
  });
}

export function getNewsSentiment(): Promise<NewsItem[]> {
  return getJson("/api/news/sentiment", [
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
  return getJson("/api/positions", [
    { id: "flat-eurusd", symbol: "EURUSD", side: "flat", quantity: 0, pnl: 0, source: "fallback" },
  ]);
}

export function getMT5Status(): Promise<MT5Status> {
  return getJson("/api/mt5/status", {
    connected: false,
    mode: "synthetic",
    data_freshness: "fallback",
  });
}

export function getTerminalEvents(): Promise<TerminalEvent[]> {
  return getJson("/api/terminal/events", [
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
  ]);
}
