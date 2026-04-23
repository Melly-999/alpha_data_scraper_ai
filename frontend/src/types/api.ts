export type Direction = "BUY" | "SELL" | "HOLD";
export type Severity = "DEBUG" | "INFO" | "WARN" | "ERROR";
export type BlockedReason =
  | "COOLDOWN"
  | "LOW_CONFIDENCE"
  | "MAX_POSITIONS"
  | "EMERGENCY_STOP"
  | "DUPLICATE_SIGNAL"
  | "MISSING_PROTECTION"
  | "NO_TRADE_SIGNAL"
  | "RISK_LIMIT";

export interface AccountOverview {
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  margin_level: number;
  drawdown: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  open_positions: number;
  today_trades: number;
}

export interface RiskGateResult {
  gate: string;
  passed: boolean;
  value?: string | number | null;
  threshold?: string | number | null;
  remaining_seconds?: number | null;
  detail?: string | null;
}

export interface SignalProvenance {
  market_data_source: "mt5" | "fallback" | "synthetic" | "technical_model" | "fixture" | "backtest";
  signal_source: "mt5" | "fallback" | "synthetic" | "technical_model" | "fixture" | "backtest";
  validation_source: string;
  confidence_source: string;
  fallback: boolean;
  generated_at: string;
  cache_age_seconds: number;
}

export interface SignalSummary {
  id: string;
  symbol: string;
  direction: Direction;
  confidence: number;
  mtf_alignment: number;
  mtf_total: number;
  sentiment_score?: number | null;
  claude_status: string;
  regime: string;
  sl?: number | null;
  tp?: number | null;
  entry?: number | null;
  rr?: number | null;
  eligible: boolean;
  blocked: boolean;
  blocked_reason?: BlockedReason | null;
  cooldown_remaining?: number | null;
  timestamp: string;
}

export interface SignalDetail extends SignalSummary {
  reasoning: string;
  technicals: {
    rsi?: number | null;
    macd?: string | null;
    atr?: number | null;
    ema20?: number | null;
    ema50?: number | null;
    score?: number | null;
    inputs: string[];
  };
  timeframes: Record<string, string>;
  risk_gate_results: RiskGateResult[];
  technical_input_summary: string[];
  confidence_explainer?: string | null;
  ai_validation_status?: string | null;
  provenance: SignalProvenance;
}

export interface SignalReasoning {
  signal_id: string;
  reasoning: string;
  technical_factors: string[];
  sentiment_context?: string | null;
  claude_response?: string | null;
  risk_gate_results: RiskGateResult[];
  blocked_reason?: BlockedReason | null;
  eligible: boolean;
  confidence_explainer?: string | null;
  provenance: SignalProvenance;
}

export interface PositionSummary {
  id: string;
  ticket: number;
  symbol: string;
  direction: Direction;
  lots: number;
  open_price: number;
  current_price?: number | null;
  close_price?: number | null;
  sl?: number | null;
  tp?: number | null;
  unrealized_pnl?: number | null;
  realized_pnl?: number | null;
  duration_seconds: number;
  signal_id?: string | null;
  mt5_synced: boolean;
  open_time: string;
  close_time?: string | null;
}

export interface OrderRow {
  id: string;
  ticket: number;
  symbol: string;
  direction: Direction;
  type: string;
  lots: number;
  price: number;
  sl?: number | null;
  tp?: number | null;
  status: string;
  source: string;
  confidence?: number | null;
  slippage_pips?: number | null;
  submitted_at: string;
  filled_at?: string | null;
  notes: string;
}

export interface RiskConfig {
  max_risk_per_trade: number;
  max_daily_loss: number;
  max_drawdown: number;
  min_confidence: number;
  min_rr: number;
  max_open_positions: number;
  max_lot_size: number;
  cooldown_seconds: number;
  allow_same_signal: boolean;
  dry_run: boolean;
  auto_trade: boolean;
  emergency_pause: boolean;
}

export interface RiskConfigUpdate extends Partial<RiskConfig> {}

export interface RiskStatus {
  daily_loss_used: number;
  daily_loss_limit: number;
  drawdown_current: number;
  drawdown_limit: number;
  open_positions: number;
  open_positions_limit: number;
  trades_blocked: number;
  trades_executed: number;
  risk_exposure: number;
  emergency_pause: boolean;
}

export interface RiskViolation {
  id: string;
  type: BlockedReason;
  signal_ref?: string | null;
  reason: string;
  severity: Severity;
  timestamp: string;
}

export interface MT5Status {
  connected: boolean;
  server: string;
  account_id: string;
  account_name: string;
  broker: string;
  currency: string;
  leverage: string;
  last_heartbeat: string;
  latency_ms: number;
  symbols_loaded: number;
  orders_sync: boolean;
  positions_sync: boolean;
  build_version: string;
  fallback: boolean;
  read_only: boolean;
  data_source: string;
  terminal_path?: string | null;
  refreshed_at?: string | null;
  cache_age_seconds: number;
  connection_logs: Array<{ time: string; event: string; msg: string }>;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  category: string;
  severity: Severity;
  message: string;
}

export interface ServiceDependencyStatus {
  active: boolean;
  detail?: string | null;
  latency_ms?: number | null;
  model?: string | null;
  last_update?: string | null;
}

export interface ApiStatus {
  healthy: boolean;
  uptime: string;
  version: string;
  fallback_mode: boolean;
}

export interface SystemStatus {
  mt5: ServiceDependencyStatus;
  api: ApiStatus;
  claude: ServiceDependencyStatus;
  news: ServiceDependencyStatus;
  symbol: string;
  mode: "DRY_RUN" | "LIVE";
  last_tick: string;
  emergency_stop: boolean;
}

export interface WatchlistItem {
  symbol: string;
  bid: number;
  ask: number;
  change: number;
  signal: string;
  confidence?: number | null;
}

export interface ActivityFeedItem {
  time: string;
  type: string;
  msg: string;
  color: string;
}

export interface EquityCurvePoint {
  x: number;
  y: number;
}

export interface DashboardSummary {
  system_status: SystemStatus;
  account: AccountOverview;
  ready_signals: SignalSummary[];
  risk_status: RiskStatus;
  watchlist: WatchlistItem[];
  activity_feed: ActivityFeedItem[];
  equity_curve: EquityCurvePoint[];
  analytics_summary?: AnalyticsSummary | null;
  degraded_services: string[];
  generated_at: string;
}

export interface AnalyticsMetric {
  label: string;
  value: number;
  formatted: string;
}

export interface AnalyticsSummary {
  symbol: string;
  timeframe: string;
  total_trades: number;
  win_rate: number;
  sharpe_ratio: number;
  max_drawdown: number;
  profit_factor: number;
  total_return: number;
  source: string;
  fallback: boolean;
  generated_at: string;
  cache_age_seconds: number;
  highlights: AnalyticsMetric[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  uptime_seconds: number;
  dependencies: {
    mt5: boolean;
    claude: boolean;
    news: boolean;
  };
  fallback_mode: boolean;
  workspace: {
    repo_root: string;
    startup_mode: string;
  };
  safety: RiskConfig;
}

export interface EmergencyStopResponse {
  stopped: boolean;
  timestamp: string;
  config: RiskConfig;
  violation: RiskViolation;
}
