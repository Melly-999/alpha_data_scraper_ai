// Read-only Alpaca Paper status card — ALPACA-PAPER-READONLY-CARD-001.
//
// Display-only component. No buttons, no onClick handlers, no forms, no
// toggles, no execution controls, no broker/order controls. Advisory/demo
// status only.
//
// Renders only safe boolean safety flags plus a human-readable provider/mode/
// status line and a safety note. It never renders (and the backend never
// provides) account_id, broker_order_id, API keys, secrets, tokens, passwords,
// real buying power, or real positions.

import { useAlpacaPaperStatus } from "../../hooks/useAlpacaPaperStatus";

const STATUS_LABEL: Record<string, string> = {
  connected: "connected",
  unavailable: "unavailable",
};

const STATUS_CLASS: Record<string, string> = {
  connected: "status-ok",
  unavailable: "status-warn",
};

export function AlpacaPaperReadOnlyCard() {
  const { data, loading } = useAlpacaPaperStatus();

  const view = data;
  const statusKey = view?.status ?? "unavailable";
  const statusLabel = STATUS_LABEL[statusKey] ?? statusKey;
  const statusClass = STATUS_CLASS[statusKey] ?? "status-muted";

  // Display-only rows. Boolean safety flags are stringified for rendering.
  // No credential, account, position, or order fields are referenced.
  const rows: Array<[string, string]> = view
    ? [
        ["provider", "Alpaca Paper"],
        ["mode", "PAPER ONLY"],
        ["data source", "GET-only status"],
        ["paper_only", String(view.data.paper_only)],
        ["read_only", String(view.data.read_only)],
        ["dry_run", String(view.data.dry_run)],
        ["execution_enabled", String(view.data.execution_enabled)],
        ["live_orders_blocked", String(view.data.live_orders_blocked)],
        ["requires_human_review", String(view.data.requires_human_review)],
      ]
    : [];

  return (
    <section id="alpaca-paper-status" className="terminal-panel">
      <div className="panel-header">
        <span>Alpaca Paper</span>
        <span className={statusClass}>
          {loading && !view ? "polling…" : statusLabel}
        </span>
      </div>

      <div className="guardrail-list">
        {rows.map(([label, value]) => (
          <div key={label} className="guardrail-row">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <p className="panel-note">
        No order routing. No credentials exposed. Advisory / demo status only —
        not live trading.
      </p>

      {view?.source === "fallback" ? (
        <p className="panel-note">
          Backend status unavailable — showing safe read-only fallback.
        </p>
      ) : null}
    </section>
  );
}
