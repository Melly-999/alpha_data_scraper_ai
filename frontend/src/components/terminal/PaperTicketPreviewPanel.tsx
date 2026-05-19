// PDS-004 — Paper Ticket Preview Panel (AI Workspace).
//
// Read-only advisory panel.  Sends a single POST to the paper-only sandbox
// endpoint (PDS-003) and displays the validation result.
//
// Safety invariants enforced here:
//   - No execute/order-placement buttons.
//   - No broker/MT5/IBKR calls.
//   - No live trading surfaces.
//   - All UI copy makes the paper-only advisory posture clear.
//   - Backend always returns paper_only=true, dry_run=true, etc.

import { useState } from "react";

import {
  createPaperTicketDraft,
  createFallbackSafetyContract,
  type EntryType,
  type PaperTicketApiResult,
  type PaperTicketInput,
  type TradeSide,
} from "../../lib/paperTicketApi";

// ---------------------------------------------------------------------------
// Default form values — EURUSD long, pre-populated for quick preview
// ---------------------------------------------------------------------------

const DEFAULT_INPUT: PaperTicketInput = {
  symbol: "EURUSD",
  side: "long",
  entry_type: "market_simulated",
  timeframe: "H1",
  entry_price: 1.1000,
  stop_loss: 1.0950,
  take_profit_1: 1.1100,
  risk_pct: 0.5,
  confidence: 75,
  reason: "H1 bullish momentum with RSI 58 and MACD cross",
  source: "workspace_preview",
};

// ---------------------------------------------------------------------------
// Small presentational helpers
// ---------------------------------------------------------------------------

function SafetyBadgeRow() {
  return (
    <div className="scanner-badge-row" aria-label="Paper ticket safety badges">
      <span className="scanner-preview-badge">PAPER ONLY</span>
      <span className="scanner-preview-badge">DRY RUN</span>
      <span className="scanner-preview-badge">HUMAN REVIEW</span>
      <span className="scanner-preview-badge">NO EXECUTION</span>
    </div>
  );
}

function ResultPanel({ apiResult }: { apiResult: PaperTicketApiResult }) {
  if (!apiResult.ok) {
    return (
      <div className="paper-ticket-result paper-ticket-result--error" role="alert">
        <strong>Request failed</strong>
        <p>{apiResult.error.message}</p>
        <SafetyBadgeRow />
      </div>
    );
  }

  const { result } = apiResult;
  const sc = result.safety_contract ?? createFallbackSafetyContract();

  return (
    <div
      className={`paper-ticket-result ${result.accepted ? "paper-ticket-result--accepted" : "paper-ticket-result--rejected"}`}
      role="status"
      aria-live="polite"
    >
      <div className="paper-ticket-verdict">
        <strong>
          {result.accepted ? "Draft accepted" : "Draft rejected"}
        </strong>
        <span className="workspace-chip">
          {result.accepted ? "VALID" : "INVALID"}
        </span>
      </div>

      {!result.accepted && result.rejection_reasons.length > 0 && (
        <ul className="paper-ticket-reasons" aria-label="Rejection reasons">
          {result.rejection_reasons.map((reason, i) => (
            <li key={i}>{reason}</li>
          ))}
        </ul>
      )}

      {result.warnings.length > 0 && (
        <ul className="paper-ticket-warnings" aria-label="Validation warnings">
          {result.warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      )}

      {result.accepted && result.draft && (
        <div className="paper-ticket-draft-summary">
          <div className="rail-metric">
            <span>Ticket ID</span>
            <strong className="paper-ticket-id">{result.draft.ticket_id}</strong>
          </div>
          <div className="rail-metric">
            <span>Symbol</span>
            <strong>{result.draft.symbol}</strong>
          </div>
          <div className="rail-metric">
            <span>Side</span>
            <strong>{result.draft.side.toUpperCase()}</strong>
          </div>
          <div className="rail-metric">
            <span>Entry</span>
            <strong>{result.draft.entry_price}</strong>
          </div>
          <div className="rail-metric">
            <span>Stop loss</span>
            <strong>{result.draft.stop_loss}</strong>
          </div>
          <div className="rail-metric">
            <span>Take profit 1</span>
            <strong>{result.draft.take_profit_1}</strong>
          </div>
          <div className="rail-metric">
            <span>Risk %</span>
            <strong>{result.draft.risk_pct}%</strong>
          </div>
          <div className="rail-metric">
            <span>Confidence</span>
            <strong>{result.draft.confidence}%</strong>
          </div>
        </div>
      )}

      <div className="paper-ticket-contract">
        <div className="workspace-section-head">
          <span>Safety contract</span>
          <span>always enforced</span>
        </div>
        <div className="rail-metric">
          <span>paper_only</span>
          <strong>{String(sc.paper_only)}</strong>
        </div>
        <div className="rail-metric">
          <span>dry_run</span>
          <strong>{String(sc.dry_run)}</strong>
        </div>
        <div className="rail-metric">
          <span>live_orders_blocked</span>
          <strong>{String(sc.live_orders_blocked)}</strong>
        </div>
        <div className="rail-metric">
          <span>risk_allowed</span>
          <strong>{String(sc.risk_allowed)}</strong>
        </div>
        <div className="rail-metric">
          <span>broker_execution_allowed</span>
          <strong>{String(sc.broker_execution_allowed)}</strong>
        </div>
        <div className="rail-metric">
          <span>max_risk_pct</span>
          <strong>{sc.max_risk_pct}%</strong>
        </div>
        <div className="rail-metric">
          <span>execution_mode</span>
          <strong>{sc.execution_mode}</strong>
        </div>
      </div>

      <SafetyBadgeRow />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main panel
// ---------------------------------------------------------------------------

export function PaperTicketPreviewPanel() {
  const [input, setInput] = useState<PaperTicketInput>(DEFAULT_INPUT);
  const [apiResult, setApiResult] = useState<PaperTicketApiResult | null>(null);
  const [loading, setLoading] = useState(false);

  function handleField<K extends keyof PaperTicketInput>(
    key: K,
    value: PaperTicketInput[K],
  ) {
    setInput((prev) => ({ ...prev, [key]: value }));
    setApiResult(null);
  }

  async function handlePreview(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setApiResult(null);
    const result = await createPaperTicketDraft(input);
    setApiResult(result);
    setLoading(false);
  }

  return (
    <section
      className="workspace-rail-section paper-ticket-preview-panel"
      aria-label="Paper ticket draft preview — advisory only"
    >
      <div className="workspace-section-head">
        <span>Paper Ticket Preview</span>
        <span>advisory only · no execution</span>
      </div>

      <p className="workspace-scanner-copy">
        Paper-only sandbox validation (PDS-003). No broker execution.
        No live trading. Human review always required.
      </p>

      <SafetyBadgeRow />

      <form
        className="paper-ticket-form"
        onSubmit={(e) => { void handlePreview(e); }}
        aria-label="Paper ticket draft form — advisory, no execution"
      >
        <div className="paper-ticket-row">
          <label htmlFor="pt-symbol">Symbol</label>
          <input
            id="pt-symbol"
            className="paper-ticket-input"
            type="text"
            value={input.symbol}
            maxLength={32}
            required
            onChange={(e) => handleField("symbol", e.target.value.toUpperCase())}
            aria-label="Symbol"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-side">Side</label>
          <select
            id="pt-side"
            className="paper-ticket-input"
            value={input.side}
            onChange={(e) => handleField("side", e.target.value as TradeSide)}
            aria-label="Side — long or short"
          >
            <option value="long">Long</option>
            <option value="short">Short</option>
          </select>
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-entry-type">Entry type</label>
          <select
            id="pt-entry-type"
            className="paper-ticket-input"
            value={input.entry_type}
            onChange={(e) =>
              handleField("entry_type", e.target.value as EntryType)
            }
            aria-label="Entry type"
          >
            <option value="market_simulated">Market simulated</option>
            <option value="limit">Limit</option>
            <option value="breakout">Breakout</option>
            <option value="reversal">Reversal</option>
            <option value="manual">Manual</option>
          </select>
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-timeframe">Timeframe</label>
          <input
            id="pt-timeframe"
            className="paper-ticket-input"
            type="text"
            value={input.timeframe}
            maxLength={8}
            required
            onChange={(e) => handleField("timeframe", e.target.value)}
            aria-label="Timeframe"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-entry">Entry price</label>
          <input
            id="pt-entry"
            className="paper-ticket-input"
            type="number"
            step="any"
            value={input.entry_price}
            required
            onChange={(e) =>
              handleField("entry_price", parseFloat(e.target.value))
            }
            aria-label="Entry price"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-sl">Stop loss</label>
          <input
            id="pt-sl"
            className="paper-ticket-input"
            type="number"
            step="any"
            value={input.stop_loss}
            required
            onChange={(e) =>
              handleField("stop_loss", parseFloat(e.target.value))
            }
            aria-label="Stop loss price"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-tp1">Take profit 1</label>
          <input
            id="pt-tp1"
            className="paper-ticket-input"
            type="number"
            step="any"
            value={input.take_profit_1}
            required
            onChange={(e) =>
              handleField("take_profit_1", parseFloat(e.target.value))
            }
            aria-label="Take profit 1"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-risk">Risk %</label>
          <input
            id="pt-risk"
            className="paper-ticket-input"
            type="number"
            step="any"
            min={0.01}
            max={1}
            value={input.risk_pct}
            required
            onChange={(e) =>
              handleField("risk_pct", parseFloat(e.target.value))
            }
            aria-label="Risk percentage — max 1%"
          />
        </div>

        <div className="paper-ticket-row">
          <label htmlFor="pt-conf">Confidence %</label>
          <input
            id="pt-conf"
            className="paper-ticket-input"
            type="number"
            step="any"
            min={0}
            max={100}
            value={input.confidence}
            required
            onChange={(e) =>
              handleField("confidence", parseFloat(e.target.value))
            }
            aria-label="Confidence percentage"
          />
        </div>

        <div className="paper-ticket-row paper-ticket-row--full">
          <label htmlFor="pt-reason">Reason</label>
          <textarea
            id="pt-reason"
            className="paper-ticket-input paper-ticket-textarea"
            value={input.reason}
            maxLength={1024}
            required
            onChange={(e) => handleField("reason", e.target.value)}
            aria-label="Trade reason — advisory text"
            spellCheck={false}
          />
        </div>

        <div className="paper-ticket-submit-row">
          <button
            type="submit"
            className="paper-ticket-preview-btn"
            disabled={loading}
            aria-label="Validate paper ticket draft — advisory only, no execution"
          >
            {loading ? "Validating…" : "Validate draft"}
          </button>
          <span className="workspace-scanner-copy">
            Advisory only · paper sandbox · no broker execution
          </span>
        </div>
      </form>

      {apiResult !== null && <ResultPanel apiResult={apiResult} />}
    </section>
  );
}
