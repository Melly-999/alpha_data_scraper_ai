import { useState, type FormEvent, type ReactNode } from "react";

import {
  getPaperRunPreview,
  type PaperRunPreviewResponse,
} from "../../lib/paperRunPreviewApi";

type PreviewFormState = {
  symbol: string;
  side: "BUY" | "SELL";
  quantity: string;
  entry_price: string;
  stop_loss: string;
  take_profit: string;
  confidence: string;
  max_risk_pct: string;
};

const DEFAULT_FORM_STATE: PreviewFormState = {
  symbol: "EURUSD",
  side: "BUY",
  quantity: "1",
  entry_price: "1.1000",
  stop_loss: "1.0950",
  take_profit: "1.1100",
  confidence: "80",
  max_risk_pct: "0.01",
};

function formatNumber(value: number): string {
  if (Number.isInteger(value)) {
    return value.toString();
  }
  if (Math.abs(value) >= 1) {
    return value.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
  }
  return value.toFixed(5).replace(/0+$/, "").replace(/\.$/, "");
}

function safetyChips() {
  return (
    <div className="workspace-chip-row paper-run-preview-chips" aria-label="Paper run preview safety chips">
      <span className="workspace-chip">READ ONLY</span>
      <span className="workspace-chip">DRY RUN</span>
      <span className="workspace-chip">LIVE ORDERS BLOCKED</span>
      <span className="workspace-chip">HUMAN REVIEW REQUIRED</span>
      <span className="workspace-chip">EXECUTION OFF</span>
    </div>
  );
}

function SafetyContractRow({ preview }: { preview: PaperRunPreviewResponse }) {
  return (
    <div className="paper-run-preview-contract">
      <div className="workspace-section-head">
        <span>Safety contract</span>
        <span>always enforced</span>
      </div>
      <div className="rail-metric">
        <span>paper_only</span>
        <strong>{String(preview.paper_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>dry_run</span>
        <strong>{String(preview.dry_run)}</strong>
      </div>
      <div className="rail-metric">
        <span>read_only</span>
        <strong>{String(preview.read_only)}</strong>
      </div>
      <div className="rail-metric">
        <span>live_orders_blocked</span>
        <strong>{String(preview.live_orders_blocked)}</strong>
      </div>
      <div className="rail-metric">
        <span>requires_human_review</span>
        <strong>{String(preview.requires_human_review)}</strong>
      </div>
      <div className="rail-metric">
        <span>execution_enabled</span>
        <strong>{String(preview.execution_enabled)}</strong>
      </div>
    </div>
  );
}

function DetailCard({
  title,
  status,
  children,
}: {
  title: string;
  status: string;
  children: ReactNode;
}) {
  return (
    <article className="paper-run-preview-card">
      <div className="paper-run-preview-card-topline">
        <strong>{title}</strong>
        <span>{status}</span>
      </div>
      {children}
    </article>
  );
}

function EmptyRunState() {
  return (
    <div className="paper-run-preview-empty" aria-live="polite">
      <strong>No preview loaded</strong>
      <p>Load Preview to fetch the current GET-only paper run simulation.</p>
      <p>No broker calls, no order placement, no persistence.</p>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="paper-run-preview-error" role="alert">
      <strong>Preview unavailable</strong>
      <p>{message}</p>
      <p>Safety posture stays read-only and dry-run only.</p>
    </div>
  );
}

function RenderState({ preview }: { preview: PaperRunPreviewResponse }) {
  const run = preview.paper_run;
  const order = run?.orders[0] ?? null;
  const fill = run?.fills[0] ?? null;
  const position = run?.positions[0] ?? null;

  return (
    <div className="paper-run-preview-output" aria-live="polite">
      <div className="paper-run-preview-decision">
        <div>
          <span className={`paper-run-preview-pill ${preview.allowed ? "is-allowed" : "is-blocked"}`}>
            {preview.allowed ? "ALLOWED" : "BLOCKED"}
          </span>
          <p className="paper-run-preview-reason">{preview.reason}</p>
        </div>
        <SafetyContractRow preview={preview} />
      </div>

      <div className="paper-run-preview-grid">
        <div className="rail-metric">
          <span>Mode</span>
          <strong>GET preview</strong>
        </div>
        <div className="rail-metric">
          <span>Run ID</span>
          <strong className="paper-run-preview-id">{run?.run_id ?? "—"}</strong>
        </div>
        <div className="rail-metric">
          <span>Started</span>
          <strong className="paper-run-preview-ts">{run?.started_at ?? "—"}</strong>
        </div>
        <div className="rail-metric">
          <span>Total signals</span>
          <strong>{run?.total_signals ?? 0}</strong>
        </div>
        <div className="rail-metric">
          <span>Accepted</span>
          <strong>{run?.accepted_signals ?? 0}</strong>
        </div>
        <div className="rail-metric">
          <span>Rejected</span>
          <strong>{run?.rejected_signals ?? 0}</strong>
        </div>
        <div className="rail-metric">
          <span>Open positions</span>
          <strong>{run?.open_positions_count ?? 0}</strong>
        </div>
        <div className="rail-metric">
          <span>Closed positions</span>
          <strong>{run?.closed_positions_count ?? 0}</strong>
        </div>
        <div className="rail-metric">
          <span>Max risk</span>
          <strong>{run ? `${formatNumber(run.max_risk_pct)}%` : "0%"}</strong>
        </div>
      </div>

      {order && fill && position ? (
        <div className="paper-run-preview-cards">
          <DetailCard title="Order preview" status={order.status.toUpperCase()}>
            <div className="paper-run-preview-details">
              <div className="rail-metric">
                <span>Order ID</span>
                <strong className="paper-run-preview-id">{order.paper_order_id}</strong>
              </div>
              <div className="rail-metric">
                <span>Created</span>
                <strong className="paper-run-preview-ts">{order.created_at}</strong>
              </div>
              <div className="rail-metric"><span>Symbol</span><strong>{order.symbol}</strong></div>
              <div className="rail-metric"><span>Side</span><strong>{order.direction}</strong></div>
              <div className="rail-metric"><span>Quantity</span><strong>{formatNumber(order.quantity)}</strong></div>
              <div className="rail-metric"><span>Entry</span><strong>{formatNumber(order.entry_price)}</strong></div>
              <div className="rail-metric"><span>Stop loss</span><strong>{formatNumber(order.stop_loss)}</strong></div>
              <div className="rail-metric"><span>Take profit</span><strong>{formatNumber(order.take_profit)}</strong></div>
              <div className="rail-metric"><span>Max risk</span><strong>{formatNumber(order.max_risk_pct)}%</strong></div>
              <div className="rail-metric"><span>Rejection</span><strong>{order.rejection_reason ?? "—"}</strong></div>
            </div>
          </DetailCard>

          <DetailCard title="Fill preview" status="FILLED">
            <div className="paper-run-preview-details">
              <div className="rail-metric">
                <span>Fill ID</span>
                <strong className="paper-run-preview-id">{fill.paper_fill_id}</strong>
              </div>
              <div className="rail-metric">
                <span>Timestamp</span>
                <strong className="paper-run-preview-ts">{fill.fill_timestamp}</strong>
              </div>
              <div className="rail-metric"><span>Order ref</span><strong className="paper-run-preview-id">{fill.paper_order_ref}</strong></div>
              <div className="rail-metric"><span>Symbol</span><strong>{fill.symbol}</strong></div>
              <div className="rail-metric"><span>Side</span><strong>{fill.direction}</strong></div>
              <div className="rail-metric"><span>Fill price</span><strong>{formatNumber(fill.fill_price)}</strong></div>
              <div className="rail-metric"><span>Quantity</span><strong>{formatNumber(fill.quantity)}</strong></div>
            </div>
          </DetailCard>

          <DetailCard title="Position preview" status={position.status.toUpperCase()}>
            <div className="paper-run-preview-details">
              <div className="rail-metric">
                <span>Position ID</span>
                <strong className="paper-run-preview-id">{position.paper_position_id}</strong>
              </div>
              <div className="rail-metric">
                <span>Opened</span>
                <strong className="paper-run-preview-ts">{position.opened_at}</strong>
              </div>
              <div className="rail-metric">
                <span>Closed</span>
                <strong className="paper-run-preview-ts">{position.closed_at ?? "—"}</strong>
              </div>
              <div className="rail-metric"><span>Order ref</span><strong className="paper-run-preview-id">{position.paper_order_ref}</strong></div>
              <div className="rail-metric"><span>Symbol</span><strong>{position.symbol}</strong></div>
              <div className="rail-metric"><span>Side</span><strong>{position.direction}</strong></div>
              <div className="rail-metric"><span>Quantity</span><strong>{formatNumber(position.quantity)}</strong></div>
              <div className="rail-metric"><span>Entry</span><strong>{formatNumber(position.entry_price)}</strong></div>
              <div className="rail-metric"><span>Current</span><strong>{formatNumber(position.current_price)}</strong></div>
              <div className="rail-metric"><span>Stop loss</span><strong>{formatNumber(position.stop_loss)}</strong></div>
              <div className="rail-metric"><span>Take profit</span><strong>{formatNumber(position.take_profit)}</strong></div>
              <div className="rail-metric"><span>Unrealized PnL</span><strong>{formatNumber(position.unrealized_pnl)}</strong></div>
              <div className="rail-metric"><span>Max risk</span><strong>{formatNumber(position.max_risk_pct)}%</strong></div>
            </div>
          </DetailCard>
        </div>
      ) : (
        <div className="paper-run-preview-blocked">
          <div className="workspace-section-head">
            <span>Paper run data</span>
            <span>blocked preview</span>
          </div>
          <p>
            {preview.allowed
              ? "Preview payload did not include a paper run."
              : "Risk checks blocked the run. No order, fill, or position was created."}
          </p>
        </div>
      )}
    </div>
  );
}

export function PaperRunPreviewPanel() {
  const [form, setForm] = useState<PreviewFormState>(DEFAULT_FORM_STATE);
  const [preview, setPreview] = useState<PaperRunPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLoadPreview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await getPaperRunPreview({
        symbol: form.symbol.trim().toUpperCase(),
        side: form.side,
        quantity: Number(form.quantity),
        entry_price: Number(form.entry_price),
        stop_loss: Number(form.stop_loss),
        take_profit: Number(form.take_profit),
        confidence: Number(form.confidence),
        max_risk_pct: Number(form.max_risk_pct),
      });
      setPreview(response);
    } catch (err) {
      setPreview(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function updateField<K extends keyof PreviewFormState>(key: K, value: PreviewFormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setError(null);
  }

  return (
    <section className="workspace-rail-section paper-run-preview-panel" aria-label="Paper run preview panel">
      <div className="workspace-section-head">
        <span>Paper Run Preview</span>
        <span>GET-only · display-only</span>
      </div>

      <p className="workspace-scanner-copy">
        Read-only preview of the merged paper run simulation. No broker execution, no order placement, no persistence.
      </p>

      {safetyChips()}

      <form className="paper-run-preview-form" onSubmit={(event) => { void handleLoadPreview(event); }}>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-symbol">Symbol</label>
          <input
            id="paper-run-symbol"
            className="paper-run-preview-input"
            type="text"
            value={form.symbol}
            maxLength={16}
            required
            onChange={(event) => updateField("symbol", event.target.value.toUpperCase())}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-side">Side</label>
          <select
            id="paper-run-side"
            className="paper-run-preview-input"
            value={form.side}
            onChange={(event) => updateField("side", event.target.value as "BUY" | "SELL")}
          >
            <option value="BUY">Long</option>
            <option value="SELL">Short</option>
          </select>
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-quantity">Quantity</label>
          <input
            id="paper-run-quantity"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            value={form.quantity}
            required
            onChange={(event) => updateField("quantity", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-entry">Entry price</label>
          <input
            id="paper-run-entry"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            value={form.entry_price}
            required
            onChange={(event) => updateField("entry_price", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-stop">Stop loss</label>
          <input
            id="paper-run-stop"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            value={form.stop_loss}
            required
            onChange={(event) => updateField("stop_loss", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-target">Take profit</label>
          <input
            id="paper-run-target"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            value={form.take_profit}
            required
            onChange={(event) => updateField("take_profit", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-confidence">Confidence</label>
          <input
            id="paper-run-confidence"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            max="100"
            value={form.confidence}
            required
            onChange={(event) => updateField("confidence", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-field">
          <label htmlFor="paper-run-risk">Max risk pct</label>
          <input
            id="paper-run-risk"
            className="paper-run-preview-input"
            type="number"
            step="any"
            min="0"
            value={form.max_risk_pct}
            required
            onChange={(event) => updateField("max_risk_pct", event.target.value)}
          />
        </div>
        <div className="paper-run-preview-actions">
          <button type="submit" className="paper-run-preview-button" disabled={loading}>
            {preview ? "Refresh Preview" : "Load Preview"}
          </button>
          <span className="paper-run-preview-note">
            GET /paper/run/preview
          </span>
        </div>
      </form>

      {loading ? <div className="paper-run-preview-loading">Loading preview…</div> : null}
      {!loading && error ? <ErrorState message={error} /> : null}
      {!loading && !error && preview === null ? <EmptyRunState /> : null}
      {!loading && !error && preview !== null ? <RenderState preview={preview} /> : null}
    </section>
  );
}
