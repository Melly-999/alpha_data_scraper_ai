import { useEffect, useState } from "react";

import type { SignalQualitySummaryResponse } from "../../lib/terminalApi";
import { getSignalQualitySummary } from "../../lib/terminalApi";

const LABEL_DISPLAY: Record<string, string> = {
  safe_fallback: "SAFE FALLBACK",
  low: "LOW",
  moderate: "MODERATE",
  high: "HIGH",
};

const BAND_DISPLAY: Record<string, string> = {
  low: "LOW",
  medium: "MEDIUM",
  high: "HIGH",
};

const FRESHNESS_DISPLAY: Record<string, string> = {
  fallback: "FALLBACK",
  live: "LIVE",
  stale: "STALE",
};

export function SignalQualitySummaryCard() {
  const [data, setData] = useState<SignalQualitySummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getSignalQualitySummary().then((response) => {
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
        className="signal-quality-card signal-quality-card--loading"
        aria-label="Signal quality summary loading"
        aria-busy="true"
      >
        <div className="signal-quality-card__header">
          <span>Signal Quality</span>
          <span>loading…</span>
        </div>
        <p className="signal-quality-card__loading-text">
          Fetching quality summary…
        </p>
      </section>
    );
  }

  if (!data) {
    return null;
  }

  const { summary, quality, notes, status } = data;
  const isDegraded = status === "degraded" || quality.label === "safe_fallback";
  const firstNote = notes[0] ?? "Read-only advisory signal quality summary.";

  return (
    <section
      className={`signal-quality-card${isDegraded ? " signal-quality-card--degraded" : ""}`}
      aria-label="Signal quality summary — advisory only"
    >
      <div className="signal-quality-card__header">
        <span>Signal Quality Summary</span>
        <span>GET-only · advisory only</span>
      </div>

      {/* Safety chips */}
      <div
        className="signal-quality-card__chips"
        aria-label="Signal quality safety status"
      >
        <span className="signal-quality-chip signal-quality-chip--safe">
          READ ONLY
        </span>
        <span className="signal-quality-chip signal-quality-chip--safe">
          DRY RUN
        </span>
        <span className="signal-quality-chip signal-quality-chip--warn">
          RISK BLOCKED
        </span>
        <span className="signal-quality-chip signal-quality-chip--warn">
          HUMAN REVIEW
        </span>
        <span className="signal-quality-chip signal-quality-chip--info">
          DRY RUN ONLY
        </span>
      </div>

      {/* Metric grid */}
      <div
        className="signal-quality-card__grid"
        aria-label="Signal quality metrics"
      >
        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Total Signals</span>
          <strong className="signal-quality-card__value">
            {summary.total_signals}
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Avg Confidence</span>
          <strong className="signal-quality-card__value">
            {summary.average_confidence.toFixed(1)}%
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Quality Label</span>
          <strong
            className={`signal-quality-card__value signal-quality-card__value--label signal-quality-label--${quality.label}`}
          >
            {LABEL_DISPLAY[quality.label] ?? quality.label.toUpperCase()}
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Confidence Band</span>
          <strong className="signal-quality-card__value">
            {BAND_DISPLAY[quality.confidence_band] ??
              quality.confidence_band.toUpperCase()}
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Freshness</span>
          <strong className="signal-quality-card__value">
            {FRESHNESS_DISPLAY[quality.freshness] ??
              quality.freshness.toUpperCase()}
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Risk Posture</span>
          <strong className="signal-quality-card__value signal-quality-card__value--blocked">
            BLOCKED
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">High Confidence</span>
          <strong className="signal-quality-card__value">
            {summary.high_confidence_count} / {summary.total_signals}
          </strong>
        </div>

        <div className="signal-quality-card__metric">
          <span className="signal-quality-card__label">Execution Mode</span>
          <strong className="signal-quality-card__value signal-quality-card__value--dry-run">
            DRY RUN ONLY
          </strong>
        </div>
      </div>

      {/* Confidence score bar */}
      <div
        className="signal-quality-card__score-bar-wrap"
        aria-label={`Quality score ${quality.score.toFixed(1)} out of 100`}
      >
        <div className="signal-quality-card__score-label-row">
          <span className="signal-quality-card__label">Quality Score</span>
          <span className="signal-quality-card__score-value">
            {quality.score.toFixed(1)}
          </span>
        </div>
        <div
          className="signal-quality-card__score-bar"
          role="meter"
          aria-valuenow={quality.score}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <span
            className="signal-quality-card__score-fill"
            style={{ width: `${Math.min(quality.score, 100)}%` }}
          />
        </div>
      </div>

      {/* Advisory note */}
      <p className="signal-quality-card__note" aria-label="Advisory note">
        {firstNote}
      </p>
    </section>
  );
}
