import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { MiniChart } from "../components/shared/MiniChart";
import { Table } from "../components/shared/Table";
import { useDashboard } from "../hooks/useDashboard";

export function DashboardPage() {
  const { data, loading, error } = useDashboard();

  if (loading && !data) {
    return <div className="state">Loading dashboard…</div>;
  }
  if (error && !data) {
    return <div className="state error">{error}</div>;
  }
  if (!data) {
    return null;
  }

  return (
    <div className="page-grid">
      <div className="stats-grid">
        <Card title="Account Equity">
          <div className="stat-value">${data.account.equity.toFixed(2)}</div>
          <div className="stat-subtle">Balance ${data.account.balance.toFixed(2)}</div>
        </Card>
        <Card title="Daily PnL">
          <div className="stat-value">${data.account.daily_pnl.toFixed(2)}</div>
          <div className="stat-subtle">{data.account.daily_pnl_pct.toFixed(2)}%</div>
        </Card>
        <Card title="Ready Signals">
          <div className="stat-value">{data.ready_signals.length}</div>
          <div className="stat-subtle">Eligible setups</div>
        </Card>
        <Card title="Risk Exposure">
          <div className="stat-value">{(data.risk_status.risk_exposure * 100).toFixed(0)}%</div>
          <div className="stat-subtle">Emergency: {data.risk_status.emergency_pause ? "ON" : "OFF"}</div>
        </Card>
      </div>

      <div className="two-column">
        <Card title="Equity Curve">
          <MiniChart points={data.equity_curve} />
        </Card>
        <Card title="System Status">
          <div className="stack">
            <div className="status-row">
              <span>MT5</span>
              <Badge tone={data.system_status.mt5.active ? "green" : "amber"}>
                {data.system_status.mt5.active ? "Connected" : "Fallback"}
              </Badge>
            </div>
            <div className="status-row">
              <span>Claude</span>
              <Badge tone={data.system_status.claude.active ? "green" : "muted"}>
                {data.system_status.claude.active ? "Active" : "Unavailable"}
              </Badge>
            </div>
            <div className="status-row">
              <span>News</span>
              <Badge tone={data.system_status.news.active ? "green" : "muted"}>
                {data.system_status.news.active ? "Active" : "Unavailable"}
              </Badge>
            </div>
          </div>
        </Card>
      </div>

      <div className="two-column">
        <Card title="Ready Signals">
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              { key: "direction", label: "Direction", render: (row) => row.direction },
              { key: "confidence", label: "Conf", render: (row) => `${row.confidence}%` },
            ]}
            rows={data.ready_signals}
          />
        </Card>
        <Card title="Watchlist">
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              { key: "signal", label: "Signal", render: (row) => row.signal },
              {
                key: "confidence",
                label: "Conf",
                render: (row) => row.confidence ?? "—",
              },
            ]}
            rows={data.watchlist.map((item) => ({ ...item, id: item.symbol }))}
          />
        </Card>
      </div>

      <Card title="Activity Feed">
        <div className="activity-list">
          {data.activity_feed.map((item) => (
            <div key={`${item.time}-${item.msg}`} className="activity-item">
              <span className="activity-time">{item.time}</span>
              <span>{item.msg}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
