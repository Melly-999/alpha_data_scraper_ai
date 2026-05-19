// PAPER-001C — Paper Sandbox Preview Panel (AI Workspace).
//
// Read-only display panel for GET /api/paper/sandbox/preview (PAPER-001B).
// Polls the endpoint every 20 seconds and on mount.
//
// Safety invariants enforced here:
//   - No execute/order-placement buttons.
//   - No broker/MT5/IBKR calls.
//   - No live trading surfaces.
//   - No POST/PUT/PATCH/DELETE requests.
//   - All UI copy makes the paper-only advisory posture clear.
//   - Safety flags are always visible regardless of sandbox state.

import { useCallback, useEffect, useState } from "react";

import {
  createFallbackSandboxState,
  getPaperSandboxPreview,
  type PaperSandboxApiResult,
  type PaperSandboxEntry,
  type PaperSandboxState,
} from "../../lib/paperSandboxApi";

const POLL_INTERVAL_MS = 20_000;

// ---------------------------------------------------------------------------
// Small presentational helpers
// ---------------------------------------------------------------------------

function SandboxSafetyBadges() {
  return (
    <div className="scanner-badge-row" aria-label="Paper sandbox safety badges">
      <span className="scanner-preview-badge">READ ONLY</span>
      <span className="scanner-preview-badge">DRY RUN</span>
      <span className="scanner-preview-badge">LIVE ORDERS BLOCKED</span>
      <span className="scanner-preview-badge">BROKER DISABLED</span>
      <span className="scanner-preview-badge">HUMAN REVIEW</span>
    </div>
  );
}

function SafetyContractRow({ state }: { state: PaperSandboxState }) {
  return (
    <div className="paper-sandbox-contract" aria-label="Safety contract snapshot">
      <div className="workspace-section-head">
        <span>Safety contract</span>
        <span>always enforced</span>
      </div>
      <div className="rail-metric">
        <span>paper_only</span>
        <strong>{String(state.paper_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>dry_run</span>
        <strong>{String(state.dry_run)}</strong>
      </div>
      <div className="rail-metric">
        <span>read_only</span>
        <strong>{String(state.read_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>live_orders_blocked</span>
        <strong>{String(state.live_orders_blocked)}</strong>
      </div>
      <div className="rail-metric">
        <span>broker_execution_allowed</span>
        <strong>{String(state.broker_execution_allowed)}</strong>
      </div>
      <div className="rail-metric">
        <span>risk_allowed</span>
        <strong>{String(state.risk_allowed)}</strong>
      </div>
      <div className="rail-metric">
        <span>execution_mode</span>
        <strong>{state.execution_mode}</strong>
      </div>
      <div className="rail-metric">
        <span>requires_human_review</span>
        <strong>{String(state.requires_human_review)}</strong>
      </div>
    </div>
  );
}

function SandboxEntryCard({ entry }: { entry: PaperSandboxEntry }) {
  return (
    <article
      className="paper-sandbox-entry-card"
      aria-label={`Paper sandbox entry — ${entry.symbol} ${entry.side.toUpperCase()}`}
    >
      <div className="paper-sandbox-entry-topline">
        <div>
          <p className="terminal-eyebrow">Sandbox preview entry</p>
          <strong>{entry.symbol}</strong>
        </div>
        <span className="paper-sandbox-entry-side">
          {entry.side.toUpperCase()}
        </span>
      </div>
      <div className="rail-metric">
        <span>Ticket ID</span>
        <strong className="paper-sandbox-entry-id">{entry.ticket_id}</strong>
      </div>
      <div className="rail-metric">
        <span>Entry type</span>
        <strong>{entry.entry_type}</strong>
      </div>
      <div className="rail-metric">
        <span>Timeframe</span>
        <strong>{entry.timeframe}</strong>
      </div>
      <div className="rail-metric">
        <span>Entry price</span>
        <strong>{entry.entry_price}</strong>
      </div>
      <div className="rail-metric">
        <span>Stop loss</span>
        <strong>{entry.stop_loss}</strong>
      </div>
      <div className="rail-metric">
        <span>Take profit 1</span>
        <strong>{entry.take_profit_1}</strong>
      </div>
      <div className="rail-metric">
        <span>Risk %</span>
        <strong>{entry.risk_pct}%</strong>
      </div>
      <div className="rail-metric">
        <span>Confidence</span>
        <strong>{entry.confidence}%</strong>
      </div>
      <div className="rail-metric">
        <span>Submitted</span>
        <strong className="paper-sandbox-entry-ts">{entry.submitted_at}</strong>
      </div>
      <div className="scanner-preview-badges" aria-label="Entry safety flags">
        <span className="scanner-preview-badge">PAPER ONLY</span>
        <span className="scanner-preview-badge">DRY RUN</span>
        <span className="scanner-preview-badge">NO EXECUTION</span>
      </div>
    </article>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="paper-sandbox-error" role="alert">
      <strong>Preview unavailable</strong>
      <p>{message}</p>
      <p className="workspace-scanner-copy">
        Safety posture is unchanged. No broker execution. Sandbox is offline or
        unreachable — advisory mode remains active.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main panel
// ---------------------------------------------------------------------------

export function PaperSandboxPreviewPanel() {
  const [apiResult, setApiResult] = useState<PaperSandboxApiResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const fetchState = useCallback(async () => {
    const result = await getPaperSandboxPreview();
    setApiResult(result);
    setLastRefreshed(new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC");
    setLoading(false);
  }, []);

  // Fetch on mount + poll every 20 s
  useEffect(() => {
    void fetchState();
    const intervalId = setInterval(() => { void fetchState(); }, POLL_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [fetchState]);

  const displayState: PaperSandboxState =
    apiResult?.ok === true
      ? apiResult.state
      : apiResult?.ok === false
        ? apiResult.fallback
        : createFallbackSandboxState();

  return (
    <section
      className="workspace-rail-section paper-sandbox-preview-panel"
      aria-label="Paper sandbox preview — read-only, advisory only"
    >
      <div className="workspace-section-head">
        <span>Paper Sandbox Preview</span>
        <span>GET-only · sandbox preview only</span>
      </div>

      <p className="workspace-scanner-copy">
        PAPER-001B sandbox state (GET /api/paper/sandbox/preview). Read-only
        display. No broker execution. No MT5/IBKR calls. No live order placement.
        Human review always required.
      </p>

      <SandboxSafetyBadges />

      <div className="paper-sandbox-meta" aria-label="Sandbox status summary">
        <div className="rail-metric">
          <span>Endpoint</span>
          <strong className="paper-sandbox-endpoint">
            GET /api/paper/sandbox/preview
          </strong>
        </div>
        <div className="rail-metric">
          <span>Entries</span>
          <strong aria-live="polite">
            {loading ? "—" : displayState.count}
          </strong>
        </div>
        {lastRefreshed && (
          <div className="rail-metric">
            <span>Last refreshed</span>
            <strong className="paper-sandbox-ts">{lastRefreshed}</strong>
          </div>
        )}
      </div>

      {loading && (
        <div className="paper-sandbox-loading" aria-live="polite">
          Loading sandbox preview…
        </div>
      )}

      {!loading && apiResult?.ok === false && (
        <ErrorBanner message={apiResult.error.message} />
      )}

      {!loading && (
        <SafetyContractRow state={displayState} />
      )}

      {!loading && apiResult?.ok === true && displayState.count === 0 && (
        <div className="paper-sandbox-empty" aria-live="polite">
          Sandbox is empty. No entries have been submitted yet. Advisory mode
          remains active.
        </div>
      )}

      {!loading && apiResult?.ok === true && displayState.entries.length > 0 && (
        <div className="paper-sandbox-entries" aria-label="Sandbox entries">
          <div className="workspace-section-head">
            <span>Simulated entries</span>
            <span>sandbox preview only · no execution</span>
          </div>
          {displayState.entries.map((entry) => (
            <SandboxEntryCard key={entry.sandbox_entry_id} entry={entry} />
          ))}
        </div>
      )}

      <p className="workspace-scanner-copy paper-sandbox-footer">
        Sandbox preview only · no broker execution · no MT5/IBKR calls ·
        display-only · advisory mode
      </p>
    </section>
  );
}
