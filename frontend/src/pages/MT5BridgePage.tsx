import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useMt5Status } from "../hooks/useMt5";

export function MT5BridgePage() {
  const { data } = useMt5Status();

  return (
    <div className="page-grid">
      <Card title="MT5 Status">
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

