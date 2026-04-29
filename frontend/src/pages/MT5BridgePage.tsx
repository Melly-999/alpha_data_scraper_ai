import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useMt5Status } from "../hooks/useMt5";

export function MT5BridgePage() {
  const { data } = useMt5Status();

  return (
    <div className="page-grid passive-page">
      <section className="page-header">
        <div>
          <div className="eyebrow">MT5 Bridge</div>
          <h1 className="page-title">Terminal Connectivity</h1>
          <div className="dashboard-muted">Status-only view of MT5 sync state.</div>
        </div>
        <div className="page-header-meta">
          <Badge tone={data?.connected ? "green" : "amber"}>
            {data?.connected ? "Connected" : "Fallback"}
          </Badge>
          <Badge tone={data?.fallback ? "amber" : "green"}>
            {data?.fallback ? "Synthetic fallback" : "Primary feed"}
          </Badge>
        </div>
      </section>

      <div className="passive-metric-grid">
        <div className="passive-status-card">
          <span>Server</span>
          <strong>{data?.server ?? "Unavailable"}</strong>
        </div>
        <div className="passive-status-card">
          <span>Account</span>
          <strong>{data?.account_name ?? "Unavailable"}</strong>
        </div>
        <div className="passive-status-card">
          <span>Latency</span>
          <strong>{data ? `${data.latency_ms} ms` : "Unavailable"}</strong>
        </div>
        <div className="passive-status-card">
          <span>Symbols</span>
          <strong>{data ? `${data.symbols_loaded}` : "Unavailable"}</strong>
        </div>
      </div>

      <div className="two-column">
        <Card title="Sync Status">
          {data ? (
            <div className="status-row-list">
              <div className="status-row">
                <span>Orders sync</span>
                <Badge tone={data.orders_sync ? "green" : "amber"}>
                  {data.orders_sync ? "Synced" : "Pending"}
                </Badge>
              </div>
              <div className="status-row">
                <span>Positions sync</span>
                <Badge tone={data.positions_sync ? "green" : "amber"}>
                  {data.positions_sync ? "Synced" : "Pending"}
                </Badge>
              </div>
              <div className="status-row">
                <span>Build</span>
                <strong>{data.build_version}</strong>
              </div>
              <div className="status-row">
                <span>Last heartbeat</span>
                <strong>{data.last_heartbeat}</strong>
              </div>
            </div>
          ) : (
            <div className="state">MT5 status unavailable</div>
          )}
        </Card>

        <Card title="Broker Account">
          {data ? (
            <div className="status-row-list">
              <div className="status-row">
                <span>Broker</span>
                <strong>{data.broker}</strong>
              </div>
              <div className="status-row">
                <span>Account ID</span>
                <strong>{data.account_id}</strong>
              </div>
              <div className="status-row">
                <span>Currency</span>
                <strong>{data.currency}</strong>
              </div>
              <div className="status-row">
                <span>Leverage</span>
                <strong>{data.leverage}</strong>
              </div>
            </div>
          ) : (
            <div className="state">Account data unavailable</div>
          )}
        </Card>
      </div>

      <Card title="Connection Log">
        {data ? (
          <Table
            columns={[
              { key: "time", label: "Time", render: (row) => row.time },
              {
                key: "event",
                label: "Event",
                render: (row) => <Badge tone="blue">{row.event}</Badge>,
              },
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
