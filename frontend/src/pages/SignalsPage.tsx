import { useEffect, useMemo, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Drawer } from "../components/shared/Drawer";
import { Table } from "../components/shared/Table";
import { SignalLifecyclePanel } from "../components/signals/SignalLifecyclePanel";
import { useMellySignals } from "../hooks/useMellySignals";
import { useSignalDecisions } from "../hooks/useSignalDecisions";
import { useSignalLifecycle } from "../hooks/useSignalLifecycle";
import { useSignals } from "../hooks/useSignals";
import { apiGet } from "../lib/api";
import { useUiStore } from "../stores/useUiStore";
import type {
  DecisionDirection,
  DecisionRiskStatus,
  DecisionType,
  Direction,
  SignalDecisionRecord,
  SignalDetail,
  SignalReasoning,
} from "../types/api";
import type { Action, SignalSummary as MellySignalSummary } from "../types/melly";

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

function SignalDecisionRows({ records }: { records: SignalDecisionRecord[] }) {
  return (
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
  );
}

function directionTone(direction: Direction): "green" | "red" | "amber" {
  if (direction === "BUY") {
    return "green";
  }
  if (direction === "SELL") {
    return "red";
  }
  return "amber";
}

function formatOptional(value: number | null | undefined) {
  return value == null ? "-" : value.toString();
}

function actionTone(action: Action): "green" | "red" | "amber" {
  if (action === "BUY") return "green";
  if (action === "SELL") return "red";
  return "amber";
}

function statusTone(status: string): "green" | "red" | "muted" {
  if (status === "accepted") return "green";
  if (status === "rejected") return "red";
  return "muted";
}

type MellyStatusFilter = "" | "accepted" | "rejected";

export function SignalsPage() {
  const { data, loading, error } = useSignals();
  const {
    data: decisionsData,
    loading: decisionsLoading,
    error: decisionsError,
  } = useSignalDecisions(50);
  const {
    data: lifecycleData,
    loading: lifecycleLoading,
    error: lifecycleError,
  } = useSignalLifecycle(50);
  const selectedSignalId = useUiStore((state) => state.selectedSignalId);
  const setSelectedSignalId = useUiStore((state) => state.setSelectedSignalId);
  const [detail, setDetail] = useState<SignalDetail | null>(null);
  const [reasoning, setReasoning] = useState<SignalReasoning | null>(null);

  const [mellySymbol, setMellySymbol] = useState("");
  const [mellyStatus, setMellyStatus] = useState<MellyStatusFilter>("");
  const trimmedSymbol = mellySymbol.trim();
  const {
    data: mellySignals,
    loading: mellyLoading,
    error: mellyError,
  } = useMellySignals({
    symbol: trimmedSymbol === "" ? undefined : trimmedSymbol,
    status: mellyStatus === "" ? undefined : mellyStatus,
    limit: 50,
  });
  const mellyRows = useMemo<MellySignalSummary[]>(
    () => mellySignals ?? [],
    [mellySignals],
  );

  useEffect(() => {
    if (!selectedSignalId) {
      setDetail(null);
      setReasoning(null);
      return;
    }
    void apiGet<SignalDetail>(`/signals/${selectedSignalId}`).then(setDetail);
    void apiGet<SignalReasoning>(`/signals/${selectedSignalId}/reasoning`).then(
      setReasoning,
    );
  }, [selectedSignalId]);

  const signals = data ?? [];
  const eligibleCount = signals.filter((signal) => !signal.blocked).length;
  const blockedCount = signals.filter((signal) => signal.blocked).length;
  const averageConfidence =
    signals.length > 0
      ? Math.round(
          signals.reduce((total, signal) => total + signal.confidence, 0) /
            signals.length,
        )
      : 0;

  return (
    <div className="page-grid with-drawer passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Signals</div>
            <h1 className="page-title">Signal Review</h1>
            <div className="dashboard-muted">Read-only signal feed from FastAPI.</div>
          </div>
          <div className="page-header-meta">
            <Badge tone="green">{eligibleCount} eligible</Badge>
            <Badge tone="amber">{blockedCount} blocked</Badge>
            <Badge tone="blue">{averageConfidence}% avg confidence</Badge>
          </div>
        </section>

        <Card
          title="Signals"
          right={<Badge tone="muted">{signals.length} total</Badge>}
        >
          {loading && !data ? <div className="state">Loading signals...</div> : null}
          {error && !data ? <div className="state error">{error}</div> : null}
          {data ? (
            <Table
              columns={[
                { key: "symbol", label: "Symbol", render: (row) => row.symbol },
                {
                  key: "direction",
                  label: "Direction",
                  render: (row) => (
                    <Badge tone={directionTone(row.direction)}>{row.direction}</Badge>
                  ),
                },
                {
                  key: "confidence",
                  label: "Conf",
                  render: (row) => `${row.confidence}%`,
                },
                {
                  key: "mtf_alignment",
                  label: "MTF",
                  render: (row) => `${row.mtf_alignment}/${row.mtf_total}`,
                },
                {
                  key: "claude_status",
                  label: "Claude",
                  render: (row) => row.claude_status,
                },
                {
                  key: "blocked_reason",
                  label: "Risk",
                  render: (row) =>
                    row.blocked_reason ? (
                      <Badge tone="amber">{row.blocked_reason}</Badge>
                    ) : (
                      <Badge tone="green">Eligible</Badge>
                    ),
                },
              ]}
              rows={data}
              onRowClick={(row) => setSelectedSignalId(row.id)}
            />
          ) : null}
        </Card>

        <Card
          title="Decision History"
          right={
            <Badge tone="muted">
              {decisionsData ? `${decisionsData.total} records` : "—"} · dry-run
            </Badge>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Read-only log of dry-run signal decisions. No orders placed.
          </div>
          {decisionsLoading && !decisionsData ? (
            <div className="state">Loading decision history...</div>
          ) : null}
          {decisionsError && !decisionsData ? (
            <div className="state error">{decisionsError}</div>
          ) : null}
          {decisionsData ? (
            <SignalDecisionRows records={decisionsData.decisions} />
          ) : null}
        </Card>

        <Card
          title="Signal Lifecycle"
          right={
            <Badge tone="muted">
              {lifecycleData ? `${lifecycleData.total} paths` : "-"} · GET-only
            </Badge>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Read-only signal path from receipt through safety checks, dry-run
            outcome, and audit correlation. Dry-run allowed is not an order.
          </div>
          {lifecycleLoading && !lifecycleData ? (
            <div className="state">Loading signal lifecycle...</div>
          ) : null}
          {lifecycleError && !lifecycleData ? (
            <div className="state error">{lifecycleError}</div>
          ) : null}
          {lifecycleData ? (
            <SignalLifecyclePanel records={lifecycleData.lifecycle} />
          ) : null}
        </Card>

        <Card
          title="API Signal History"
          right={
            <Badge tone="muted">
              {mellyRows.length} entries · read-only
            </Badge>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Sprint 1A signal records from the MellyTrade API (read-only,
            confidence clamped to [33, 85]).
          </div>
          <div className="audit-feed-controls">
            <label htmlFor="melly-symbol" className="dashboard-muted">
              Symbol
            </label>
            <input
              id="melly-symbol"
              type="text"
              placeholder="e.g. EURUSD"
              value={mellySymbol}
              onChange={(event) => setMellySymbol(event.target.value)}
              maxLength={16}
            />
            <label htmlFor="melly-status" className="dashboard-muted">
              Status
            </label>
            <select
              id="melly-status"
              value={mellyStatus}
              onChange={(event) =>
                setMellyStatus(event.target.value as MellyStatusFilter)
              }
            >
              <option value="">All</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          {mellyLoading && !mellySignals ? (
            <div className="state">Loading API signals...</div>
          ) : null}
          {mellyError && !mellySignals ? (
            <div className="state error">{mellyError}</div>
          ) : null}
          {mellySignals && mellyRows.length === 0 ? (
            <div className="state">No signals match this filter.</div>
          ) : null}
          {mellyRows.length > 0 ? (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Conf</th>
                    <th>Clamped</th>
                    <th>Risk %</th>
                    <th>Status</th>
                    <th>Reason</th>
                    <th>Mode</th>
                  </tr>
                </thead>
                <tbody>
                  {mellyRows.map((row) => {
                    const ts = new Date(row.created_at);
                    const time = Number.isNaN(ts.getTime())
                      ? row.created_at
                      : ts.toLocaleString("en-GB", {
                          day: "2-digit",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                          second: "2-digit",
                        });
                    const rowClass =
                      row.status === "rejected" ? "signal-row-rejected" : undefined;
                    return (
                      <tr key={row.id} className={rowClass}>
                        <td>{time}</td>
                        <td>{row.symbol}</td>
                        <td>
                          <Badge tone={actionTone(row.action)}>{row.action}</Badge>
                        </td>
                        <td>{row.confidence.toFixed(1)}</td>
                        <td>{row.confidence_clamped.toFixed(1)}</td>
                        <td>{row.risk_pct.toFixed(2)}%</td>
                        <td>
                          <Badge tone={statusTone(row.status)}>{row.status}</Badge>
                        </td>
                        <td>{row.rejection_reason ?? row.reason ?? "-"}</td>
                        <td>
                          <Badge tone={row.dry_run ? "green" : "amber"}>
                            {row.dry_run ? "dry-run" : "live"}
                          </Badge>{" "}
                          <Badge tone={row.read_only ? "green" : "amber"}>
                            {row.read_only ? "read-only" : "writable"}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : null}
        </Card>
      </div>

      <Drawer
        open={Boolean(selectedSignalId && detail)}
        title={detail ? `${detail.symbol} ${detail.direction}` : "Signal Detail"}
        onClose={() => setSelectedSignalId(null)}
      >
        {detail ? (
          <div className="stack">
            <div className="signal-drawer-grid">
              <div className="detail-tile">
                <span>Direction</span>
                <Badge tone={directionTone(detail.direction)}>{detail.direction}</Badge>
              </div>
              <div className="detail-tile">
                <span>Confidence</span>
                <strong>{detail.confidence}%</strong>
              </div>
              <div className="detail-tile">
                <span>Regime</span>
                <strong>{detail.regime}</strong>
              </div>
              <div className="detail-tile">
                <span>R:R</span>
                <strong>{formatOptional(detail.rr)}</strong>
              </div>
            </div>

            <div className="detail-row">
              <span>Levels</span>
              <div className="detail-grid">
                <strong>Entry {formatOptional(detail.entry)}</strong>
                <strong>SL {formatOptional(detail.sl)}</strong>
                <strong>TP {formatOptional(detail.tp)}</strong>
              </div>
            </div>

            <div className="detail-row">
              <span>Reasoning</span>
              <p>{detail.reasoning}</p>
            </div>

            <div className="detail-row">
              <span>Risk Gates</span>
              <ul className="compact-list">
                {reasoning?.risk_gate_results.map((item) => (
                  <li key={item.gate}>
                    {item.gate}: {item.passed ? "PASS" : "BLOCK"}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}
