import type {
  BacktestSummary,
  IBKRStatus,
  MarketItem,
  MT5Status,
  NewsItem,
  PositionItem,
  RiskPolicy,
  RiskStatus,
  SignalItem,
  TerminalEvent,
  TerminalSummary,
} from "../../lib/terminalApi";
import { AISignalFeedPreview } from "./AISignalFeedPreview";
import { AuditEventsPreview } from "./AuditEventsPreview";
import { IBKRBrokerCard } from "./IBKRBrokerCard";
import { LeftSidebar } from "./LeftSidebar";
import { LoadingScreen } from "./LoadingScreen";
import { MarketOverviewGrid } from "./MarketOverviewGrid";
import { NewsRail } from "./NewsRail";
import { RiskGuardrailsCard } from "./RiskGuardrailsCard";
import { TopTickerBar } from "./TopTickerBar";

export type TerminalShellData = {
  summary: TerminalSummary;
  markets: MarketItem[];
  watchlist: MarketItem[];
  signals: SignalItem[];
  riskStatus: RiskStatus;
  riskPolicy: RiskPolicy;
  backtest: BacktestSummary;
  news: NewsItem[];
  positions: PositionItem[];
  mt5: MT5Status;
  events: TerminalEvent[];
  broker: IBKRStatus;
};

type TerminalShellProps = {
  data: TerminalShellData;
  loading: boolean;
  pathname: string;
};

const agents = [
  ["Risk Sentinel", "Monitors max risk <= 1% and blocked live orders."],
  ["Signal Analyst", "Explains dry-run signal thesis and evidence."],
  ["Market Regime", "Classifies trend, range, volatility, and session context."],
  ["News Filter", "Summarizes read-only macro and flow headlines."],
  ["Broker Watch", "Observes disconnected or paper read-only broker state."],
  ["Audit Scribe", "Tracks safety events and degraded services."],
  ["Portfolio Guard", "Reviews exposure without creating orders."],
  ["Validation Runner", "Keeps local checks visible before PRs."],
  ["Operator Copilot", "Produces no-trade and watch-only notes."],
];

function viewFromPath(pathname: string) {
  if (pathname.includes("markets")) return "markets";
  if (pathname.includes("watchlist")) return "watchlist";
  if (pathname.includes("workspace")) return "workspace";
  if (pathname.includes("signals")) return "signals";
  if (pathname.includes("risk")) return "risk";
  if (pathname.includes("brokers")) return "brokers";
  if (pathname.includes("portfolio") || pathname.includes("positions")) return "portfolio";
  if (pathname.includes("audit") || pathname.includes("reports")) return "audit";
  if (pathname.includes("settings")) return "settings";
  return "dashboard";
}

function CommandCenter({
  data,
  openPositions,
}: {
  data: TerminalShellData;
  openPositions: PositionItem[];
}) {
  return (
    <section id="command" className="command-center">
      <div>
        <p className="terminal-eyebrow">Command center</p>
        <h1>MellyTrade V1 Terminal</h1>
        <p>
          Premium read-only market workstation with degraded-first broker
          adapters and blocked live orders.
        </p>
      </div>
      <div className="command-metrics">
        <div>
          <span>Backend</span>
          <strong>{data.summary.backend}</strong>
        </div>
        <div>
          <span>MT5</span>
          <strong>{data.mt5.connected ? "connected" : data.mt5.mode}</strong>
        </div>
        <div>
          <span>Positions</span>
          <strong>{openPositions.length}</strong>
        </div>
        <div>
          <span>Backtest samples</span>
          <strong>{data.backtest.sample_size}</strong>
        </div>
      </div>
    </section>
  );
}

function WatchlistPanel({ markets }: { markets: MarketItem[] }) {
  return (
    <section className="terminal-panel">
      <div className="panel-header">
        <span>Watchlist</span>
        <span>read-only</span>
      </div>
      <div className="terminal-table terminal-table-wide">
        <div className="table-row table-head">
          <span>Symbol</span>
          <span>Price</span>
          <span>Change</span>
          <span>Signal</span>
        </div>
        {markets.map((market) => (
          <div key={market.symbol} className="table-row">
            <span>{market.symbol}</span>
            <span>{market.price.toFixed(market.price > 10 ? 2 : 4)}</span>
            <span className={market.change_pct >= 0 ? "value-positive" : "value-negative"}>
              {market.change_pct >= 0 ? "+" : ""}
              {market.change_pct.toFixed(2)}%
            </span>
            <span>{market.signal} / {market.confidence}%</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function AIWorkspacePanel() {
  return (
    <section className="terminal-panel">
      <div className="panel-header">
        <span>AI Workspace</span>
        <span>9 read-only agents</span>
      </div>
      <div className="agent-grid">
        {agents.map(([name, detail]) => (
          <article key={name} className="agent-card">
            <strong>{name}</strong>
            <p>{detail}</p>
            <span>NO EXECUTION TOOLS</span>
          </article>
        ))}
      </div>
    </section>
  );
}

function SignalThesisPanel({ signals }: { signals: SignalItem[] }) {
  const lead = signals[0];

  return (
    <section className="terminal-panel">
      <div className="panel-header">
        <span>Thesis / Evidence</span>
        <span>display-only</span>
      </div>
      <div className="thesis-grid">
        <div>
          <p className="terminal-eyebrow">Lead thesis</p>
          <h2>{lead ? `${lead.symbol} ${lead.direction}` : "No active thesis"}</h2>
          <p>{lead?.reason ?? "Fallback state: signal feed is unavailable."}</p>
        </div>
        <div className="evidence-stack">
          <span>Dry-run only</span>
          <span>Risk gate visible</span>
          <span>Broker execution denied</span>
          <span>Human review required</span>
        </div>
      </div>
    </section>
  );
}

function PortfolioPanel({ positions }: { positions: PositionItem[] }) {
  return (
    <section className="terminal-panel">
      <div className="panel-header">
        <span>Portfolio</span>
        <span>paper/read-only snapshot</span>
      </div>
      <div className="terminal-table terminal-table-wide">
        <div className="table-row table-head">
          <span>Symbol</span>
          <span>Side</span>
          <span>Qty</span>
          <span>PnL</span>
        </div>
        {positions.map((position) => (
          <div key={position.id} className="table-row">
            <span>{position.symbol}</span>
            <span>{position.side}</span>
            <span>{position.quantity}</span>
            <span>{position.pnl.toFixed(2)} {position.currency ?? ""}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function SettingsPanel() {
  return (
    <section className="terminal-panel">
      <div className="panel-header">
        <span>Settings</span>
        <span>locked safety posture</span>
      </div>
      <div className="guardrail-list">
        {[
          ["autotrade", "false"],
          ["dry_run", "true"],
          ["read_only", "true"],
          ["live_orders_blocked", "true"],
          ["max risk", "<= 1%"],
        ].map(([label, value]) => (
          <div key={label} className="guardrail-row">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

export function TerminalShell({ data, loading, pathname }: TerminalShellProps) {
  const openPositions = data.positions.filter((position) => position.side !== "flat");
  const view = viewFromPath(pathname);
  const watchlist = data.watchlist.length > 0 ? data.watchlist : data.markets;

  return (
    <div className="terminal-root">
      <TopTickerBar markets={data.markets} />
      <div className="terminal-body">
        <LeftSidebar />
        <main className="terminal-main">
          {loading ? <LoadingScreen /> : null}
          {view === "dashboard" ? (
            <>
              <CommandCenter data={data} openPositions={openPositions} />
              <MarketOverviewGrid markets={data.markets} />
              <section className="terminal-columns">
                <RiskGuardrailsCard policy={data.riskPolicy} status={data.riskStatus} />
                <IBKRBrokerCard broker={data.broker} />
              </section>
              <section className="terminal-columns">
                <AISignalFeedPreview signals={data.signals} />
                <AuditEventsPreview events={data.events} />
              </section>
            </>
          ) : null}

          {view === "markets" ? <MarketOverviewGrid markets={data.markets} /> : null}
          {view === "watchlist" ? <WatchlistPanel markets={watchlist} /> : null}
          {view === "workspace" ? <AIWorkspacePanel /> : null}
          {view === "signals" ? (
            <>
              <SignalThesisPanel signals={data.signals} />
              <AISignalFeedPreview signals={data.signals} />
            </>
          ) : null}
          {view === "risk" ? (
            <RiskGuardrailsCard policy={data.riskPolicy} status={data.riskStatus} />
          ) : null}
          {view === "brokers" ? <IBKRBrokerCard broker={data.broker} /> : null}
          {view === "portfolio" ? <PortfolioPanel positions={data.positions} /> : null}
          {view === "audit" ? <AuditEventsPreview events={data.events} /> : null}
          {view === "settings" ? <SettingsPanel /> : null}
        </main>
        <NewsRail news={data.news} />
      </div>
      <footer className="terminal-statusbar">
        <span>READ ONLY ENABLED</span>
        <span>DRY RUN ACTIVE</span>
        <span>AUTO TRADE OFF</span>
        <span>LIVE ORDERS BLOCKED</span>
        <span>IBKR PAPER READ-ONLY FIRST</span>
      </footer>
    </div>
  );
}
