import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useMt5Status } from "../hooks/useMt5";
import { Badge } from "../components/shared/Badge";

export function MT5BridgePage() {
  const { data, loading, error } = useMt5Status();

  if (loading && !data) {
    return <div className="state">Loading MT5 bridge…</div>;
  }
  if (error && !data) {
    return <div className="state error">{error}</div>;
  }

  return (
    <div className="page-grid">
      <Card
        title="MT5 Status"
        right={
          data ? (
            <Badge tone={data.fallback ? "amber" : "green"}>
              {data.fallback ? "Fallback Read Model" : "Live Read Adapter"}
            </Badge>
          ) : null
        }
      >
        {data ? (
          <div className="stack">
            <div className="detail-row">
              <span>Server</span>
              <strong>{data.server}</strong>
            </div>
            <div className="detail-row">
              <span>Account</span>
              <strong>{data.account_name}</strong>
            </div>
            <div className="detail-row">
              <span>Latency</span>
              <strong>{data.latency_ms} ms</strong>
            </div>
            <div className="detail-row">
              <span>Read Only</span>
              <strong>{data.read_only ? "Yes" : "No"}</strong>
            </div>
            <div className="detail-row">
              <span>Cache Age</span>
              <strong>{data.cache_age_seconds}s</strong>
            </div>
            <div className="detail-row">
              <span>Terminal Path</span>
              <strong>{data.terminal_path || "Unavailable"}</strong>
            </div>
          </div>
        ) : null}
      </Card>
      <Card title="Connection Log">
        {data ? (
          <Table
            columns={[
              { key: "time", label: "Time", render: (row) => row.time },
              { key: "event", label: "Event", render: (row) => row.event },
              { key: "msg", label: "Message", render: (row) => row.msg },
            ]}
            rows={data.connection_logs.map((row, index) => ({
              ...row,
              id: `${row.time}-${index}`,
            }))}
          />
        ) : null}
      </Card>
    </div>
  );
}
