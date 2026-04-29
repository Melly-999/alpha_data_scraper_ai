import { useEffect, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Drawer } from "../components/shared/Drawer";
import { Table } from "../components/shared/Table";
import { useSignals } from "../hooks/useSignals";
import { apiGet } from "../lib/api";
import { useUiStore } from "../stores/useUiStore";
import type { Direction, SignalDetail, SignalReasoning } from "../types/api";

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

export function SignalsPage() {
  const { data, loading, error } = useSignals();
  const selectedSignalId = useUiStore((state) => state.selectedSignalId);
  const setSelectedSignalId = useUiStore((state) => state.setSelectedSignalId);
  const [detail, setDetail] = useState<SignalDetail | null>(null);
  const [reasoning, setReasoning] = useState<SignalReasoning | null>(null);

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
