import { Link } from "react-router-dom";

import { AgentStatusBar } from "../terminal/AgentStatusBar";
import { AISignalFeedPreview } from "../terminal/AISignalFeedPreview";
import { AuditEventsPreview } from "../terminal/AuditEventsPreview";
import { IBKRBrokerCard } from "../terminal/IBKRBrokerCard";
import { MarketOverviewGrid } from "../terminal/MarketOverviewGrid";
import { RiskGuardrailsCard } from "../terminal/RiskGuardrailsCard";
import {
  demoAuditEvents,
  demoPortfolioRiskSummary,
  demoTerminalShellData,
} from "../../fixtures/publicShowcaseFixtures";

/**
 * ProductPreviewGrid — PUBLIC-SITE-001
 *
 * Composes existing, prop-driven terminal components over the static demo
 * fixture for the public "product preview" section. Deliberately does NOT
 * embed `TerminalShell`, `AIWorkspacePanel`, `SupabaseStatusCard`,
 * `AlpacaPaperReadOnlyCard`, or the paper-sandbox preview panels — those
 * components perform their own live GET fetches on mount, which would send
 * live backend requests on behalf of anonymous public visitors. Per the
 * design pack's fallback rule ("if an internal component can't render
 * safely on sample data without modification, wrap it"), the terminal,
 * portfolio, and paper-sandbox cards below are lightweight static wrappers;
 * only `AuditEventsPreview` (and the market/risk/broker/agent components,
 * all pure and props-only) are reused unmodified.
 */
export function ProductPreviewGrid() {
  const data = demoTerminalShellData;
  const { exposure, limits, posture } = demoPortfolioRiskSummary;

  return (
    <section id="product-previews" className="public-section">
      <p className="public-section__eyebrow">Product Previews</p>
      <h2>Everything except an order button.</h2>
      <p className="public-section__lead">
        Every panel below renders illustrative, static DEMO data — never a
        live feed. Nothing here calls a live account.
      </p>

      <div className="public-preview-grid">
        {/* Terminal preview — wide card, real prop-driven components */}
        <article className="public-preview-card public-preview-card--wide">
          <div className="public-preview-card__head">
            <h3>Terminal preview</h3>
            <span className="public-chip public-chip--safe">DEMO DATA</span>
          </div>
          <div className="public-terminal-frame">
            <div className="public-terminal-frame__scale">
              <MarketOverviewGrid markets={data.markets} />
              <section className="terminal-columns">
                <RiskGuardrailsCard policy={data.riskPolicy} status={data.riskStatus} />
                <IBKRBrokerCard broker={data.broker} />
              </section>
              <AISignalFeedPreview signals={data.signals} />
              <AgentStatusBar
                summary={data.summary}
                broker={data.broker}
                agentCount={9}
                healthyAgents={9}
              />
            </div>
            <div className="public-terminal-frame__watermark">
              DEMO DATA · display-only · no execution controls exist in this interface
            </div>
          </div>
          <p className="public-preview-card__body">
            A production-grade terminal with everything except an order
            button. Market intelligence, AI advisory, agent status — rendered
            on demo data, labeled as such.
          </p>
          <Link to="/terminal" className="public-preview-card__link">
            Open the terminal preview →
          </Link>
        </article>

        {/* Portfolio dashboard preview — static wrapper, same visual language as PortfolioRiskSummaryCard */}
        <article className="public-preview-card" aria-label="Portfolio risk summary — demo data">
          <div className="public-preview-card__head">
            <h3>Portfolio dashboard preview</h3>
            <span className="public-chip public-chip--safe">SIMULATED</span>
          </div>
          <div className="public-preview-card__body">
            <div className="public-chip-row">
              <span className="public-chip public-chip--safe">READ ONLY</span>
              <span className="public-chip public-chip--safe">DRY RUN</span>
              <span className="public-chip">RISK BLOCKED</span>
            </div>
            <div className="public-metric-grid">
              <div className="public-metric">
                <span className="public-metric__label">Gross exposure</span>
                <span className="public-metric__value">{exposure.gross_exposure_pct.toFixed(1)}%</span>
              </div>
              <div className="public-metric">
                <span className="public-metric__label">Cash buffer</span>
                <span className="public-metric__value">{exposure.cash_buffer_pct.toFixed(1)}%</span>
              </div>
              <div className="public-metric">
                <span className="public-metric__label">Max risk / trade</span>
                <span className="public-metric__value">{limits.max_risk_per_trade_pct.toFixed(1)}%</span>
              </div>
              <div className="public-metric">
                <span className="public-metric__label">Posture</span>
                <span className="public-metric__value">{posture.label.replace(/_/g, " ")}</span>
              </div>
            </div>
            <p>
              Risk first, always. Exposure, drawdown guards, and allocation
              views on illustrative data. Performance is deliberately
              understated — because it is simulated.
            </p>
          </div>
          <Link to="/watchlist" className="public-preview-card__link">
            Open the watchlist →
          </Link>
        </article>

        {/* Paper sandbox preview — static card, no live component reuse (avoids anonymous live fetch) */}
        <article className="public-preview-card" aria-label="Paper sandbox preview — demo data">
          <div className="public-preview-card__head">
            <h3>Paper sandbox preview</h3>
            <span className="public-chip public-chip--safe">PAPER</span>
          </div>
          <div className="public-preview-card__body">
            <div className="public-chip-row">
              <span className="public-chip public-chip--safe">PAPER ONLY</span>
              <span className="public-chip public-chip--safe">NO LIVE PATH</span>
            </div>
            <p>
              Every position here is paper. The sandbox has no path to a
              live account — not hidden, not gated. Absent.
            </p>
          </div>
          <Link to="/terminal/paper-run-preview" className="public-preview-card__link">
            Open the paper sandbox preview →
          </Link>
        </article>

        {/* Audit / event rail — real component reuse, static event fixture */}
        <article className="public-preview-card" aria-label="Audit event rail — demo data">
          <div className="public-preview-card__head">
            <h3>Audit / event rail</h3>
            <span className="public-chip public-chip--safe">DEMO</span>
          </div>
          <div className="public-preview-card__body">
            <p>
              Every analysis, validation, and safety check leaves a record.
              The platform argues from evidence, and so does this site.
            </p>
            <div className="public-audit-mini-list">
              <AuditEventsPreview events={demoAuditEvents} lastUpdatedAt={new Date()} />
            </div>
          </div>
          <Link to="/terminal" className="public-preview-card__link">
            Open the full audit trail →
          </Link>
        </article>
      </div>
    </section>
  );
}
