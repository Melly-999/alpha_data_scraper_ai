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
import type { SignalScannerBatch } from "../../lib/scannerPreviewApi";
import { AIWorkspacePanel } from "./AIWorkspacePanel";
import { AISignalFeedPreview } from "./AISignalFeedPreview";
import { AuditEventsPreview } from "./AuditEventsPreview";
import { DegradedServicesBanner } from "./DegradedServicesBanner";
import { IBKRBrokerCard } from "./IBKRBrokerCard";
import { LeftSidebar } from "./LeftSidebar";
import { LoadingScreen } from "./LoadingScreen";
import { MarketOverviewGrid } from "./MarketOverviewGrid";
import { PaperRunPreviewPanel } from "./PaperRunPreviewPanel";
import { NewsRail } from "./NewsRail";
import { RiskGuardrailsCard } from "./RiskGuardrailsCard";
import { SupabaseStatusCard } from "./SupabaseStatusCard";
import { AgentStatusBar } from "./AgentStatusBar";
import { TopTickerBar } from "./TopTickerBar";

export type TerminalShellData = {
  summary: TerminalSummary;
  markets: MarketItem[];
  watchlist: MarketItem[];
  signals: SignalItem[];
  scannerPreview: SignalScannerBatch;
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
  /** SUPA-009: timestamp of most recent successful audit events poll. */
  eventsLastUpdatedAt?: Date | null;
};

function viewFromPath(pathname: string) {
  if (pathname.includes("markets")) return "markets";
  if (pathname.includes("watchlist")) return "watchlist";
  if (pathname.includes("paper-run-preview")) return "paper-preview";
  if (pathname.includes("workspace")) return "workspace";
  if (pathname.includes("signals")) return "signals";
  if (pathname.includes("risk")) return "risk";
  if (pathname.includes("brokers")) return "brokers";
  if (pathname.includes("portfolio") || pathname.includes("positions")) return "portfolio";
  if (pathname.includes("audit") || pathname.includes("reports")) return "audit";
  if (pathname.includes("settings")) return "settings";
  return "dashboard";
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

export function TerminalShell({
  data,
  loading,
  pathname,
  eventsLastUpdatedAt = null,
}: TerminalShellProps) {
  const view = viewFromPath(pathname);
  const watchlist = data.watchlist.length > 0 ? data.watchlist : data.markets;
  const healthyAgents = 9;

  return (
    <div className="terminal-root">
      <TopTickerBar markets={data.markets} />
      <div className="terminal-body">
        <LeftSidebar />
        <main className="terminal-main" aria-label={`Terminal view: ${view}`}>
          <DegradedServicesBanner
            summary={data.summary}
            mt5={data.mt5}
            broker={data.broker}
          />
          {loading ? <LoadingScreen /> : null}
          {view === "dashboard" ? (
            <>
              <AIWorkspacePanel data={data} />
              <MarketOverviewGrid markets={data.markets} />
              <section className="terminal-columns">
                <RiskGuardrailsCard policy={data.riskPolicy} status={data.riskStatus} />
                <IBKRBrokerCard broker={data.broker} />
                <SupabaseStatusCard />
              </section>
              <section className="terminal-columns">
                <AISignalFeedPreview signals={data.signals} />
                <AuditEventsPreview
                  events={data.events}
                  lastUpdatedAt={eventsLastUpdatedAt}
                />
              </section>
            </>
          ) : null}

          {view === "markets" ? <MarketOverviewGrid markets={data.markets} /> : null}
          {view === "watchlist" ? <WatchlistPanel markets={watchlist} /> : null}
          {view === "workspace" ? <AIWorkspacePanel data={data} /> : null}
          {view === "paper-preview" ? <PaperRunPreviewPanel /> : null}
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
          {view === "audit" ? (
            <AuditEventsPreview
              events={data.events}
              lastUpdatedAt={eventsLastUpdatedAt}
            />
          ) : null}
          {view === "settings" ? <SettingsPanel /> : null}
        </main>
        <NewsRail news={data.news} />
      </div>
      <AgentStatusBar
        summary={data.summary}
        broker={data.broker}
        agentCount={9}
        healthyAgents={healthyAgents}
      />
    </div>
  );
}
