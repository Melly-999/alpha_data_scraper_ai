import { Badge } from "../shared/Badge";
import {
  exportSignalLifecycleCsv,
  exportSignalLifecycleJson,
  type SignalLifecycleExportFilters,
} from "../../lib/exportLifecycle";
import type {
  SignalLifecycleRecord,
  SignalLifecycleStepStatus,
} from "../../types/api";

function statusTone(
  status: SignalLifecycleStepStatus,
): "green" | "red" | "amber" | "blue" | "muted" {
  if (status === "passed" || status === "allowed") return "green";
  if (status === "blocked") return "red";
  if (status === "received") return "blue";
  if (status === "recorded") return "amber";
  return "muted";
}

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function percent(count: number, total: number) {
  return total === 0 ? 0 : Math.round((count / total) * 100);
}

function summarizeLifecycle(records: SignalLifecycleRecord[]) {
  const total = records.length;
  const decisions = {
    dry_run_allowed: records.filter(
      (record) => record.decision === "dry_run_allowed",
    ).length,
    blocked: records.filter((record) => record.decision === "blocked").length,
    watch_only: records.filter((record) => record.decision === "watch_only").length,
    no_action: records.filter((record) => record.decision === "no_action").length,
  };
  const risk = {
    pass: records.filter((record) => record.risk_status === "pass").length,
    warn: records.filter((record) => record.risk_status === "warn").length,
    blocked: records.filter((record) => record.risk_status === "blocked").length,
    unknown: records.filter((record) => record.risk_status === "unknown").length,
  };
  const averageConfidence =
    total === 0
      ? 0
      : Math.round(
          (records.reduce((sum, record) => sum + record.confidence, 0) / total) *
            1000,
        ) / 10;
  const readOnlySafe = records.every(
    (record) =>
      record.dry_run &&
      !record.auto_trade &&
      record.read_only &&
      !record.supports_live_orders &&
      !record.order_placed &&
      record.max_risk_per_trade <= 0.01,
  );
  return {
    total,
    decisions,
    risk,
    blockedRatio: percent(decisions.blocked, total),
    averageConfidence,
    readOnlySafe,
  };
}

function SummaryBar({
  label,
  value,
  total,
}: {
  label: string;
  value: number;
  total: number;
}) {
  return (
    <div className="lifecycle-summary-bar-row">
      <span>{label}</span>
      <div className="lifecycle-summary-bar" aria-hidden="true">
        <div
          className="lifecycle-summary-bar-fill"
          style={{ width: `${percent(value, total)}%` }}
        />
      </div>
      <strong>{value}</strong>
    </div>
  );
}

export function SignalLifecyclePanel({
  records,
  hasActiveFilters = false,
  generatedAt,
  filters,
}: {
  records: SignalLifecycleRecord[];
  hasActiveFilters?: boolean;
  generatedAt: string;
  filters: SignalLifecycleExportFilters;
}) {
  const hasRecords = records.length > 0;
  const summary = summarizeLifecycle(records);

  const exportOptions = {
    generatedAt,
    filters,
  };

  const exportActions = (
    <div className="signal-lifecycle-export">
      <div className="dashboard-muted">
        Exports current read-only filtered lifecycle records. No orders are placed.
      </div>
      <div className="signal-lifecycle-export-actions">
        <button
          type="button"
          disabled={!hasRecords}
          onClick={() => exportSignalLifecycleCsv(records, exportOptions)}
        >
          Export CSV
        </button>
        <button
          type="button"
          disabled={!hasRecords}
          onClick={() => exportSignalLifecycleJson(records, exportOptions)}
        >
          Export JSON
        </button>
      </div>
    </div>
  );

  const visualSummary = (
    <section className="lifecycle-summary" aria-label="Signal lifecycle summary">
      <div className="lifecycle-summary-header">
        <div>
          <strong>Visual summary</strong>
          <p>Summary reflects the currently filtered lifecycle records.</p>
          <p>Read-only analysis. No orders were placed.</p>
        </div>
        <Badge tone={summary.readOnlySafe ? "green" : "amber"}>
          {summary.readOnlySafe ? "read-only safe" : "review safety flags"}
        </Badge>
      </div>
      <div className="lifecycle-summary-grid">
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">{summary.total}</span>
          <span className="lifecycle-summary-label">total records</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">
            {summary.decisions.dry_run_allowed}
          </span>
          <span className="lifecycle-summary-label">dry-run allowed</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">
            {summary.decisions.blocked}
          </span>
          <span className="lifecycle-summary-label">blocked</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">
            {summary.decisions.watch_only}
          </span>
          <span className="lifecycle-summary-label">watch-only</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">
            {summary.decisions.no_action}
          </span>
          <span className="lifecycle-summary-label">no-action</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">{summary.risk.pass}</span>
          <span className="lifecycle-summary-label">risk pass</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">{summary.risk.warn}</span>
          <span className="lifecycle-summary-label">risk warn</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">{summary.risk.blocked}</span>
          <span className="lifecycle-summary-label">risk blocked</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">{summary.blockedRatio}%</span>
          <span className="lifecycle-summary-label">blocked ratio</span>
        </div>
        <div className="lifecycle-summary-card">
          <span className="lifecycle-summary-value">
            {summary.averageConfidence.toFixed(1)}%
          </span>
          <span className="lifecycle-summary-label">avg confidence</span>
        </div>
      </div>
      <div className="lifecycle-summary-bars">
        <div>
          <span className="lifecycle-summary-label">decision distribution</span>
          <SummaryBar
            label="dry-run allowed"
            value={summary.decisions.dry_run_allowed}
            total={summary.total}
          />
          <SummaryBar
            label="blocked"
            value={summary.decisions.blocked}
            total={summary.total}
          />
          <SummaryBar
            label="watch-only"
            value={summary.decisions.watch_only}
            total={summary.total}
          />
          <SummaryBar
            label="no-action"
            value={summary.decisions.no_action}
            total={summary.total}
          />
        </div>
        <div>
          <span className="lifecycle-summary-label">risk distribution</span>
          <SummaryBar label="pass" value={summary.risk.pass} total={summary.total} />
          <SummaryBar label="warn" value={summary.risk.warn} total={summary.total} />
          <SummaryBar
            label="blocked"
            value={summary.risk.blocked}
            total={summary.total}
          />
          <SummaryBar
            label="unknown"
            value={summary.risk.unknown}
            total={summary.total}
          />
        </div>
      </div>
    </section>
  );

  if (records.length === 0) {
    return (
      <>
        {visualSummary}
        {exportActions}
        <div className="state">
          {hasActiveFilters
            ? "No lifecycle records match the selected filters."
            : "No lifecycle records available."}
        </div>
      </>
    );
  }

  return (
    <>
      {visualSummary}
      {exportActions}
      <div className="signal-lifecycle-list">
        {records.map((record) => (
          <article className="signal-lifecycle-record" key={record.id}>
            <header className="signal-lifecycle-record-header">
              <div>
                <div className="card-kicker">{formatTime(record.timestamp)}</div>
                <strong>
                  {record.symbol} {record.direction}
                </strong>
              </div>
              <div className="signal-lifecycle-badges">
                <Badge
                  tone={record.decision === "dry_run_allowed" ? "green" : "amber"}
                >
                  {record.decision}
                </Badge>
                <Badge tone="muted">{Math.round(record.confidence * 100)}%</Badge>
                <Badge tone="muted">{record.risk_status}</Badge>
                <Badge tone="green">dry-run</Badge>
              </div>
            </header>

            <ol className="signal-lifecycle-steps">
              {record.steps.map((step) => (
                <li key={step.key}>
                  <div className="signal-lifecycle-step-top">
                    <span>{step.label}</span>
                    <Badge tone={statusTone(step.status)}>{step.status}</Badge>
                  </div>
                  <p>{step.detail}</p>
                </li>
              ))}
            </ol>

            <footer className="signal-lifecycle-footer">
              <span>Decision {record.decision_id}</span>
              <span>Audit {record.audit_event_id}</span>
              <span>Dry-run explanation only. No order was placed.</span>
              <span>Live orders remain blocked.</span>
              <span>{record.order_placed ? "order placed" : "no order placed"}</span>
            </footer>
          </article>
        ))}
      </div>
    </>
  );
}
