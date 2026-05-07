import { Badge } from "../shared/Badge";
import { Table } from "../shared/Table";
import {
  exportSignalDecisionsCsv,
  exportSignalDecisionsJson,
  type SignalDecisionExportFilters,
} from "../../lib/exportSignalDecisions";
import type {
  DecisionDirection,
  DecisionRiskStatus,
  DecisionType,
  SignalDecisionRecord,
} from "../../types/api";

function decisionTone(
  decision: DecisionType,
): "green" | "red" | "amber" | "muted" {
  if (decision === "dry_run_allowed") return "green";
  if (decision === "blocked") return "red";
  if (decision === "watch_only") return "amber";
  return "muted";
}

function riskStatusTone(
  status: DecisionRiskStatus,
): "green" | "red" | "amber" | "muted" {
  if (status === "pass") return "green";
  if (status === "blocked") return "red";
  if (status === "warn") return "amber";
  return "muted";
}

function decisionDirectionTone(
  direction: DecisionDirection,
): "green" | "red" | "amber" {
  if (direction === "BUY") return "green";
  if (direction === "SELL") return "red";
  return "amber";
}

function percent(count: number, total: number) {
  return total === 0 ? 0 : Math.round((count / total) * 100);
}

function summarizeDecisions(records: SignalDecisionRecord[]) {
  const total = records.length;
  const dryRunAllowed = records.filter(
    (record) => record.decision === "dry_run_allowed",
  ).length;
  const blocked = records.filter((record) => record.decision === "blocked").length;
  const watchOnly = records.filter(
    (record) => record.decision === "watch_only",
  ).length;
  const noAction = records.filter(
    (record) => record.decision === "no_action",
  ).length;
  const averageConfidence =
    total === 0
      ? 0
      : Math.round(
          (records.reduce((sum, record) => sum + record.confidence, 0) / total) *
            1000,
        ) / 10;
  return {
    total,
    dryRunAllowed,
    blocked,
    watchOnly,
    noAction,
    averageConfidence,
    blockedRatio: percent(blocked, total),
  };
}

export function SignalDecisionHistoryPanel({
  records,
  hasActiveFilters = false,
  generatedAt,
  filters,
}: {
  records: SignalDecisionRecord[];
  hasActiveFilters?: boolean;
  generatedAt: string;
  filters: SignalDecisionExportFilters;
}) {
  const hasRecords = records.length > 0;
  const summary = summarizeDecisions(records);

  const exportOptions = {
    generatedAt,
    filters,
  };

  const exportActions = (
    <div className="signal-lifecycle-export">
      <div className="dashboard-muted">
        Exports current read-only filtered dry-run decision records. No orders are
        placed.
      </div>
      <div className="signal-lifecycle-export-actions">
        <button
          type="button"
          disabled={!hasRecords}
          onClick={() => exportSignalDecisionsCsv(records, exportOptions)}
        >
          Export CSV
        </button>
        <button
          type="button"
          disabled={!hasRecords}
          onClick={() => exportSignalDecisionsJson(records, exportOptions)}
        >
          Export JSON
        </button>
      </div>
    </div>
  );

  return (
    <>
      <section className="lifecycle-summary" aria-label="Dry-run journal summary">
        <div className="lifecycle-summary-header">
          <div>
            <strong>Dry-run journal summary</strong>
            <p>Summary reflects the currently filtered decision records.</p>
            <p>Dry-run decision history only. No order was placed.</p>
            <p>Live orders remain blocked.</p>
          </div>
          <Badge tone="green">read-only</Badge>
        </div>
        <div className="lifecycle-summary-grid">
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">{summary.total}</span>
            <span className="lifecycle-summary-label">total decisions</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">
              {summary.dryRunAllowed}
            </span>
            <span className="lifecycle-summary-label">dry-run allowed</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">{summary.blocked}</span>
            <span className="lifecycle-summary-label">blocked</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">{summary.watchOnly}</span>
            <span className="lifecycle-summary-label">watch-only</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">{summary.noAction}</span>
            <span className="lifecycle-summary-label">no-action</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">
              {summary.blockedRatio}%
            </span>
            <span className="lifecycle-summary-label">blocked ratio</span>
          </div>
          <div className="lifecycle-summary-card">
            <span className="lifecycle-summary-value">
              {summary.averageConfidence.toFixed(1)}%
            </span>
            <span className="lifecycle-summary-label">avg confidence</span>
          </div>
        </div>
      </section>
      {exportActions}

      {records.length === 0 ? (
        <div className="state">
          {hasActiveFilters
            ? "No dry-run decision records match the selected filters."
            : "No dry-run decision records available."}
        </div>
      ) : (
        <Table
          columns={[
            { key: "symbol", label: "Symbol", render: (row) => row.symbol },
            {
              key: "direction",
              label: "Dir",
              render: (row) => (
                <Badge tone={decisionDirectionTone(row.direction)}>
                  {row.direction}
                </Badge>
              ),
            },
            {
              key: "confidence",
              label: "Conf",
              render: (row) => `${Math.round(row.confidence * 100)}%`,
            },
            { key: "strategy", label: "Strategy", render: (row) => row.strategy },
            {
              key: "risk_status",
              label: "Risk",
              render: (row) => (
                <Badge tone={riskStatusTone(row.risk_status)}>
                  {row.risk_status}
                </Badge>
              ),
            },
            {
              key: "decision",
              label: "Decision",
              render: (row) => (
                <Badge tone={decisionTone(row.decision)}>{row.decision}</Badge>
              ),
            },
            {
              key: "blocked_reason",
              label: "Reason",
              render: (row) => row.blocked_reason ?? "-",
            },
          ]}
          rows={records}
        />
      )}
    </>
  );
}
