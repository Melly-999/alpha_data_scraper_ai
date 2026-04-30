// Sprint 1A backend contracts (mellytrade_v3/mellytrade-api). These are
// kept in a separate module from the legacy `types/api.ts` shapes so the
// existing dashboard hooks/pages continue to compile while new Direction B
// surfaces consume the read-only contracts shipped in commit b76df47.
//
// READ-ONLY: nothing in this module describes a mutation. The dashboard
// must never POST signals or call execution-style endpoints from these
// types.

export type Action = "BUY" | "SELL" | "HOLD";

export type AuditEventType =
  | "signal_received"
  | "signal_accepted"
  | "signal_rejected"
  | "risk_gate_failed"
  | "cooldown_active"
  | "dry_run_active"
  | "read_only_mode_active"
  | "live_orders_blocked"
  | "mt5_connection_status";

export type AuditSeverity = "info" | "warning" | "error";
export type AlertSeverity = "info" | "warning" | "error" | "success";

export interface HealthInfo {
  status: string;
  service: string;
  version: string;
  cooldown_seconds: number;
  min_confidence: number;
  max_risk_percent: number;
  database: string;
  dry_run: boolean;
  autotrade_enabled: boolean;
  read_only: boolean;
  live_orders_blocked: boolean;
}

export interface SignalSummary {
  id: number;
  created_at: string;
  symbol: string;
  action: Action;
  confidence: number;
  confidence_clamped: number;
  risk_pct: number;
  status: string;
  reason: string;
  rejection_reason: string | null;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  source: string;
  dry_run: boolean;
  read_only: boolean;
}

export interface AuditEvent {
  type: AuditEventType;
  timestamp: string;
  severity: AuditSeverity;
  message: string;
  detail?: Record<string, unknown> | null;
  signal_id?: number | null;
}

export interface AuditFeed {
  events: AuditEvent[];
  dry_run: boolean;
  read_only: boolean;
  live_orders_blocked: boolean;
}

export interface RiskGateStatus {
  name: string;
  active: boolean;
  description: string;
}

export interface RiskConfig {
  min_confidence: number;
  max_risk_percent: number;
  cooldown_seconds: number;
  dry_run: boolean;
  autotrade_enabled: boolean;
  read_only: boolean;
  live_orders_blocked: boolean;
  gates: RiskGateStatus[];
}

export interface AlertItem {
  id: string;
  timestamp: string;
  severity: AlertSeverity;
  category: string;
  title: string;
  message: string;
  source: string;
  symbol?: string | null;
  signal_id?: number | null;
  read_only: boolean;
  metadata: Record<string, unknown>;
}

export interface SignalsQuery {
  symbol?: string;
  status?: "accepted" | "rejected";
  since?: string;
  until?: string;
  limit?: number;
}

export interface AuditQuery {
  event_type?: AuditEventType;
  limit?: number;
}

export interface AlertsQuery {
  limit?: number;
}
