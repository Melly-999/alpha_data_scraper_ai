import { useEffect, useRef, useState } from "react";

import {
  analyzeScreenshot,
  ClientValidationError,
  type ScreenshotAnalysisPreview,
} from "../../lib/screenshotPreviewApi";

/**
 * ScreenshotPreviewCard — MOBILE-AI-007C
 *
 * Display-only mobile card that lets a user pick a chart screenshot and see an
 * analysis-only, paper-only preview from
 * `POST /api/mobile/ai/screenshot/preview`.
 *
 * Safety: analysis only, not financial advice, paper plan only, human review
 * required, no live orders. No buy/sell/order/execute controls, no broker /
 * account fields, no AI provider key input. The image is not stored — it is
 * sent once for analysis and discarded by the backend. If the backend is
 * unavailable, a clearly-labelled offline demo preview is shown instead.
 */

const SAFETY_NOTES = [
  "Analysis only. Not financial advice.",
  "Paper plan only. No live orders.",
  "Human review required.",
] as const;

// Offline/demo fallback shown only when the backend cannot be reached.
const DEMO_PREVIEW: ScreenshotAnalysisPreview = {
  chart_analysis: {
    instrument: "XAUUSD",
    timeframe: "M15",
    trading_style: "Intraday / paper only",
    market_bias: "Neutral-Bullish",
    trend: "Bullish short-term",
    key_levels: ["Support 2,318-2,322", "Resistance 2,341-2,346"],
    momentum: "Improving",
    volatility: "High",
    pattern: "Retest continuation candidate",
    confirmation_checklist: [
      "M15 close confirms",
      "Retest holds",
      "Momentum confirms",
      "Risk <= 1%",
    ],
    analysis_only: true,
    not_financial_advice: true,
    disclaimer: "Analysis only. Not financial advice.",
  },
  paper_game_plan: {
    scenario: "Long only if confirmed",
    entry_zone: "2,322 - 2,326 (example)",
    invalidation: "M15 candle close below 2,316 (example)",
    take_profit_1: "2,341 (example)",
    take_profit_2: "2,352 (example)",
    max_risk_per_trade_pct: 1.0,
    status: "PAPER_ONLY",
    paper_only: true,
    live_orders_blocked: true,
    broker_execution: false,
    requires_human_review: true,
  },
  risk_assessment: {
    safety_score: 82,
    risk_per_trade_pct: 1.0,
    stop_loss_present: true,
    take_profit_present: true,
    overtrading_risk: "Medium",
    news_risk: "High",
    human_review_required: true,
    paper_only: true,
  },
  analysis_only: true,
  paper_only: true,
  live_orders_blocked: true,
  broker_execution: false,
  requires_human_review: true,
  stored: false,
  provider_used: false,
  disclaimer: "Analysis only. Not financial advice.",
};

type Status = "idle" | "loading" | "done" | "demo" | "error";

export function ScreenshotPreviewCard() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [thumbUrl, setThumbUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<ScreenshotAnalysisPreview | null>(null);

  // Revoke the ephemeral object URL when it changes / on unmount.
  useEffect(() => {
    return () => {
      if (thumbUrl) {
        URL.revokeObjectURL(thumbUrl);
      }
    };
  }, [thumbUrl]);

  function reset(): void {
    setError(null);
    setPreview(null);
    setStatus("idle");
  }

  async function onPick(file: File): Promise<void> {
    reset();
    setFileName(file.name);
    setThumbUrl((prev) => {
      if (prev) {
        URL.revokeObjectURL(prev);
      }
      return URL.createObjectURL(file);
    });

    setStatus("loading");
    try {
      const result = await analyzeScreenshot(file);
      setPreview(result);
      setStatus("done");
    } catch (err) {
      if (err instanceof ClientValidationError) {
        setError(err.message);
        setStatus("error");
        return;
      }
      // Network / backend unavailable → clearly-labelled offline demo preview.
      setError(
        err instanceof Error ? err.message : "Could not reach the analysis service.",
      );
      setPreview(DEMO_PREVIEW);
      setStatus("demo");
    }
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>): void {
    const file = e.target.files?.[0];
    if (file) {
      void onPick(file);
    }
  }

  return (
    <section
      aria-label="AI screenshot review"
      className="mobile-card mobile-card--accent"
    >
      <div className="mobile-card-head">
        <h2 className="mobile-card-title">AI Screenshot Review</h2>
        <span className="mobile-pill mobile-pill--amber">Paper only</span>
      </div>

      <p className="mobile-card-sub">
        Upload a chart screenshot to see a paper-only analysis preview. PNG,
        JPEG, or WebP, up to 5 MB. The image is not stored.
      </p>

      <div className="mobile-upload-row">
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          className="mobile-upload-input"
          aria-label="Choose a chart screenshot to analyze"
          onChange={onInputChange}
        />
      </div>

      {thumbUrl && (
        <div className="mobile-upload-preview">
          <img
            src={thumbUrl}
            alt={fileName ? `Selected screenshot: ${fileName}` : "Selected screenshot"}
            className="mobile-upload-thumb"
          />
          <span className="mobile-upload-filename">{fileName}</span>
        </div>
      )}

      {status === "loading" && (
        <p className="mobile-card-body" role="status">
          Analyzing screenshot…
        </p>
      )}

      {status === "error" && error && (
        <p className="mobile-upload-error" role="alert">
          {error}
        </p>
      )}

      {status === "demo" && (
        <p className="mobile-upload-notice" role="status">
          Analysis service unavailable — showing an offline demo preview.
        </p>
      )}

      {preview && (status === "done" || status === "demo") && (
        <ScreenshotPreviewResult preview={preview} />
      )}

      <ul className="mobile-upload-safety">
        {SAFETY_NOTES.map((note) => (
          <li key={note} className="mobile-upload-safety-item">
            {note}
          </li>
        ))}
      </ul>
    </section>
  );
}

function ScreenshotPreviewResult({
  preview,
}: {
  preview: ScreenshotAnalysisPreview;
}) {
  const { chart_analysis: chart, paper_game_plan: plan, risk_assessment: risk } =
    preview;
  return (
    <div className="mobile-upload-result" aria-label="Analysis preview">
      <dl className="mobile-fact-list">
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Instrument</dt>
          <dd className="mobile-fact-value">
            {chart.instrument} · {chart.timeframe}
          </dd>
        </div>
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Market bias</dt>
          <dd className="mobile-fact-value">{chart.market_bias}</dd>
        </div>
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Pattern</dt>
          <dd className="mobile-fact-value">{chart.pattern}</dd>
        </div>
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Paper plan</dt>
          <dd className="mobile-fact-value">{plan.scenario}</dd>
        </div>
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Max simulated risk</dt>
          <dd className="mobile-fact-value">
            {plan.max_risk_per_trade_pct}% · {plan.status}
          </dd>
        </div>
        <div className="mobile-fact-row">
          <dt className="mobile-fact-label">Safety score</dt>
          <dd className="mobile-fact-value">{risk.safety_score}/100</dd>
        </div>
      </dl>
      <div className="mobile-chip-row" aria-label="Safety posture">
        <span className="mobile-static-chip mobile-static-chip--sm" aria-disabled="true">
          No live orders
        </span>
        <span className="mobile-static-chip mobile-static-chip--sm" aria-disabled="true">
          Human review required
        </span>
        <span className="mobile-static-chip mobile-static-chip--sm" aria-disabled="true">
          Not stored
        </span>
      </div>
      <p className="mobile-disclaimer">{preview.disclaimer}</p>
    </div>
  );
}
