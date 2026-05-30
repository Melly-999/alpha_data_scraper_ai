import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { MellyPetMascot } from "../branding/MellyPetMascot";
import { useOpenPositions, usePositionHistory } from "../../hooks/usePositions";
import { usePollingResource } from "../../hooks/usePollingResource";
import { apiGet } from "../../lib/api";
import type { OrderRow, PositionSummary } from "../../types/api";
import type { TerminalShellData } from "./TerminalShell";
import { MiniChart } from "../shared/MiniChart";
import { SafetyBadges } from "./SafetyBadges";

type TabKey = "positions" | "blotter" | "backtest";
type BlotterFilter = "all" | "filled" | "pending" | "blocked";

type BlotterRow = {
  id: string;
  time: string;
  symbol: string;
  direction: "BUY" | "SELL" | "HOLD";
  status: string;
  source: string;
  confidence: string;
  riskFlag: string;
  filter: BlotterFilter;
};

type BacktestRun = {
  id: string;
  label: string;
  timestamp: string;
  variant: string;
  outcome: string;
  mode: string;
};

const tabMeta: Array<{
  key: TabKey;
  label: string;
  kicker: string;
}> = [
  { key: "positions", label: "Positions", kicker: "Version B" },
  { key: "blotter", label: "Trade Blotter", kicker: "Version A" },
  { key: "backtest", label: "Backtest Lab", kicker: "Version C" },
];

const blotterFallbackRows: OrderRow[] = [
  {
    id: "demo-ord-1",
    ticket: 0,
    symbol: "EURUSD",
    direction: "BUY",
    type: "read_only_demo",
    lots: 0.25,
    price: 1.0784,
    status: "filled",
    source: "signal_engine",
    confidence: 79,
    slippage_pips: 0.1,
    submitted_at: "2026-05-29T08:15:00.000Z",
    filled_at: "2026-05-29T08:15:08.000Z",
    notes: "Local read-only placeholder row.",
  },
  {
    id: "demo-ord-2",
    ticket: 0,
    symbol: "XAUUSD",
    direction: "SELL",
    type: "read_only_demo",
    lots: 0.1,
    price: 2344.5,
    status: "pending",
    source: "scanner",
    confidence: 66,
    slippage_pips: null,
    submitted_at: "2026-05-29T08:42:00.000Z",
    notes: "Local read-only placeholder row.",
  },
  {
    id: "demo-ord-3",
    ticket: 0,
    symbol: "GBPUSD",
    direction: "HOLD",
    type: "read_only_demo",
    lots: 0.15,
    price: 1.2531,
    status: "blocked",
    source: "risk_gate",
    confidence: 58,
    slippage_pips: null,
    submitted_at: "2026-05-29T09:03:00.000Z",
    notes: "Local read-only placeholder row.",
  },
];

const demoSavedRuns: BacktestRun[] = [
  {
    id: "run-b-01",
    label: "EURUSD trend filter",
    timestamp: "2026-05-28 14:22",
    variant: "Approved pattern B",
    outcome: "+4.8% net",
    mode: "Read-only",
  },
  {
    id: "run-c-02",
    label: "Gold volatility clamp",
    timestamp: "2026-05-27 11:07",
    variant: "Approved pattern C",
    outcome: "1.31 PF",
    mode: "Read-only",
  },
  {
    id: "run-a-03",
    label: "Blotter audit replay",
    timestamp: "2026-05-26 09:54",
    variant: "Approved pattern A",
    outcome: "92 trades",
    mode: "Read-only",
  },
];

const demoEquityCurve = [
  100,
  101.5,
  102.2,
  101.8,
  103.5,
  104.1,
  103.9,
  105.6,
  106.4,
  106.0,
  107.2,
];

const demoDrawdownCurve = [
  0,
  -0.3,
  -0.7,
  -0.5,
  -1.2,
  -0.9,
  -1.6,
  -1.1,
  -2.0,
  -1.4,
  -2.4,
];

function formatNumber(value: number, digits = 2): string {
  return new Intl.NumberFormat("en-GB", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

function formatCurrency(value: number): string {
  const prefix = value >= 0 ? "+" : "";
  return `${prefix}$${formatNumber(value)}`;
}

function formatDuration(seconds: number): string {
  const totalMinutes = Math.max(0, Math.floor(seconds / 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

function formatTime(value?: string | null): string {
  if (!value) {
    return "—";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isSameLocalDay(left: string, right: Date): boolean {
  const parsed = new Date(left);
  return (
    !Number.isNaN(parsed.getTime()) &&
    parsed.getFullYear() === right.getFullYear() &&
    parsed.getMonth() === right.getMonth() &&
    parsed.getDate() === right.getDate()
  );
}

function directionTone(direction: PositionSummary["direction"] | "BUY" | "SELL" | "HOLD") {
  if (direction === "BUY") return "buy";
  if (direction === "SELL") return "sell";
  return "hold";
}

function statusTone(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized.includes("fill")) return "safe";
  if (normalized.includes("pend")) return "warn";
  if (normalized.includes("block")) return "danger";
  return "neutral";
}

function mapBlotterRows(rows: OrderRow[]): BlotterRow[] {
  return rows.map((row) => {
    const status = row.status.toLowerCase();
    const filter: BlotterFilter = status.includes("fill")
      ? "filled"
      : status.includes("pend")
        ? "pending"
        : status.includes("block")
          ? "blocked"
          : "all";

    return {
      id: row.id,
      time: formatTime(row.filled_at ?? row.submitted_at),
      symbol: row.symbol,
      direction: row.direction,
      status: row.status.toUpperCase(),
      source: row.source.replace(/_/g, " "),
      confidence: row.confidence != null ? `${Math.round(row.confidence)}%` : "—",
      riskFlag:
        status.includes("block") || row.source.includes("risk")
          ? "HUMAN REVIEW"
          : "READ ONLY",
      filter,
    };
  });
}

function sumPnL(rows: Array<{ unrealized_pnl?: number | null; realized_pnl?: number | null }>, key: "unrealized_pnl" | "realized_pnl"): number {
  return rows.reduce((total, row) => total + (row[key] ?? 0), 0);
}

function metricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="open-design-kpi-card">
      <div className="open-design-kpi-label">{label}</div>
      <div className="open-design-kpi-value">{value}</div>
      <div className="open-design-kpi-detail">{detail}</div>
    </div>
  );
}

function TableRow({ cells }: { cells: Array<ReactNode> }) {
  return (
    <div className="table-row open-design-table-row">
      {cells.map((cell, index) => (
        <div key={index}>{cell}</div>
      ))}
    </div>
  );
}

function OpenDesignPositionsTab({ data }: { data: TerminalShellData }) {
  const openPositions = useOpenPositions();
  const positionHistory = usePositionHistory();
  const today = useMemo(() => new Date(), []);

  const openRows = useMemo(() => {
    const source =
      openPositions.data && openPositions.data.length > 0
        ? openPositions.data
        : [
            {
              id: "demo-open-1",
              ticket: 0,
              symbol: "EURUSD",
              direction: "BUY" as const,
              lots: 0.25,
              open_price: 1.0784,
              current_price: 1.0811,
              unrealized_pnl: 68.4,
              duration_seconds: 5460,
              mt5_synced: false,
              open_time: "2026-05-29T07:34:00.000Z",
            },
            {
              id: "demo-open-2",
              ticket: 0,
              symbol: "XAUUSD",
              direction: "SELL" as const,
              lots: 0.1,
              open_price: 2345.2,
              current_price: 2338.8,
              unrealized_pnl: 64.0,
              duration_seconds: 3900,
              mt5_synced: false,
              open_time: "2026-05-29T08:10:00.000Z",
            },
          ];

    return source;
  }, [openPositions.data]);

  const closedTodayRows = useMemo(() => {
    const history = positionHistory.data ?? [];
    const filtered = history.filter((row) => row.close_time && isSameLocalDay(row.close_time, today));
    if (filtered.length > 0) {
      return filtered;
    }

    return [
      {
        id: "demo-closed-1",
        ticket: 0,
        symbol: "GBPUSD",
        direction: "BUY" as const,
        lots: 0.2,
        open_price: 1.2514,
        close_price: 1.2556,
        realized_pnl: 84.8,
        duration_seconds: 8400,
        mt5_synced: false,
        open_time: "2026-05-29T04:30:00.000Z",
        close_time: "2026-05-29T06:50:00.000Z",
      },
    ];
  }, [positionHistory.data, today]);

  const floatPnL = sumPnL(openRows, "unrealized_pnl");
  const realizedPnL = sumPnL(closedTodayRows, "realized_pnl");
  const openCount = openRows.length;
  const closedTodayCount = closedTodayRows.length;
  const riskPosture = data.riskStatus.live_orders_blocked ? "READ ONLY" : "GUARDED";
  const openStatusCopy = openPositions.loading && openPositions.data == null
    ? "Loading read-only positions …"
    : openPositions.error
      ? "Demo rows active while the position feed is unavailable."
      : "Read-only open book with approved premium layout.";
  const closedStatusCopy = positionHistory.loading && positionHistory.data == null
    ? "Loading closed-today rows …"
    : positionHistory.error
      ? "Demo rows active while the history feed is unavailable."
      : "Closed-today history shown for audit review only.";

  return (
    <div className="open-design-layout open-design-layout--positions">
      <div className="open-design-main">
        <div className="open-design-kpi-grid">
          {metricCard({
            label: "Float PnL",
            value: formatCurrency(floatPnL),
            detail: "Open book, read-only",
          })}
          {metricCard({
            label: "Realized PnL",
            value: formatCurrency(realizedPnL),
            detail: "Closed today only",
          })}
          {metricCard({
            label: "Open Count",
            value: String(openCount),
            detail: "Current open positions",
          })}
          {metricCard({
            label: "Closed Today",
            value: String(closedTodayCount),
            detail: "Historical audit rows",
          })}
          {metricCard({
            label: "Risk Posture",
            value: riskPosture,
            detail: "Human review required",
          })}
        </div>

        <section className="open-design-section">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Positions</div>
              <h3 className="open-design-section-title">Open positions</h3>
            </div>
            <span className="open-design-section-note">{openStatusCopy}</span>
          </div>
          <div className="terminal-table open-design-table">
            <div className="table-row table-head open-design-table-head">
              <span>Symbol</span>
              <span>Direction</span>
              <span>Lots</span>
              <span>Open</span>
              <span>Mark</span>
              <span>Float</span>
              <span>Duration</span>
              <span>Sync</span>
            </div>
            {openRows.map((row) => (
              <TableRow
                key={row.id}
                cells={[
                  <strong key="symbol">{row.symbol}</strong>,
                  <span
                    key="direction"
                    className={`open-design-chip open-design-chip--${directionTone(
                      row.direction,
                    )}`}
                  >
                    {row.direction}
                  </span>,
                  <span key="lots">{formatNumber(row.lots, 2)}</span>,
                  <span key="open">{formatNumber(row.open_price, row.open_price >= 100 ? 2 : 4)}</span>,
                  <span key="mark">{formatNumber(row.current_price ?? row.open_price, row.open_price >= 100 ? 2 : 4)}</span>,
                  <span
                    key="float"
                    className={((row.unrealized_pnl ?? 0) >= 0 ? "value-positive" : "value-negative")}
                  >
                    {formatCurrency(row.unrealized_pnl ?? 0)}
                  </span>,
                  <span key="duration">{formatDuration(row.duration_seconds)}</span>,
                  <span key="sync">{row.mt5_synced ? "SYNCED" : "DEMO"}</span>,
                ]}
              />
            ))}
          </div>
        </section>

        <section className="open-design-section">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Positions</div>
              <h3 className="open-design-section-title">Closed today</h3>
            </div>
            <span className="open-design-section-note">{closedStatusCopy}</span>
          </div>
          <div className="terminal-table open-design-table">
            <div className="table-row table-head open-design-table-head">
              <span>Close time</span>
              <span>Symbol</span>
              <span>Direction</span>
              <span>Lots</span>
              <span>Realized</span>
              <span>Duration</span>
              <span>Source</span>
            </div>
            {closedTodayRows.map((row) => (
              <TableRow
                key={row.id}
                cells={[
                  <span key="close-time">{formatTime(row.close_time)}</span>,
                  <strong key="symbol">{row.symbol}</strong>,
                  <span
                    key="direction"
                    className={`open-design-chip open-design-chip--${directionTone(
                      row.direction,
                    )}`}
                  >
                    {row.direction}
                  </span>,
                  <span key="lots">{formatNumber(row.lots, 2)}</span>,
                  <span
                    key="realized"
                    className={((row.realized_pnl ?? 0) >= 0 ? "value-positive" : "value-negative")}
                  >
                    {formatCurrency(row.realized_pnl ?? 0)}
                  </span>,
                  <span key="duration">{formatDuration(row.duration_seconds)}</span>,
                  <span key="source">{row.mt5_synced ? "SYNCED" : "DEMO"}</span>,
                ]}
              />
            ))}
          </div>
        </section>
      </div>

      <aside className="open-design-aside">
        <section className="open-design-side-card">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Read only</div>
              <h3 className="open-design-section-title">Terminal posture</h3>
            </div>
          </div>
          <div className="open-design-side-stack">
            <div className="open-design-side-row">
              <span>Mode</span>
              <strong>DRY RUN</strong>
            </div>
            <div className="open-design-side-row">
              <span>Auto trade</span>
              <strong>AUTO TRADE OFF</strong>
            </div>
            <div className="open-design-side-row">
              <span>Orders</span>
              <strong>LIVE ORDERS BLOCKED</strong>
            </div>
            <div className="open-design-side-row">
              <span>Human review</span>
              <strong>REQUIRED</strong>
            </div>
          </div>
          <div className="open-design-note-row">
            <span className="workspace-mini-pill">Icon concept</span>
            <span>Dark monochrome Melly PET mark</span>
          </div>
        </section>

        <MellyPetMascot />
      </aside>
    </div>
  );
}

function OpenDesignBlotterTab() {
  const orders = usePollingResource(() => apiGet<OrderRow[]>("/orders"), 5000);
  const [filter, setFilter] = useState<BlotterFilter>("all");

  const blotterRows = useMemo(() => {
    const mapped = mapBlotterRows(
      orders.data && orders.data.length > 0 ? orders.data : blotterFallbackRows,
    );
    return filter === "all" ? mapped : mapped.filter((row) => row.filter === filter);
  }, [filter, orders.data]);

  const counts = useMemo(() => {
    const source = mapBlotterRows(
      orders.data && orders.data.length > 0 ? orders.data : blotterFallbackRows,
    );
    return {
      all: source.length,
      filled: source.filter((row) => row.filter === "filled").length,
      pending: source.filter((row) => row.filter === "pending").length,
      blocked: source.filter((row) => row.filter === "blocked").length,
    };
  }, [orders.data]);

  const filterCopy =
    orders.loading && orders.data == null
      ? "Loading read-only blotter rows …"
      : orders.error
        ? "Demo rows active while the execution feed is unavailable."
        : "Audit-style blotter rows filtered locally only.";

  return (
    <div className="open-design-layout open-design-layout--blotter">
      <div className="open-design-main">
        <section className="open-design-section">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Trade Blotter</div>
              <h3 className="open-design-section-title">Order / execution audit</h3>
            </div>
            <span className="open-design-section-note">{filterCopy}</span>
          </div>

          <div className="workspace-chip-row open-design-filter-row" role="tablist" aria-label="Blotter filters">
            {([
              ["all", "All"],
              ["filled", "Filled"],
              ["pending", "Pending"],
              ["blocked", "Blocked"],
            ] as const).map(([value, label]) => (
              <button
                key={value}
                type="button"
                className={`workspace-chip open-design-filter-button ${
                  filter === value ? "active" : ""
                }`}
                onClick={() => setFilter(value)}
                aria-pressed={filter === value}
              >
                {label}
                <span className="open-design-filter-count">{counts[value]}</span>
              </button>
            ))}
          </div>

          <div className="terminal-table open-design-table open-design-table--blotter">
            <div className="table-row table-head open-design-table-head open-design-table-head--blotter">
              <span>Time</span>
              <span>Symbol</span>
              <span>Direction</span>
              <span>Status</span>
              <span>Source</span>
              <span>Confidence</span>
              <span>Risk flag</span>
            </div>
            {blotterRows.length > 0 ? (
              blotterRows.map((row) => (
                <TableRow
                  key={row.id}
                  cells={[
                    <span key="time">{row.time}</span>,
                    <strong key="symbol">{row.symbol}</strong>,
                    <span
                      key="direction"
                      className={`open-design-chip open-design-chip--${directionTone(row.direction)}`}
                    >
                      {row.direction}
                    </span>,
                    <span
                      key="status"
                      className={`open-design-chip open-design-chip--${statusTone(row.status)}`}
                    >
                      {row.status}
                    </span>,
                    <span key="source">{row.source}</span>,
                    <span key="confidence">{row.confidence}</span>,
                    <span
                      key="risk-flag"
                      className={`open-design-chip open-design-chip--${
                        row.riskFlag === "READ ONLY" ? "safe" : "warn"
                      }`}
                    >
                      {row.riskFlag}
                    </span>,
                  ]}
                />
              ))
            ) : (
              <div className="open-design-empty-state">
                No read-only rows match the selected filter.
              </div>
            )}
          </div>
        </section>
      </div>

      <aside className="open-design-aside">
        <section className="open-design-side-card">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Audit first</div>
              <h3 className="open-design-section-title">Read-only notes</h3>
            </div>
          </div>
          <div className="open-design-side-stack">
            <div className="open-design-side-row">
              <span>Total rows</span>
              <strong>{counts.all}</strong>
            </div>
            <div className="open-design-side-row">
              <span>Filled</span>
              <strong>{counts.filled}</strong>
            </div>
            <div className="open-design-side-row">
              <span>Pending</span>
              <strong>{counts.pending}</strong>
            </div>
            <div className="open-design-side-row">
              <span>Blocked</span>
              <strong>{counts.blocked}</strong>
            </div>
          </div>
          <div className="open-design-note-row">
            <span className="workspace-mini-pill">Filters</span>
            <span>Local only. No order routing.</span>
          </div>
        </section>

        <MellyPetMascot />
      </aside>
    </div>
  );
}

function OpenDesignBacktestTab({ data }: { data: TerminalShellData }) {
  const summary = data.backtest;
  const equityCurve = useMemo(
    () =>
      demoEquityCurve.map((value, index) => ({
        x: index,
        y: value + summary.profit_factor * 0.35,
      })),
    [summary.profit_factor],
  );
  const drawdownCurve = useMemo(
    () =>
      demoDrawdownCurve.map((value, index) => ({
        x: index,
        y: value - summary.max_drawdown_pct * 0.08,
      })),
    [summary.max_drawdown_pct],
  );

  const savedRuns = demoSavedRuns;
  const avgWin = summary.profit_factor * 112.5;
  const sharpe = Math.max(0.8, Math.min(2.2, summary.profit_factor + summary.win_rate / 100));

  return (
    <div className="open-design-layout open-design-layout--backtest">
      <div className="open-design-main">
        <div className="open-design-kpi-grid open-design-kpi-grid--backtest">
          {metricCard({
            label: "Win Rate",
            value: `${formatNumber(summary.win_rate)}%`,
            detail: "Historical simulation only",
          })}
          {metricCard({
            label: "Profit Factor",
            value: formatNumber(summary.profit_factor, 2),
            detail: "Read-only performance ratio",
          })}
          {metricCard({
            label: "Total Trades",
            value: String(summary.sample_size),
            detail: "Sample size",
          })}
          {metricCard({
            label: "Avg Win",
            value: formatCurrency(avgWin),
            detail: "Demo-derived metric",
          })}
          {metricCard({
            label: "Max Drawdown",
            value: `${formatNumber(summary.max_drawdown_pct)}%`,
            detail: "Simulation drawdown",
          })}
          {metricCard({
            label: "Sharpe",
            value: formatNumber(sharpe, 2),
            detail: "Demo-derived metric",
          })}
        </div>

        <div className="open-design-chart-grid">
          <section className="open-design-section">
            <div className="open-design-section-head">
              <div>
                <div className="terminal-eyebrow">Backtest</div>
                <h3 className="open-design-section-title">Equity curve</h3>
              </div>
              <span className="open-design-section-note">Historical simulation only</span>
            </div>
            <div className="open-design-chart-panel">
              <MiniChart points={equityCurve} />
            </div>
          </section>

          <section className="open-design-section">
            <div className="open-design-section-head">
              <div>
                <div className="terminal-eyebrow">Backtest</div>
                <h3 className="open-design-section-title">Drawdown panel</h3>
              </div>
              <span className="open-design-section-note">Advisory only</span>
            </div>
            <div className="open-design-chart-panel">
              <MiniChart points={drawdownCurve} stroke="var(--terminal-red)" />
            </div>
          </section>
        </div>

        <div className="open-design-two-column">
          <section className="open-design-section">
            <div className="open-design-section-head">
              <div>
                <div className="terminal-eyebrow">Configuration</div>
                <h3 className="open-design-section-title">Display-only strategy card</h3>
              </div>
            </div>
            <div className="open-design-config-grid">
              <div className="open-design-config-row">
                <span>Symbol</span>
                <strong>EURUSD</strong>
              </div>
              <div className="open-design-config-row">
                <span>Timeframe</span>
                <strong>M5 / H1</strong>
              </div>
              <div className="open-design-config-row">
                <span>Bars</span>
                <strong>700</strong>
              </div>
              <div className="open-design-config-row">
                <span>Min confidence</span>
                <strong>70%</strong>
              </div>
              <div className="open-design-config-row">
                <span>Max risk</span>
                <strong>&lt;= 1%</strong>
              </div>
              <div className="open-design-config-row">
                <span>Mode</span>
                <strong>READ ONLY</strong>
              </div>
            </div>
          </section>

          <section className="open-design-section">
            <div className="open-design-section-head">
              <div>
                <div className="terminal-eyebrow">Saved runs</div>
                <h3 className="open-design-section-title">Approved historical snapshots</h3>
              </div>
            </div>
            <div className="open-design-saved-run-list">
              {savedRuns.map((run) => (
                <div key={run.id} className="open-design-saved-run">
                  <div className="open-design-saved-run-topline">
                    <strong>{run.label}</strong>
                    <span>{run.outcome}</span>
                  </div>
                  <div className="open-design-saved-run-meta">
                    <span>{run.timestamp}</span>
                    <span>{run.variant}</span>
                    <span>{run.mode}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      <aside className="open-design-aside">
        <section className="open-design-side-card">
          <div className="open-design-section-head">
            <div>
              <div className="terminal-eyebrow">Backtest</div>
              <h3 className="open-design-section-title">Read-only disclaimer</h3>
            </div>
          </div>
          <p className="open-design-disclaimer">
            Backtest results are historical simulation only. Not investment advice.
          </p>
          <div className="open-design-empty-state">
            No live run controls are available in this shell-integrated view.
          </div>
        </section>

        <MellyPetMascot />
      </aside>
    </div>
  );
}

export function OpenDesignTabsPanel({ data }: { data: TerminalShellData }) {
  const [tab, setTab] = useState<TabKey>("positions");

  return (
    <section className="terminal-panel open-design-panel">
      <div className="open-design-topline">
        <div>
          <div className="terminal-eyebrow">Open Design</div>
          <h2 className="open-design-title">Read-only terminal tabs</h2>
          <p className="open-design-subtitle">
            Approved pattern port: Positions B, Trade Blotter A, Backtest Lab C.
          </p>
        </div>
        <div className="open-design-topline-meta">
          <SafetyBadges />
          <div className="workspace-chip-row">
            <span className="workspace-chip">Icon: dark monochrome</span>
            <span className="workspace-chip">Prototype evidence port</span>
          </div>
        </div>
      </div>

      <div className="workspace-safety-banner">
        Read only · dry run · auto trade off · live orders blocked · human review required
      </div>

      <div className="workspace-chip-row open-design-tab-row" role="tablist" aria-label="Open Design tabs">
        {tabMeta.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`workspace-chip open-design-tab-button ${tab === item.key ? "active" : ""}`}
            onClick={() => setTab(item.key)}
            role="tab"
            aria-selected={tab === item.key}
          >
            <span>{item.label}</span>
            <strong>{item.kicker}</strong>
          </button>
        ))}
      </div>

      <div className="open-design-tab-panel" hidden={tab !== "positions"}>
        <OpenDesignPositionsTab data={data} />
      </div>
      <div className="open-design-tab-panel" hidden={tab !== "blotter"}>
        <OpenDesignBlotterTab />
      </div>
      <div className="open-design-tab-panel" hidden={tab !== "backtest"}>
        <OpenDesignBacktestTab data={data} />
      </div>
    </section>
  );
}
