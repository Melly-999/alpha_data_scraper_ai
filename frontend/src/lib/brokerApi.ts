// frontend/src/lib/brokerApi.ts
//
// BRK-012 — read-only TypeScript client for the new GET-only broker
// endpoints landed in PR #68 (BRK-008..011):
//
//   GET /api/brokers
//   GET /api/brokers/{adapter_id}/status
//   GET /api/brokers/{adapter_id}/account
//   GET /api/brokers/{adapter_id}/positions
//
// Every function on this surface is read-only by construction:
//
//   * uses the existing `apiGet` helper from `./api` (GET only),
//   * carries no body and never mutates server state,
//   * exposes no `placeOrder` / `submitOrder` / `cancelOrder` /
//     `modifyOrder` / `executeTrade` / `enableAutotrade` /
//     `disableDryRun` / `brokerExecute` style entry point.
//
// The TypeScript types mirror `app/schemas/broker.py` (BRK-003) for the
// four typed schemas. Backend-validated safety flags (`read_only`,
// `execution_enabled`, `live_orders_blocked`) are part of the response
// shape so the UI can render them as locked, surface-only values.

import { apiGet } from "./api";

export interface BrokerCapabilities {
  read_only: boolean;
  paper: boolean;
  execution_enabled: boolean;
  live_orders_blocked: boolean;
  can_place_orders: boolean;
  can_cancel_orders: boolean;
  can_modify_orders: boolean;
  supports_account_snapshot: boolean;
  supports_positions: boolean;
  safety_note: string;
}

export interface BrokerStatus {
  adapter_id: string;
  connected: boolean;
  degraded: boolean;
  degraded_reason: string | null;
  read_only: boolean;
  execution_enabled: boolean;
  live_orders_blocked: boolean;
  last_heartbeat: string | null;
  latency_ms: number | null;
  safety_note: string;
}

export interface BrokerAccountSnapshot {
  adapter_id: string;
  currency: string;
  cash: number;
  equity: number;
  buying_power: number;
  read_only: boolean;
  safety_note: string;
  as_of: string | null;
}

export interface BrokerPosition {
  adapter_id: string;
  symbol: string;
  quantity: number;
  average_price: number | null;
  market_price: number | null;
  unrealized_pnl: number | null;
  currency: string | null;
  read_only: boolean;
  safety_note: string | null;
}

export interface BrokerListItem {
  adapter_id: string;
  capabilities: BrokerCapabilities;
}

export interface BrokerListResponse {
  default_adapter_id: string;
  adapters: BrokerListItem[];
}

// ---------------------------------------------------------------------------
// GET clients. Every entry below is GET-only.
//
// No mutation helpers, no order helpers, no execute helpers. Adding any
// of those here would also be caught by the repo-wide forbidden-name
// scans on the backend side; this surface mirrors that contract on the
// frontend.
// ---------------------------------------------------------------------------

export function getBrokers(): Promise<BrokerListResponse> {
  return apiGet<BrokerListResponse>("/brokers");
}

export function getBrokerStatus(adapterId: string): Promise<BrokerStatus> {
  return apiGet<BrokerStatus>(
    `/brokers/${encodeURIComponent(adapterId)}/status`,
  );
}

export function getBrokerAccount(
  adapterId: string,
): Promise<BrokerAccountSnapshot> {
  return apiGet<BrokerAccountSnapshot>(
    `/brokers/${encodeURIComponent(adapterId)}/account`,
  );
}

export function getBrokerPositions(
  adapterId: string,
): Promise<BrokerPosition[]> {
  return apiGet<BrokerPosition[]>(
    `/brokers/${encodeURIComponent(adapterId)}/positions`,
  );
}
