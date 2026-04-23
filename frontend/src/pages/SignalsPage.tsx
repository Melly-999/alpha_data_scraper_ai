import { useEffect, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Drawer } from "../components/shared/Drawer";
import { Table } from "../components/shared/Table";
import { useSignals } from "../hooks/useSignals";
import { apiGet } from "../lib/api";
import { useUiStore } from "../stores/useUiStore";
import type { SignalDetail, SignalReasoning } from "../types/api";

export function SignalsPage() {
  const { data, loading, error } = useSignals();
  const selectedSignalId = useUiStore((state) => state.selectedSignalId);
  const setSelectedSignalId = useUiStore((state) => state.setSelectedSignalId);
  const [detail, setDetail] = useState<SignalDetail | null>(null);
  const [reasoning, setReasoning] = useState<SignalReasoning | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedSignalId) {
      setDetail(null);
      setReasoning(null);
      setDetailError(null);
      return;
    }
    void apiGet<SignalDetail>(`/signals/${selectedSignalId}`)
      .then((next) => {
        setDetail(next);
        setDetailError(null);
      })
      .catch((nextError: unknown) => {
        setDetailError(
          nextError instanceof Error ? nextError.message : "Failed to load signal detail",
        );
      });
    void apiGet<SignalReasoning>(`/signals/${selectedSignalId}/reasoning`)
      .then(setReasoning)
      .catch(() => setReasoning(null));
  }, [selectedSignalId]);

  return (
    <div className="page-grid with-drawer">
      <Card title="Signals">
        {loading && !data ? <div className="state">Loading signals…</div> : null}
        {error && !data ? <div className="state error">{error}</div> : null}
        {data ? (
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              {
                key: "direction",
                label: "Direction",
                render: (row) => row.direction,
              },
              {
                key: "confidence",
                label: "Conf",
                render: (row) => `${row.confidence}%`,
              },
              {
                key: "blocked_reason",
                label: "Risk",
                render: (row) =>
                  row.blocked_reason ? (
                    <Badge tone="amber">{row.blocked_reason}</Badge>
                  ) : (
                    <Badge tone="green">ELIGIBLE</Badge>
                  ),
              },
              {
                key: "timestamp",
                label: "Age",
                render: (row) =>
                  `${Math.max(0, Math.round((Date.now() - new Date(row.timestamp).getTime()) / 1000))}s`,
              },
            ]}
            rows={data}
            onRowClick={(row) => setSelectedSignalId(row.id)}
          />
        ) : null}
      </Card>
      <Drawer
        open={Boolean(selectedSignalId && detail)}
        title={detail ? `${detail.symbol} ${detail.direction}` : "Signal Detail"}
        onClose={() => setSelectedSignalId(null)}
      >
        {detailError ? <div className="state error">{detailError}</div> : null}
        {detail ? (
          <div className="stack">
            <div className="detail-row">
              <span>Confidence</span>
              <strong>{detail.confidence}%</strong>
            </div>
            <div className="detail-row">
              <span>Source</span>
              <Badge tone={detail.provenance.fallback ? "amber" : "green"}>
                {detail.provenance.signal_source} / {detail.provenance.market_data_source}
              </Badge>
            </div>
            <div className="detail-row">
              <span>Validation</span>
              <p>{detail.ai_validation_status ?? "No validation metadata."}</p>
            </div>
            <div className="detail-row">
              <span>Reasoning</span>
              <p>{detail.reasoning}</p>
            </div>
            <div className="detail-row">
              <span>Confidence Model</span>
              <p>{reasoning?.confidence_explainer ?? detail.confidence_explainer}</p>
            </div>
            <div className="detail-row">
              <span>Technical Inputs</span>
              <ul className="compact-list">
                {detail.technical_input_summary.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
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
            <div className="detail-row">
              <span>Cache</span>
              <strong>{detail.provenance.cache_age_seconds}s</strong>
            </div>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}
