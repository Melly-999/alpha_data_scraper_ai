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
};

export function TerminalShell({ data, loading }: TerminalShellProps) {
  const openPositions = data.positions.filter((position) => position.side !== "flat");

  return (
    <div className="terminal-root">
      <TopTickerBar markets={data.markets} />
      <div className="terminal-body">
        <LeftSidebar />
        <main className="terminal-main">
          {loading ? <LoadingScreen /> : null}
          <section id="command" className="command-center">
            <div>
              <p className="terminal-eyebrow">Command center</p>
              <h1>MellyTrade V1 Terminal</h1>
              <p>
                Read-only market workstation with degraded-first broker adapters
                and blocked live orders.
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

          <MarketOverviewGrid markets={data.markets} />

          <section className="terminal-columns">
            <RiskGuardrailsCard policy={data.riskPolicy} status={data.riskStatus} />
            <IBKRBrokerCard broker={data.broker} />
          </section>

          <section className="terminal-columns">
            <AISignalFeedPreview signals={data.signals} />
            <AuditEventsPreview events={data.events} />
          </section>
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
