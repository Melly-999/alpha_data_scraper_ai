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
        {detail ? (
          <div className="stack">
            <div className="detail-row">
              <span>Confidence</span>
              <strong>{detail.confidence}%</strong>
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

