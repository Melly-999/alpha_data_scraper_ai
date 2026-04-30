import { useMemo, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { useDailyReport, useWeeklyReport } from "../hooks/useReports";
import type { AuditEvent, ReportItem, ReportPeriod } from "../types/melly";

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatWindow(report: ReportItem): string {
  return `${formatTimestamp(report.window_start)} - ${formatTimestamp(
    report.window_end,
  )}`;
}

function statusTone(value: boolean): "green" | "red" {
  return value ? "green" : "red";
}

function countEntries(counts: Record<string, number>): Array<[string, number]> {
  return Object.entries(counts).sort(([left], [right]) =>
    left.localeCompare(right),
  );
}

function AuditRows({ events }: { events: AuditEvent[] }) {
  if (events.length === 0) {
    return <div className="state">No audit events in this report window.</div>;
  }

  return (
    <div className="report-audit-list">
      {events.map((event, index) => (
        <div
          className="report-audit-row"
          key={`${event.timestamp}-${event.type}-${event.signal_id ?? index}`}
        >
          <span className="report-audit-time">
            {formatTimestamp(event.timestamp)}
          </span>
          <Badge tone={event.severity === "warning" ? "amber" : "blue"}>
            {event.type}
          </Badge>
          <span className="dashboard-muted">{event.message}</span>
        </div>
      ))}
    </div>
  );
}

function CountList({
  title,
  counts,
}: {
  title: string;
  counts: Record<string, number>;
}) {
  const rows = countEntries(counts);
  return (
    <div className="report-count-list">
      <div className="report-section-title">{title}</div>
      {rows.length === 0 ? (
        <div className="dashboard-muted">No entries</div>
      ) : (
        rows.map(([label, value]) => (
          <div key={label} className="report-count-row">
            <span>{label.replace(/_/g, " ")}</span>
            <strong>{value}</strong>
          </div>
        ))
      )}
    </div>
  );
}

function ReportPanel({
  report,
  loading,
  error,
}: {
  report: ReportItem | null;
  loading: boolean;
  error: string | null;
}) {
  if (loading && !report) {
    return <div className="state">Loading report...</div>;
  }
  if (error && !report) {
    return <div className="state error">{error}</div>;
  }
  if (!report) {
    return <div className="state">No report data available.</div>;
  }

  const safety = report.safety_posture;
  const signalCounts = report.signal_counts;

  return (
    <div className="report-layout">
      {error ? <div className="state error">{error}</div> : null}

      <div className="report-summary-grid">
        <div className="report-summary-card">
          <div className="dashboard-metric-label">Signals</div>
          <div className="dashboard-metric-value">{signalCounts.total}</div>
          <div className="dashboard-metric-detail">
            {signalCounts.accepted} accepted / {signalCounts.rejected} rejected
          </div>
        </div>
        <div className="report-summary-card">
          <div className="dashboard-metric-label">Safety</div>
          <div className="report-badge-stack">
            <Badge tone={statusTone(safety.dry_run)}>
              dry_run={String(safety.dry_run)}
            </Badge>
            <Badge tone={statusTone(safety.read_only)}>
              read_only={String(safety.read_only)}
            </Badge>
            <Badge tone={statusTone(safety.live_orders_blocked)}>
              live_orders_blocked={String(safety.live_orders_blocked)}
            </Badge>
          </div>
        </div>
        <div className="report-summary-card">
          <div className="dashboard-metric-label">Risk Config</div>
          <div className="dashboard-metric-value">
            {report.risk_config_snapshot.max_risk_percent.toFixed(2)}%
          </div>
          <div className="dashboard-metric-detail">
            Max risk / min confidence{" "}
            {report.risk_config_snapshot.min_confidence.toFixed(0)}
          </div>
        </div>
      </div>

      <div className="report-two-column">
        <CountList
          title="Alerts by severity"
          counts={report.alert_counts_by_severity}
        />
        <CountList
          title="Alerts by category"
          counts={report.alert_counts_by_category}
        />
      </div>

      <section className="report-section">
        <div className="report-section-title">Latest audit events</div>
        <AuditRows events={report.latest_audit_events} />
      </section>

      <section className="report-section">
        <div className="report-section-title">Markdown preview</div>
        <pre className="report-markdown-preview">{report.markdown_summary}</pre>
      </section>
    </div>
  );
}

export function ReportsPage() {
  const [period, setPeriod] = useState<ReportPeriod>("daily");
  const daily = useDailyReport();
  const weekly = useWeeklyReport();

  const active = period === "daily" ? daily : weekly;
  const report = active.data;
  const badgeTone = report?.read_only ? "green" : "amber";
  const windowLabel = useMemo(
    () => (report ? formatWindow(report) : "Report window unavailable"),
    [report],
  );

  return (
    <div className="page-grid passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Reports</div>
            <h1 className="page-title">Read-only report summaries</h1>
            <div className="dashboard-muted">
              Daily and weekly summaries generated from safety posture, signal
              history, alert counts, audit events, and risk configuration.
            </div>
          </div>
          <div className="page-header-meta">
            <Badge tone={badgeTone}>
              read_only={String(report?.read_only ?? true)}
            </Badge>
            <Badge tone="blue">{period}</Badge>
          </div>
        </section>

        <Card
          title="Report"
          right={<span className="card-kicker">{windowLabel}</span>}
        >
          <div className="report-controls">
            <label>
              <span>Period</span>
              <select
                value={period}
                onChange={(event) =>
                  setPeriod(event.target.value as ReportPeriod)
                }
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </label>
          </div>

          <ReportPanel
            report={report}
            loading={active.loading}
            error={active.error}
          />
        </Card>
      </div>
    </div>
  );
}
