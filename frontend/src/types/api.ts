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
  };
  timeframes: Record<string, string>;
  risk_gate_results: RiskGateResult[];
}

export interface SignalReasoning {
  signal_id: string;
  reasoning: string;
  technical_factors: string[];
  sentiment_context?: string | null;
  claude_response?: string | null;
  risk_gate_results: RiskGateResult[];
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
  generated_at: string;
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
  safety: RiskConfig;
}

export type LocalChecklistStatus = "pass" | "warn" | "fail";

export interface LocalChecklistCheck {
  id: string;
  label: string;
  status: LocalChecklistStatus;
  detail: string;
}

export interface LocalChecklistSummary {
  dry_run: boolean;
  auto_trade: boolean;
  supports_live_orders: boolean;
  live_orders_blocked: boolean;
  broker_status: string;
  broker_mode: string;
  broker_connected: boolean;
  broker_read_only: boolean;
}

export interface LocalChecklistResponse {
  status: "ok" | "degraded";
  service: string;
  checks: LocalChecklistCheck[];
  summary: LocalChecklistSummary;
}

export interface BrokerHealthResponse {
  adapter: string;
  mode: string;
  connected: boolean;
  host: string;
  port: number;
  client_id: number;
  read_only: boolean;
  supports_live_orders: boolean;
  last_error?: string | null;
  status: string;
  timestamp: string;
}

export interface BrokerAccountResponse {
  adapter: string;
  connected: boolean;
  account?: string | null;
  currency: string;
  net_liquidation: number;
  cash: number;
  buying_power: number;
  last_error?: string | null;
  timestamp: string;
}

export interface EmergencyStopResponse {
  stopped: boolean;
  timestamp: string;
  config: RiskConfig;
  violation: RiskViolation;
}

export type AuditSeverity = "info" | "success" | "warning" | "error" | "safety";

export interface AuditEvent {
  id: string;
  timestamp: string;
  type: string;
  severity: AuditSeverity;
  source: string;
  message: string;
  read_only: boolean;
  /**
   * Optional one-sentence safety explanation surfaced by the backend.
   * Older fixtures and pre-Task-2 backends may omit it, so the frontend
   * always treats it as optional and renders a fallback when absent.
   */
  safety_note?: string | null;
  metadata: Record<string, unknown>;
}

export interface AuditEventFeedResponse {
  dry_run: boolean;
  auto_trade: boolean;
  read_only: boolean;
  events: AuditEvent[];
  degraded: boolean;
  fallback: boolean;
  generated_at: string;
}

export type DecisionType =
  | "dry_run_allowed"
  | "blocked"
  | "watch_only"
  | "no_action";
export type DecisionRiskStatus = "pass" | "warn" | "blocked" | "unknown";
export type DecisionDirection = "BUY" | "SELL" | "HOLD" | "UNKNOWN";

export interface SignalDecisionRecord {
  id: string;
  timestamp: string;
  symbol: string;
  direction: DecisionDirection;
  confidence: number;
  source: string;
  strategy: string;
  risk_status: DecisionRiskStatus;
  decision: DecisionType;
  blocked_reason?: string | null;
  dry_run: boolean;
  auto_trade: boolean;
  read_only: boolean;
  stop_loss_required: boolean;
  take_profit_required: boolean;
  max_risk_per_trade: number;
  metadata: Record<string, unknown>;
}

export interface SignalDecisionHistoryResponse {
  dry_run: boolean;
  auto_trade: boolean;
  read_only: boolean;
  total: number;
  decisions: SignalDecisionRecord[];
  generated_at: string;
  degraded: boolean;
  fallback: boolean;
}

export type SignalLifecycleStepKey =
  | "signal_received"
  | "confidence_checked"
  | "risk_checked"
  | "broker_safety_checked"
  | "dry_run_decision"
  | "blocked_or_allowed_reason"
  | "audit_event_reference";
export type SignalLifecycleStepStatus =
  | "received"
  | "passed"
  | "blocked"
  | "allowed"
  | "recorded"
  | "skipped";

export interface SignalLifecycleStep {
  key: SignalLifecycleStepKey;
  label: string;
  status: SignalLifecycleStepStatus;
  detail: string;
  audit_event_id?: string | null;
}

export interface SignalLifecycleRecord {
  id: string;
  signal_id: string;
  decision_id: string;
  audit_event_id: string;
  timestamp: string;
  symbol: string;
  direction: DecisionDirection;
  confidence: number;
  decision: DecisionType;
  risk_status: DecisionRiskStatus;
  blocked_reason?: string | null;
  dry_run: boolean;
  auto_trade: boolean;
  read_only: boolean;
  supports_live_orders: boolean;
  dry_run_allowed: boolean;
  order_placed: boolean;
  max_risk_per_trade: number;
  steps: SignalLifecycleStep[];
}

export interface SignalLifecycleResponse {
  dry_run: boolean;
  auto_trade: boolean;
  read_only: boolean;
  supports_live_orders: boolean;
  total: number;
  lifecycle: SignalLifecycleRecord[];
  generated_at: string;
  degraded: boolean;
  fallback: boolean;
}
