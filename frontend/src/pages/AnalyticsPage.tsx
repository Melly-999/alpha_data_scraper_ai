import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useAnalytics } from "../hooks/useAnalytics";

export function AnalyticsPage() {
  const { data, loading, error } = useAnalytics();

  if (loading && !data) {
    return <div className="state">Loading analytics…</div>;
  }
  if (error && !data) {
    return <div className="state error">{error}</div>;
  }
  if (!data) {
    return <div className="state">No analytics available.</div>;
  }

  return (
    <div className="page-grid">
      <div className="stats-grid">
        <Card title="Total Trades">
          <div className="stat-value">{data.total_trades}</div>
          <div className="stat-subtle">{data.symbol} · {data.timeframe}</div>
        </Card>
        <Card title="Win Rate">
          <div className="stat-value">{data.win_rate.toFixed(2)}%</div>
          <div className="stat-subtle">Read-only analytics</div>
        </Card>
        <Card title="Sharpe">
          <div className="stat-value">{data.sharpe_ratio.toFixed(2)}</div>
          <div className="stat-subtle">Risk-adjusted return</div>
        </Card>
        <Card title="Profit Factor">
          <div className="stat-value">{data.profit_factor.toFixed(2)}x</div>
          <div className="stat-subtle">Source {data.source}</div>
        </Card>
      </div>

      <Card
        title="Analytics State"
        right={
          <Badge tone={data.fallback ? "amber" : "green"}>
            {data.fallback ? "Fallback" : "Backtest Engine"}
          </Badge>
        }
      >
        <div className="stack">
          <div className="detail-row">
            <span>Total Return</span>
            <strong>{data.total_return.toFixed(2)}%</strong>
          </div>
          <div className="detail-row">
            <span>Max Drawdown</span>
            <strong>{data.max_drawdown.toFixed(2)}%</strong>
          </div>
          <div className="detail-row">
            <span>Cache Age</span>
            <strong>{data.cache_age_seconds}s</strong>
          </div>
        </div>
      </Card>

      <Card title="Highlights">
        <Table
          columns={[
            { key: "label", label: "Metric", render: (row) => row.label },
            { key: "formatted", label: "Value", render: (row) => row.formatted },
          ]}
          rows={data.highlights.map((item) => ({ ...item, id: item.label }))}
        />
      </Card>
    </div>
  );
}
