import { useEffect, useState } from "react";

import type { PortfolioRiskSummaryResponse } from "../../lib/terminalApi";
import { getPortfolioRiskSummary } from "../../lib/terminalApi";

const POSTURE_LABEL_DISPLAY: Record<string, string> = {
  safe_fallback: "SAFE FALLBACK",
  read_only: "READ ONLY",
  risk_blocked: "RISK BLOCKED",
  dry_run_only: "DRY RUN ONLY",
};

export function PortfolioRiskSummaryCard() {
  const [data, setData] = useState<PortfolioRiskSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getPortfolioRiskSummary().then((response) => {
      if (!cancelled) {
        setData(response);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <section
        className="portfolio-risk-card portfolio-risk-card--loading"
        aria-label="Portfolio risk summary loading"
        aria-busy="true"
      >
        <div className="portfolio-risk-card__header">
          <span>Portfolio Risk</span>
          <span>loading…</span>
        </div>
        <p className="portfolio-risk-card__loading-text">
          Fetching risk summary…
        </p>
      </section>
    );
  }

  if (!data) {
    return null;
  }

  const { exposure, limits, posture, notes, status } = data;
  const isDegraded =
    status === "degraded" || posture.label === "safe_fallback";
  const firstNote = notes[0] ?? "Read-only portfolio risk summary.";

  const riskUsedPct = Math.min(
    limits.risk_used_pct,
    limits.max_portfolio_risk_pct,
  );
  const riskBarWidth =
    limits.max_portfolio_risk_pct > 0
      ? (riskUsedPct / limits.max_portfolio_risk_pct) * 100
      : 0;

  return (
    <section
      className={`portfolio-risk-card${isDegraded ? " portfolio-risk-card--degraded" : ""}`}
      aria-label="Portfolio risk summary — advisory only"
    >
      <div className="portfolio-risk-card__header">
        <span>Portfolio Risk Summary</span>
        <span>GET-only · advisory only</span>
      </div>

      {/* Safety chips */}
      <div
        className="portfolio-risk-card__chips"
        aria-label="Portfolio risk safety status"
      >
        <span className="portfolio-risk-chip portfolio-risk-chip--safe">
          READ ONLY
        </span>
        <span className="portfolio-risk-chip portfolio-risk-chip--safe">
          DRY RUN
        </span>
        <span className="portfolio-risk-chip portfolio-risk-chip--warn">
          RISK BLOCKED
        </span>
        <span className="portfolio-risk-chip portfolio-risk-chip--warn">
          HUMAN REVIEW
        </span>
        <span className="portfolio-risk-chip portfolio-risk-chip--info">
          DRY RUN ONLY
        </span>
      </div>

      {/* Metric grid */}
      <div
        className="portfolio-risk-card__grid"
        aria-label="Portfolio risk metrics"
      >
        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Positions</span>
          <strong className="portfolio-risk-card__value">
            {exposure.open_positions} / {exposure.total_positions}
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Gross Exposure</span>
          <strong className="portfolio-risk-card__value">
            {exposure.gross_exposure_pct.toFixed(1)}%
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Cash Buffer</span>
          <strong className="portfolio-risk-card__value">
            {exposure.cash_buffer_pct.toFixed(1)}%
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Max Risk / Trade</span>
          <strong className="portfolio-risk-card__value">
            {limits.max_risk_per_trade_pct.toFixed(1)}%
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Risk Used</span>
          <strong className="portfolio-risk-card__value">
            {limits.risk_used_pct.toFixed(2)}%
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Risk Remaining</span>
          <strong className="portfolio-risk-card__value">
            {limits.remaining_risk_capacity_pct.toFixed(2)}%
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Posture</span>
          <strong className="portfolio-risk-card__value portfolio-risk-card__value--posture">
            {POSTURE_LABEL_DISPLAY[posture.label] ??
              posture.label.toUpperCase()}
          </strong>
        </div>

        <div className="portfolio-risk-card__metric">
          <span className="portfolio-risk-card__label">Execution Mode</span>
          <strong className="portfolio-risk-card__value portfolio-risk-card__value--dry-run">
            DRY RUN ONLY
          </strong>
        </div>
      </div>

      {/* Risk capacity bar */}
      <div
        className="portfolio-risk-card__bar-wrap"
        aria-label={`Risk used ${limits.risk_used_pct.toFixed(2)}% of ${limits.max_portfolio_risk_pct.toFixed(1)}% max`}
      >
        <div className="portfolio-risk-card__bar-label-row">
          <span className="portfolio-risk-card__label">
            Portfolio Risk Capacity
          </span>
          <span className="portfolio-risk-card__bar-value">
            {limits.risk_used_pct.toFixed(2)}% / {limits.max_portfolio_risk_pct.toFixed(1)}%
          </span>
        </div>
        <div
          className="portfolio-risk-card__bar"
          role="meter"
          aria-valuenow={riskUsedPct}
          aria-valuemin={0}
          aria-valuemax={limits.max_portfolio_risk_pct}
        >
          <span
            className="portfolio-risk-card__bar-fill"
            style={{ width: `${Math.min(riskBarWidth, 100)}%` }}
          />
        </div>
      </div>

      {/* Advisory note */}
      <p className="portfolio-risk-card__note" aria-label="Advisory note">
        {firstNote}
      </p>
    </section>
  );
}
