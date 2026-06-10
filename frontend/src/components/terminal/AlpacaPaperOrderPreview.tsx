// Alpaca Paper Order Preview — ALPACA-PAPER-ORDER-PREVIEW-003.
//
// GET-only paper-order preview form.  Submits only to
// GET /api/alpaca-paper/order-preview — no POST/PUT/PATCH/DELETE.
//
// Safety contract:
//   - No Buy/Sell/Execute/Submit/Place-Order button or label anywhere.
//   - Always visible: "Preview only — not submitted · Paper trading demo · No real orders"
//   - paper_only, dry_run, read_only, live_orders_blocked, execution_enabled=false,
//     requires_human_review, submitted=false — shown in every result.
//   - No account_id, broker_order_id, credentials, or secrets exposed.
//   - Button label: "Generate Preview" only.
//   - result.order.paper_order_id always starts with "paper-alpaca-".

import { useState } from "react";

import {
  type AlpacaPaperOrderPreviewParams,
  type AlpacaPaperOrderPreviewView,
  fetchAlpacaPaperOrderPreview,
} from "../../lib/alpacaPaperOrderPreviewApi";

// ---------------------------------------------------------------------------
// Default form values (paper-demo defaults, no real prices)
// ---------------------------------------------------------------------------

const DEFAULTS: AlpacaPaperOrderPreviewParams = {
  symbol: "AAPL",
  side: "BUY",
  quantity: 10,
  entry_price: 150.0,
  stop_loss: 148.0,
  take_profit: 155.0,
  max_risk_pct: 0.5,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AlpacaPaperOrderPreview() {
  const [symbol, setSymbol] = useState(DEFAULTS.symbol);
  const [side, setSide] = useState<"BUY" | "SELL">(DEFAULTS.side);
  const [quantity, setQuantity] = useState(String(DEFAULTS.quantity));
  const [entryPrice, setEntryPrice] = useState(String(DEFAULTS.entry_price));
  const [stopLoss, setStopLoss] = useState(String(DEFAULTS.stop_loss));
  const [takeProfit, setTakeProfit] = useState(String(DEFAULTS.take_profit));
  const [maxRiskPct, setMaxRiskPct] = useState(String(DEFAULTS.max_risk_pct));

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AlpacaPaperOrderPreviewView | null>(
    null,
  );

  async function handleGeneratePreview() {
    setLoading(true);
    setResult(null);
    try {
      const view = await fetchAlpacaPaperOrderPreview({
        symbol: symbol.trim().toUpperCase(),
        side,
        quantity: Number(quantity),
        entry_price: Number(entryPrice),
        stop_loss: Number(stopLoss),
        take_profit: Number(takeProfit),
        max_risk_pct: Number(maxRiskPct),
      });
      setResult(view);
    } finally {
      setLoading(false);
    }
  }

  const order = result?.data?.order ?? null;
  const allowed = result?.data?.allowed ?? null;

  return (
    <section id="alpaca-paper-order-preview" className="terminal-panel">
      <div className="panel-header">
        <span>Alpaca Paper Order Preview</span>
        <span className="status-muted">preview-only</span>
      </div>

      {/* Always-visible safety notice */}
      <p className="panel-note panel-note--prominent">
        Preview only — not submitted · Paper trading demo · No real orders
      </p>

      {/* Input form */}
      <div className="preview-form">
        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-symbol">
            Symbol
          </label>
          <input
            id="apop-symbol"
            className="preview-form__input"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            maxLength={32}
            autoComplete="off"
          />
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-side">
            Direction
          </label>
          <select
            id="apop-side"
            className="preview-form__input"
            value={side}
            onChange={(e) => setSide(e.target.value as "BUY" | "SELL")}
          >
            <option value="BUY">BUY (long)</option>
            <option value="SELL">SELL (short)</option>
          </select>
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-qty">
            Quantity
          </label>
          <input
            id="apop-qty"
            className="preview-form__input"
            type="number"
            min="0.0001"
            step="any"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-entry">
            Entry price
          </label>
          <input
            id="apop-entry"
            className="preview-form__input"
            type="number"
            min="0.0001"
            step="any"
            value={entryPrice}
            onChange={(e) => setEntryPrice(e.target.value)}
          />
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-sl">
            Stop loss
          </label>
          <input
            id="apop-sl"
            className="preview-form__input"
            type="number"
            min="0.0001"
            step="any"
            value={stopLoss}
            onChange={(e) => setStopLoss(e.target.value)}
          />
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-tp">
            Take profit
          </label>
          <input
            id="apop-tp"
            className="preview-form__input"
            type="number"
            min="0.0001"
            step="any"
            value={takeProfit}
            onChange={(e) => setTakeProfit(e.target.value)}
          />
        </div>

        <div className="preview-form__row">
          <label className="preview-form__label" htmlFor="apop-risk">
            Max risk % (≤ 1.0)
          </label>
          <input
            id="apop-risk"
            className="preview-form__input"
            type="number"
            min="0.0001"
            max="100"
            step="any"
            value={maxRiskPct}
            onChange={(e) => setMaxRiskPct(e.target.value)}
          />
        </div>

        {/* Generate Preview — NOT "Buy", "Sell", "Execute", "Submit", "Place Order" */}
        <button
          className="preview-form__btn"
          type="button"
          disabled={loading}
          onClick={handleGeneratePreview}
        >
          {loading ? "Generating…" : "Generate Preview"}
        </button>
      </div>

      {/* Result */}
      {result !== null && (
        <div className="preview-result">
          {/* Connection state */}
          {result.source === "fallback" && (
            <p className="panel-note">
              Backend unavailable — showing safe read-only fallback.
            </p>
          )}

          {/* Allowed / blocked status */}
          <div className="guardrail-row">
            <span>allowed</span>
            <strong className={allowed ? "status-ok" : "status-warn"}>
              {String(allowed)}
            </strong>
          </div>

          <div className="guardrail-row">
            <span>reason</span>
            <span className="preview-result__reason">{result.data.reason}</span>
          </div>

          {/* Top-level safety flags */}
          <div className="guardrail-list">
            {(
              [
                ["submitted", String(result.data.submitted)],
                ["paper_only", String(result.data.paper_only)],
                ["dry_run", String(result.data.dry_run)],
                ["read_only", String(result.data.read_only)],
                ["execution_enabled", String(result.data.execution_enabled)],
                [
                  "live_orders_blocked",
                  String(result.data.live_orders_blocked),
                ],
                [
                  "requires_human_review",
                  String(result.data.requires_human_review),
                ],
                ["broker", result.data.broker],
                ["label", result.data.label],
              ] as Array<[string, string]>
            ).map(([key, val]) => (
              <div key={key} className="guardrail-row">
                <span>{key}</span>
                <strong>{val}</strong>
              </div>
            ))}
          </div>

          {/* Order detail (only when allowed) */}
          {order !== null && (
            <div className="preview-result__order">
              <p className="preview-result__order-title">Paper order preview</p>
              <div className="guardrail-list">
                {(
                  [
                    ["paper_order_id", order.paper_order_id],
                    ["run_id", order.run_id],
                    ["symbol", order.symbol],
                    ["direction", order.direction],
                    ["quantity", String(order.quantity)],
                    ["entry_price", String(order.entry_price)],
                    ["stop_loss", String(order.stop_loss)],
                    ["take_profit", String(order.take_profit)],
                    ["max_risk_pct", String(order.max_risk_pct)],
                    ["status", order.status],
                    ["fill_type", order.fill_type],
                    ["broker", order.broker],
                    ["submitted", String(order.submitted)],
                  ] as Array<[string, string]>
                ).map(([key, val]) => (
                  <div key={key} className="guardrail-row">
                    <span>{key}</span>
                    <strong>{val}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Persistent bottom safety note */}
      <p className="panel-note">
        No order routing. No credentials exposed. Paper trading demo only —
        not live trading. Human review required before any real action.
      </p>
    </section>
  );
}
