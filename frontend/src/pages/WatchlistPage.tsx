import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { useWatchlist } from "../hooks/useWatchlist";
import type { WatchlistItem, WatchlistRiskState } from "../types/melly";

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function riskTone(
  riskState: WatchlistRiskState,
): "green" | "amber" | "red" | "muted" {
  switch (riskState) {
    case "clear":
      return "green";
    case "watch":
      return "amber";
    case "blocked":
      return "red";
    default:
      return "muted";
  }
}

function signalTone(status: string): "green" | "amber" | "red" | "muted" {
  if (status === "accepted") return "green";
  if (status === "rejected") return "red";
  if (status === "none") return "muted";
  return "amber";
}

function WatchlistRows({ rows }: { rows: WatchlistItem[] }) {
  if (rows.length === 0) {
    return <div className="state">No watchlist rows available.</div>;
  }

  return (
    <div className="watchlist-table">
      <div className="watchlist-table-head">
        <span>Symbol</span>
        <span>Price</span>
        <span>Signal</span>
        <span>Alerts</span>
        <span>Risk</span>
        <span>Source</span>
      </div>
      {rows.map((row) => (
        <div key={row.symbol} className="watchlist-table-row">
          <div>
            <div className="dashboard-symbol">{row.symbol}</div>
            <div className="dashboard-muted">
              {row.name} / {row.asset_class}
            </div>
          </div>
          <div>
            <div>{row.last_price.toFixed(row.last_price > 10 ? 2 : 5)}</div>
            <div
              className={`dashboard-change ${
                row.change_pct > 0
                  ? "positive"
                  : row.change_pct < 0
                    ? "negative"
                    : "flat"
              }`}
            >
              {row.change_pct > 0 ? "+" : ""}
              {row.change_pct.toFixed(2)}%
            </div>
          </div>
          <div>
            <Badge tone={signalTone(row.signal_status)}>
              {row.signal_status}
            </Badge>
            <div className="dashboard-muted">
              {row.signal_confidence === null
                ? "No signal"
                : `${row.signal_confidence.toFixed(0)} confidence`}
            </div>
          </div>
          <div>{row.alert_count}</div>
          <div>
            <Badge tone={riskTone(row.risk_state)}>{row.risk_state}</Badge>
          </div>
          <div>
            <div className="dashboard-muted">{row.source}</div>
            <div className="watchlist-generated">
              {formatTimestamp(row.generated_at)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function WatchlistPage() {
  const { data, loading, error } = useWatchlist();
  const rows = data ?? [];
  const blocked = rows.filter((row) => row.risk_state === "blocked").length;
  const watching = rows.filter((row) => row.risk_state === "watch").length;

  return (
    <div className="page-grid passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Watchlist</div>
            <h1 className="page-title">Read-only market watchlist</h1>
            <div className="dashboard-muted">
              Safe fallback market rows enriched with existing signal status,
              alert counts, and risk state. No actions are exposed.
            </div>
          </div>
          <div className="page-header-meta">
            <Badge tone="green">read-only</Badge>
            <Badge tone={blocked > 0 ? "red" : "green"}>{blocked} blocked</Badge>
            <Badge tone={watching > 0 ? "amber" : "muted"}>
              {watching} watch
            </Badge>
          </div>
        </section>

        <Card
          title="Watchlist"
          right={<Badge tone="blue">{rows.length} symbols</Badge>}
        >
          {loading && rows.length === 0 ? (
            <div className="state">Loading watchlist...</div>
          ) : null}
          {error && rows.length === 0 ? (
            <div className="state error">{error}</div>
          ) : null}
          {error && rows.length > 0 ? (
            <div className="state error">{error}</div>
          ) : null}
          {!loading && !error && rows.length === 0 ? (
            <div className="state">No watchlist rows available.</div>
          ) : null}
          <WatchlistRows rows={rows} />
        </Card>
      </div>
    </div>
  );
}
