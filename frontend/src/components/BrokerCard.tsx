// frontend/src/components/BrokerCard.tsx
//
// BRK-013 — read-only broker card. Renders the read-only state of a
// single broker adapter exposed by the GET-only `/api/brokers/...`
// surface (BRK-008..011):
//
//   * adapter id
//   * connected / degraded state
//   * read-only / execution-disabled / live-orders-blocked badges
//   * account snapshot (cash, equity, buying power, currency)
//   * positions count
//   * safety note from the backend
//
// The component is intentionally **display-only**: no place-order button,
// no cancel button, no execute / submit / autotrade / connect-live CTA,
// no credential input, no account-id display. The optional "Refresh"
// button only re-issues GET calls — it never mutates backend state.
//
// Data is fetched on mount via the GET-only `brokerApi` client. A small
// "loading" / "error" / "empty" wrapper is rendered inline to match the
// existing `ResourceState` look without forcing this card to depend on
// the polling-resource hook (the card is intended to be embeddable in
// pages that may already manage their own refresh cadence).

import { useCallback, useEffect, useState } from "react";

import { Badge } from "./shared/Badge";
import { Card } from "./shared/Card";
import {
  getBrokerAccount,
  getBrokerPositions,
  getBrokerStatus,
  type BrokerAccountSnapshot,
  type BrokerCapabilities,
  type BrokerPosition,
  type BrokerStatus,
} from "../lib/brokerApi";

export interface BrokerCardProps {
  /**
   * Adapter id to display. Today this is always ``"safe-disconnected"``
   * for the default registry; future read-only adapters (MT5 read-only,
   * IBKR Paper read-only) will register additional ids.
   */
  adapterId: string;
  /**
   * Optional pre-fetched capabilities (from `getBrokers()`). When
   * provided the card avoids re-issuing a list call; it never falls
   * back to anything that mutates state.
   */
  capabilities?: BrokerCapabilities | null;
  /** Optional title override. Defaults to `Broker: {adapterId}`. */
  title?: string;
}

interface BrokerCardData {
  status: BrokerStatus | null;
  account: BrokerAccountSnapshot | null;
  positions: BrokerPosition[] | null;
}

function formatMoney(amount: number, currency: string): string {
  return `${currency} ${amount.toFixed(2)}`;
}

export function BrokerCard({
  adapterId,
  capabilities = null,
  title,
}: BrokerCardProps) {
  const [data, setData] = useState<BrokerCardData>({
    status: null,
    account: null,
    positions: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Three GETs in parallel; none mutate backend state.
      const [status, account, positions] = await Promise.all([
        getBrokerStatus(adapterId),
        getBrokerAccount(adapterId),
        getBrokerPositions(adapterId),
      ]);
      setData({ status, account, positions });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [adapterId]);

  useEffect(() => {
    void load();
  }, [load]);

  const headerTitle = title ?? `Broker: ${adapterId}`;
  const refresh = (
    // Refresh re-issues the same three GETs. It does not mutate backend
    // state and is not a "connect" or "execute" affordance.
    <button
      type="button"
      className="card-refresh"
      onClick={() => {
        void load();
      }}
      disabled={loading}
      aria-label={`Refresh broker ${adapterId}`}
    >
      Refresh
    </button>
  );

  if (error) {
    return (
      <Card title={headerTitle} right={refresh}>
        <div
          className="resource-state resource-state-error broker-card-error"
          role="alert"
        >
          <div className="resource-state-title">Broker unavailable</div>
          <div className="resource-state-detail">{error}</div>
          <div className="resource-state-meta">
            No orders can be placed from this view.
          </div>
        </div>
      </Card>
    );
  }

  if (loading && !data.status) {
    return (
      <Card title={headerTitle} right={refresh}>
        <div className="resource-state resource-state-loading" role="status">
          <div className="resource-state-title">Loading …</div>
          <div className="resource-state-detail">
            Fetching read-only broker state.
          </div>
        </div>
      </Card>
    );
  }

  const status = data.status;
  const account = data.account;
  const positions = data.positions ?? [];

  // Safety pillars displayed as badges. These mirror backend-enforced
  // invariants (BRK-003 schemas + safety-status pillars); the UI cannot
  // toggle them.
  const connectedTone = status?.connected ? "green" : "amber";
  const connectedLabel = status?.connected
    ? "Connected"
    : status?.degraded
      ? "Disconnected"
      : "Offline";

  const safetyNote =
    status?.safety_note ??
    capabilities?.safety_note ??
    account?.safety_note ??
    "Read-only broker view.";

  return (
    <Card title={headerTitle} right={refresh}>
      <div className="broker-card">
        <div className="broker-card-badges">
          <Badge tone={connectedTone}>{connectedLabel}</Badge>
          <Badge tone="green">Read only</Badge>
          <Badge tone="green">Execution disabled</Badge>
          <Badge tone="amber">Live orders blocked</Badge>
          {status?.degraded ? <Badge tone="amber">Degraded</Badge> : null}
        </div>

        <div className="broker-grid broker-grid-v2">
          <span>Adapter</span>
          <strong>{adapterId}</strong>
          <span>Connected</span>
          <strong>{status?.connected ? "true" : "false"}</strong>
          <span>Read only</span>
          <strong>{status?.read_only === false ? "false" : "true"}</strong>
          <span>Execution enabled</span>
          <strong>{status?.execution_enabled ? "true" : "false"}</strong>
          <span>Live orders blocked</span>
          <strong className="danger-text">
            {status?.live_orders_blocked === false ? "false" : "BLOCKED"}
          </strong>
          {status?.degraded_reason ? (
            <>
              <span>Degraded reason</span>
              <strong>{status.degraded_reason}</strong>
            </>
          ) : null}
          {account ? (
            <>
              <span>Currency</span>
              <strong>{account.currency}</strong>
              <span>Cash</span>
              <strong>{formatMoney(account.cash, account.currency)}</strong>
              <span>Equity</span>
              <strong>{formatMoney(account.equity, account.currency)}</strong>
              <span>Buying power</span>
              <strong>
                {formatMoney(account.buying_power, account.currency)}
              </strong>
            </>
          ) : null}
          <span>Positions</span>
          <strong>{positions.length}</strong>
        </div>

        <div className="dashboard-safe-note broker-card-safety-note">
          <div className="broker-status-headline">Safety</div>
          <div>{safetyNote}</div>
        </div>
      </div>
    </Card>
  );
}
