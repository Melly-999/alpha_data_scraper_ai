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
            <div className="status-row">
              <span>Degraded</span>
              <Badge tone={data.degraded_services.length ? "amber" : "green"}>
                {data.degraded_services.length
                  ? data.degraded_services.join(", ")
                  : "None"}
              </Badge>
            </div>
          </div>
        </Card>
      </div>

      {data.analytics_summary ? (
        <div className="stats-grid">
          <Card title="Analytics Trades">
            <div className="stat-value">{data.analytics_summary.total_trades}</div>
            <div className="stat-subtle">{data.analytics_summary.source}</div>
          </Card>
          <Card title="Analytics Win Rate">
            <div className="stat-value">{data.analytics_summary.win_rate.toFixed(2)}%</div>
            <div className="stat-subtle">Cache {data.analytics_summary.cache_age_seconds}s</div>
          </Card>
          <Card title="Analytics Sharpe">
            <div className="stat-value">{data.analytics_summary.sharpe_ratio.toFixed(2)}</div>
            <div className="stat-subtle">
              {data.analytics_summary.fallback ? "Fallback" : "Live backtest"}
            </div>
          </Card>
          <Card title="Analytics Max DD">
            <div className="stat-value">{data.analytics_summary.max_drawdown.toFixed(2)}%</div>
            <div className="stat-subtle">
              Return {data.analytics_summary.total_return.toFixed(2)}%
            </div>
          </Card>
        </div>
      ) : null}

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
