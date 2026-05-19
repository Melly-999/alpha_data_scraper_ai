// PAPER-002C — Paper Sandbox Activity / Audit Rail panel.
//
// Read-only display panel for GET /api/paper/sandbox/history (PAPER-002B).
// Polls the endpoint every 20 seconds and on mount.
//
// Safety invariants enforced here:
//   - No execute/order-placement buttons.
//   - No broker/MT5/IBKR calls.
//   - No live trading surfaces.
//   - No POST/PUT/PATCH/DELETE requests.
//   - All UI copy makes the paper-only advisory posture clear.
//   - Safety flags are always visible regardless of history state.

import { useCallback, useEffect, useState } from "react";

import {
  createFallbackAuditHistory,
  getPaperSandboxHistory,
  type PaperAuditEvent,
  type PaperAuditHistory,
  type PaperHistoryApiResult,
} from "../../lib/paperSandboxApi";

const POLL_INTERVAL_MS = 20_000;

// ---------------------------------------------------------------------------
// Severity chip colour classes
// ---------------------------------------------------------------------------

const SEVERITY_CLASS: Record<string, string> = {
  info:    "audit-severity--info",
  warning: "audit-severity--warning",
  blocked: "audit-severity--blocked",
};

// ---------------------------------------------------------------------------
// Small presentational helpers
// ---------------------------------------------------------------------------

function AuditSafetyBadges() {
  return (
    <div className="scanner-badge-row" aria-label="Audit rail safety badges">
      <span className="scanner-preview-badge">READ ONLY</span>
      <span className="scanner-preview-badge">DRY RUN</span>
      <span className="scanner-preview-badge">LIVE ORDERS BLOCKED</span>
      <span className="scanner-preview-badge">BROKER DISABLED</span>
      <span className="scanner-preview-badge">HUMAN REVIEW</span>
    </div>
  );
}

function AuditSafetyContractRow({ history }: { history: PaperAuditHistory }) {
  return (
    <div className="paper-audit-contract" aria-label="Audit history safety contract snapshot">
      <div className="workspace-section-head">
        <span>Safety contract</span>
        <span>always enforced</span>
      </div>
      <div className="rail-metric">
        <span>paper_only</span>
        <strong>{String(history.paper_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>dry_run</span>
        <strong>{String(history.dry_run)}</strong>
      </div>
      <div className="rail-metric">
        <span>read_only</span>
        <strong>{String(history.read_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>live_orders_blocked</span>
        <strong>{String(history.live_orders_blocked)}</strong>
      </div>
      <div className="rail-metric">
        <span>broker_execution_allowed</span>
        <strong>{String(history.broker_execution_allowed)}</strong>
      </div>
      <div className="rail-metric">
        <span>risk_allowed</span>
        <strong>{String(history.risk_allowed)}</strong>
      </div>
      <div className="rail-metric">
        <span>execution_mode</span>
        <strong>{history.execution_mode}</strong>
      </div>
      <div className="rail-metric">
        <span>requires_human_review</span>
        <strong>{String(history.requires_human_review)}</strong>
      </div>
    </div>
  );
}

function AuditEventRow({ event }: { event: PaperAuditEvent }) {
  const severityClass = SEVERITY_CLASS[event.severity] ?? "audit-severity--info";
  const metaKeys = Object.keys(event.metadata);

  return (
    <article
      className="paper-audit-event-row"
      aria-label={`Audit event — ${event.event_type} (${event.severity})`}
    >
      <div className="paper-audit-event-topline">
        <span className={`paper-audit-severity ${severityClass}`}>
          {event.severity.toUpperCase()}
        </span>
        <span className="paper-audit-event-type">{event.event_type}</span>
        <span className="paper-audit-event-ts">{event.timestamp.replace("T", " ").slice(0, 19)} UTC</span>
      </div>
      <p className="paper-audit-event-message">{event.message}</p>
      <div className="paper-audit-event-meta">
        <span className="paper-audit-event-source">src: {event.source}</span>
        {metaKeys.length > 0 && (
          <span className="paper-audit-event-metakeys">
            {metaKeys.slice(0, 3).join(", ")}
            {metaKeys.length > 3 && ` +${metaKeys.length - 3} more`}
          </span>
        )}
      </div>
    </article>
  );
}

function AuditErrorBanner({ message }: { message: string }) {
  return (
    <div className="paper-audit-error" role="alert">
      <strong>Audit history unavailable</strong>
      <p>{message}</p>
      <p className="workspace-scanner-copy">
        Safety posture is unchanged. No broker execution. History endpoint is
        offline or unreachable — advisory mode remains active.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main panel
// ---------------------------------------------------------------------------

export function PaperSandboxActivityRail() {
  const [apiResult, setApiResult] = useState<PaperHistoryApiResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const fetchHistory = useCallback(async () => {
    const result = await getPaperSandboxHistory();
    setApiResult(result);
    setLastRefreshed(new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC");
    setLoading(false);
  }, []);

  // Fetch on mount + poll every 20 s
  useEffect(() => {
    void fetchHistory();
    const intervalId = setInterval(() => { void fetchHistory(); }, POLL_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [fetchHistory]);

  const displayHistory: PaperAuditHistory =
    apiResult?.ok === true
      ? apiResult.history
      : apiResult?.ok === false
        ? apiResult.fallback
        : createFallbackAuditHistory();

  // Newest-first display order
  const displayEvents = [...displayHistory.events].reverse();

  return (
    <section
      className="workspace-rail-section paper-audit-rail"
      aria-label="Paper sandbox audit/activity history — read-only, advisory only"
    >
      <div className="workspace-section-head">
        <span>Paper Sandbox Activity / Audit Rail</span>
        <span>GET-only · audit history only</span>
      </div>

      <p className="workspace-scanner-copy">
        PAPER-002B audit history (GET /api/paper/sandbox/history). Read-only
        display. No broker execution. No MT5/IBKR calls. No live order placement.
        Human review always required.
      </p>

      <AuditSafetyBadges />

      <div className="paper-audit-meta" aria-label="Audit history status summary">
        <div className="rail-metric">
          <span>Endpoint</span>
          <strong className="paper-audit-endpoint">
            GET /api/paper/sandbox/history
          </strong>
        </div>
        <div className="rail-metric">
          <span>Events</span>
          <strong aria-live="polite">
            {loading ? "—" : displayHistory.count}
          </strong>
        </div>
        {lastRefreshed && (
          <div className="rail-metric">
            <span>Last refreshed</span>
            <strong className="paper-audit-ts">{lastRefreshed}</strong>
          </div>
        )}
      </div>

      {loading && (
        <div className="paper-audit-loading" aria-live="polite">
          Loading audit history…
        </div>
      )}

      {!loading && apiResult?.ok === false && (
        <AuditErrorBanner message={apiResult.error.message} />
      )}

      {!loading && (
        <AuditSafetyContractRow history={displayHistory} />
      )}

      {!loading && apiResult?.ok === true && displayHistory.count === 0 && (
        <div className="paper-audit-empty" aria-live="polite">
          No audit events recorded yet. Advisory mode remains active.
        </div>
      )}

      {!loading && apiResult?.ok === true && displayEvents.length > 0 && (
        <div className="paper-audit-events" aria-label="Audit event history">
          <div className="workspace-section-head">
            <span>Recent events</span>
            <span>newest first · audit only · no execution</span>
          </div>
          {displayEvents.map((event) => (
            <AuditEventRow key={event.event_id} event={event} />
          ))}
        </div>
      )}

      <p className="workspace-scanner-copy paper-audit-footer">
        Audit history only · no broker execution · no MT5/IBKR calls ·
        display-only · advisory mode
      </p>
    </section>
  );
}
