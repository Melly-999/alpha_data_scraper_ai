import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { MiniChart } from "../components/shared/MiniChart";
import { Table } from "../components/shared/Table";
import { useBrokerAccount, useBrokerHealth } from "../hooks/useBroker";
import { useDashboard } from "../hooks/useDashboard";
import { useHealth } from "../hooks/useHealth";
import { useRiskConfig } from "../hooks/useRisk";
import type { ActivityFeedItem, SignalSummary, WatchlistItem } from "../types/api";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatTimestamp(value: string) {
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

function directionTone(direction: string): "green" | "red" | "amber" | "muted" {
  if (direction === "BUY") {
    return "green";
  }
  if (direction === "SELL") {
    return "red";
  }
  if (direction === "HOLD") {
    return "amber";
  }
  return "muted";
}

function activityTone(type: string): "green" | "red" | "amber" | "blue" | "muted" {
  const normalized = type.toLowerCase();
  if (normalized.includes("error") || normalized.includes("reject")) {
    return "red";
  }
  if (normalized.includes("risk") || normalized.includes("blocked")) {
    return "amber";
  }
  if (normalized.includes("signal") || normalized.includes("info")) {
    return "blue";
  }
  if (normalized.includes("connect") || normalized.includes("fill")) {
    return "green";
  }
  return "muted";
}

function MetricCard({
  label,
  value,
  detail,
  tone = "muted",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "green" | "red" | "amber" | "blue" | "muted";
}) {
  return (
    <div className={`dashboard-metric-card dashboard-metric-${tone}`}>
      <div className="dashboard-metric-label">{label}</div>
      <div className="dashboard-metric-value">{value}</div>
      <div className="dashboard-metric-detail">{detail}</div>
    </div>
  );
}

function WatchlistRows({ rows }: { rows: WatchlistItem[] }) {
  return (
    <div className="dashboard-row-list">
      {rows.map((row) => (
        <div key={row.symbol} className="dashboard-row">
          <div>
            <div className="dashboard-symbol">{row.symbol}</div>
            <div className="dashboard-muted">
              Bid {row.bid.toFixed(5)} / Ask {row.ask.toFixed(5)}
            </div>
          </div>
          <div className="dashboard-row-end">
            <span
              className={`dashboard-change ${
                row.change > 0 ? "positive" : row.change < 0 ? "negative" : "flat"
              }`}
            >
              {row.change > 0 ? "+" : ""}
              {row.change.toFixed(2)}%
            </span>
            <Badge tone={directionTone(row.signal)}>
              {row.signal}
              {row.confidence ? ` ${row.confidence}%` : ""}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

function SignalRows({ rows }: { rows: SignalSummary[] }) {
  return (
    <div className="dashboard-row-list">
      {rows.length === 0 ? (
        <div className="state">No ready signals in the latest dashboard summary.</div>
      ) : (
        rows.map((row) => (
          <div key={row.id} className="dashboard-row">
            <div>
              <div className="dashboard-signal-line">
                <Badge tone={directionTone(row.direction)}>{row.direction}</Badge>
                <span className="dashboard-symbol">{row.symbol}</span>
                <span className="dashboard-muted">{row.confidence}%</span>
              </div>
              <div className="dashboard-muted">
                {row.blocked
                  ? `Blocked: ${row.blocked_reason ?? "risk gate"}`
                  : `${row.regime} / MTF ${row.mtf_alignment}/${row.mtf_total}`}
              </div>
            </div>
            <Badge tone={row.blocked ? "amber" : "green"}>
              {row.blocked ? "Blocked" : "Eligible"}
            </Badge>
          </div>
        ))
      )}
    </div>
  );
}

function ActivityRows({ rows }: { rows: ActivityFeedItem[] }) {
  return (
    <div className="dashboard-row-list">
      {rows.map((row) => (
        <div key={`${row.time}-${row.msg}`} className="dashboard-row activity-row">
          <span className="activity-time">{row.time}</span>
          <Badge tone={activityTone(row.type)}>{row.type}</Badge>
          <span className="dashboard-muted activity-message">{row.msg}</span>
        </div>
      ))}
    </div>
  );
}

export function DashboardPage() {
  const { data, loading, error } = useDashboard();
  const health = useHealth();
  const riskConfig = useRiskConfig();
  const brokerHealth = useBrokerHealth();
  const brokerAccount = useBrokerAccount();

  if (loading && !data) {
    return <div className="state">Loading dashboard...</div>;
  }
  if (error && !data) {
    return <div className="state error">{error}</div>;
  }
  if (!data) {
    return null;
  }

  const safety = riskConfig.data ?? health.data?.safety ?? null;
  const dryRun = safety?.dry_run ?? true;
  const autoTrade = safety?.auto_trade ?? false;
  const riskExposurePct = Math.min(data.risk_status.risk_exposure * 100, 100);

  return (
    <div className="dashboard-v2">
      <section className="dashboard-v2-header">
        <div>
          <div className="eyebrow">MellyTrade Terminal</div>
          <h1 className="dashboard-title">Dashboard</h1>
          <div className="dashboard-muted">
            {data.system_status.symbol} / {data.system_status.mode} / updated{" "}
            {formatTimestamp(data.generated_at)}
          </div>
        </div>
        <div className="dashboard-status-strip">
          <Badge tone={dryRun ? "blue" : "red"}>{dryRun ? "DRY RUN" : "LIVE"}</Badge>
          <Badge tone={autoTrade ? "red" : "muted"}>
            {autoTrade ? "AUTO TRADE ON" : "AUTO TRADE OFF"}
          </Badge>
          <Badge tone="amber">Live orders: BLOCKED</Badge>
          <Badge tone={brokerHealth.data?.supports_live_orders ? "red" : "green"}>
            supports_live_orders=
            {brokerHealth.data?.supports_live_orders ? "true" : "false"}
          </Badge>
        </div>
      </section>

      <div className="dashboard-metric-grid">
        <MetricCard
          label="Balance"
          value={formatCurrency(data.account.balance)}
          detail={`Equity ${formatCurrency(data.account.equity)}`}
        />
        <MetricCard
          label="Daily PnL"
          value={formatCurrency(data.account.daily_pnl)}
          detail={`${data.account.daily_pnl_pct.toFixed(2)}% today`}
          tone={data.account.daily_pnl >= 0 ? "green" : "red"}
        />
        <MetricCard
          label="Ready Signals"
          value={`${data.ready_signals.length}`}
          detail="Eligible setups from backend summary"
          tone="blue"
        />
        <MetricCard
          label="Risk Exposure"
          value={`${riskExposurePct.toFixed(0)}%`}
          detail={`Emergency pause ${
            data.risk_status.emergency_pause ? "active" : "clear"
          }`}
          tone={data.risk_status.emergency_pause ? "red" : "amber"}
        />
      </div>

      <div className="dashboard-main-grid">
        <Card
          title="Equity Curve"
          right={<span className="card-kicker">real dashboard summary</span>}
        >
          <div className="dashboard-chart-panel">
            <MiniChart points={data.equity_curve} />
            <div className="dashboard-chart-footer">
              <span>Open positions: {data.account.open_positions}</span>
              <span>Trades today: {data.account.today_trades}</span>
              <span>Drawdown: {data.account.drawdown.toFixed(2)}%</span>
            </div>
          </div>
        </Card>

        <Card
          title="Watchlist"
          right={<Badge tone="blue">{data.watchlist.length} symbols</Badge>}
        >
          <WatchlistRows rows={data.watchlist} />
        </Card>

        <Card title="Broker">
          <div className="dashboard-row-list">
            {brokerHealth.error ? (
              <div className="state error">Broker status unavailable</div>
            ) : (
              <>
                <div className="dashboard-row">
                  <span className="dashboard-symbol">
                    {brokerHealth.data?.adapter ?? "ibkr_paper"}
                  </span>
                  <Badge tone={brokerHealth.data?.connected ? "green" : "amber"}>
                    {brokerHealth.data?.connected
                      ? "Connected"
                      : brokerHealth.data?.status ?? "Disconnected"}
                  </Badge>
                </div>
                <div className="broker-grid broker-grid-v2">
                  <span>Mode</span>
                  <strong>{brokerHealth.data?.mode ?? "paper"}</strong>
                  <span>Live orders</span>
                  <strong className="danger-text">BLOCKED</strong>
                  <span>Supports live</span>
                  <strong>
                    {brokerHealth.data?.supports_live_orders ? "true" : "false"}
                  </strong>
                  <span>Read only</span>
                  <strong>{brokerHealth.data?.read_only === false ? "false" : "true"}</strong>
                  <span>Account</span>
                  <strong>{brokerAccount.data?.account ?? "Disconnected"}</strong>
                  <span>Cash</span>
                  <strong>
                    {brokerAccount.data
                      ? `${brokerAccount.data.currency} ${brokerAccount.data.cash.toFixed(2)}`
                      : "Unavailable"}
                  </strong>
                </div>
                {!brokerHealth.data?.connected ? (
                  <div className="dashboard-safe-note">
                    Safe disconnected paper state. No order controls are exposed.
                  </div>
                ) : null}
              </>
            )}
          </div>
        </Card>

        <Card
          title="Ready Signals"
          right={<Badge tone="green">{data.ready_signals.length} total</Badge>}
        >
          <SignalRows rows={data.ready_signals.slice(0, 5)} />
        </Card>

        <Card title="Activity">
          <ActivityRows rows={data.activity_feed.slice(0, 7)} />
        </Card>

        <Card title="System Health">
          <div className="dashboard-row-list">
            <div className="dashboard-row">
              <span>MT5</span>
              <Badge tone={data.system_status.mt5.active ? "green" : "amber"}>
                {data.system_status.mt5.active ? "Connected" : "Fallback"}
              </Badge>
            </div>
            <div className="dashboard-row">
              <span>FastAPI</span>
              <Badge tone={data.system_status.api.healthy ? "green" : "red"}>
                {data.system_status.api.healthy ? "Healthy" : "Attention"}
              </Badge>
            </div>
            <div className="dashboard-row">
              <span>Claude</span>
              <Badge tone={data.system_status.claude.active ? "green" : "muted"}>
                {data.system_status.claude.active ? "Active" : "Unavailable"}
              </Badge>
            </div>
            <div className="dashboard-row">
              <span>News</span>
              <Badge tone={data.system_status.news.active ? "green" : "muted"}>
                {data.system_status.news.active ? "Active" : "Unavailable"}
              </Badge>
            </div>
          </div>
        </Card>

        <Card title="Risk Summary">
          <div className="dashboard-row-list">
            <div className="dashboard-row">
              <span>Daily loss</span>
              <strong>
                {data.risk_status.daily_loss_used.toFixed(2)} /{" "}
                {data.risk_status.daily_loss_limit.toFixed(2)}
              </strong>
            </div>
            <div className="dashboard-row">
              <span>Drawdown</span>
              <strong>
                {data.risk_status.drawdown_current.toFixed(2)} /{" "}
                {data.risk_status.drawdown_limit.toFixed(2)}
              </strong>
            </div>
            <div className="dashboard-row">
              <span>Positions</span>
              <strong>
                {data.risk_status.open_positions} /{" "}
                {data.risk_status.open_positions_limit}
              </strong>
            </div>
            <div className="dashboard-row">
              <span>Blocked / executed</span>
              <strong>
                {data.risk_status.trades_blocked} / {data.risk_status.trades_executed}
              </strong>
            </div>
          </div>
        </Card>

        <Card title="Execution Mode">
          <div className="dashboard-row-list">
            <div className="dashboard-row">
              <span>Runtime</span>
              <Badge tone={dryRun ? "blue" : "red"}>{dryRun ? "Dry run" : "Live"}</Badge>
            </div>
            <div className="dashboard-row">
              <span>Auto-trade</span>
              <Badge tone={autoTrade ? "red" : "muted"}>
                {autoTrade ? "Enabled" : "Disabled"}
              </Badge>
            </div>
            <div className="dashboard-row">
              <span>Min confidence</span>
              <strong>{safety ? `${safety.min_confidence}%` : "Unavailable"}</strong>
            </div>
            <div className="dashboard-row">
              <span>Cooldown</span>
              <strong>{safety ? `${safety.cooldown_seconds}s` : "Unavailable"}</strong>
            </div>
            <div className="dashboard-row">
              <span>Live orders</span>
              <Badge tone="amber">BLOCKED</Badge>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Ready Signal Table">
        <Table
          columns={[
            { key: "symbol", label: "Symbol", render: (row) => row.symbol },
            { key: "direction", label: "Direction", render: (row) => row.direction },
            { key: "confidence", label: "Conf", render: (row) => `${row.confidence}%` },
            { key: "regime", label: "Regime", render: (row) => row.regime },
            {
              key: "status",
              label: "Status",
              render: (row) => (row.blocked ? row.blocked_reason ?? "Blocked" : "Eligible"),
            },
          ]}
          rows={data.ready_signals}
        />
      </Card>
    </div>
  );
}
