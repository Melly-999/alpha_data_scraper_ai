import { Link } from "react-router-dom";

import { MellyPetMascot } from "../components/branding/MellyPetMascot";
import { ScreenshotPreviewCard } from "../components/mobile/ScreenshotPreviewCard";
import "../components/terminal/terminal.css";
import "./mobile-app.css";

/**
 * MobileAppPage — MOBILE-AI-003
 *
 * Mobile AI chart-review mock for MellyTrade ("Mobile Command Center").
 * Frontend-only, display-only / mock surface. No API mutations, no backend
 * calls, no screenshot upload, no AI provider keys, no trading controls,
 * no POST/PUT/PATCH/DELETE.
 *
 * Every "action" label below is a static / disabled placeholder — not a real
 * trading action. Monte Carlo is referenced only as an existing static
 * simulation summary snapshot (no new engine, no backend call).
 *
 * Safety posture: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED ·
 * HUMAN REVIEW REQUIRED. Paper / simulation only.
 */

const SAFETY_BADGES = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "HUMAN REVIEW REQUIRED",
] as const;

// ── Section 2: mobile action grid (static cards, no real actions) ──────────
type ActionCard = {
  title: string;
  hint: string;
};

const ACTION_CARDS: ActionCard[] = [
  { title: "Analyze Chart", hint: "Mock AI chart review" },
  { title: "Watchlist", hint: "Tracked instruments" },
  { title: "Paper Game Plan", hint: "Simulation plan only" },
  { title: "Journal", hint: "Setup history" },
];

// ── Section 3: AI Chart Review mock ────────────────────────────────────────
const CHART_REVIEW_FACTS: { label: string; value: string }[] = [
  { label: "Instrument", value: "XAUUSD" },
  { label: "Timeframe", value: "M15" },
  { label: "Trading style", value: "Intraday / paper only" },
  { label: "Market bias", value: "Neutral-Bullish" },
  { label: "Trend", value: "Bullish short-term" },
  { label: "Key levels", value: "Support 2,318–2,322 · Resistance 2,341–2,346" },
  { label: "Momentum", value: "Improving" },
  { label: "Volatility", value: "High" },
  { label: "Pattern", value: "Retest continuation candidate" },
];

const CONFIRMATION_CHECKLIST = [
  "M15 close confirms",
  "Retest holds",
  "Momentum confirms",
  "Risk ≤ 1%",
] as const;

// ── Section 4: Safety Score ────────────────────────────────────────────────
type SafetyRow = { label: string; value: string; tone: "ok" | "warn" | "info" };

const SAFETY_ROWS: SafetyRow[] = [
  { label: "Risk per trade", value: "OK · max 1%", tone: "ok" },
  { label: "Stop loss", value: "Present in paper plan", tone: "ok" },
  { label: "Take profit", value: "Present in paper plan", tone: "ok" },
  { label: "Overtrading risk", value: "Medium", tone: "warn" },
  { label: "News risk", value: "High", tone: "warn" },
  { label: "Human review", value: "Required", tone: "info" },
];

// ── Section 5: Paper Game Plan ─────────────────────────────────────────────
const GAME_PLAN_ROWS: { label: string; value: string }[] = [
  { label: "Scenario", value: "Long only if confirmed" },
  { label: "Entry zone", value: "2,322 – 2,326 (example)" },
  { label: "Invalidation", value: "M15 candle close below 2,316 (example)" },
  { label: "TP1 / TP2", value: "2,341 / 2,352 (example)" },
  { label: "Max simulated risk", value: "1%" },
];

const GAME_PLAN_LABELS = [
  "Save to Journal",
  "Run Paper Preview",
  "Create Alert",
] as const;

// ── Section 6: Mobile Watchlist ────────────────────────────────────────────
type WatchRow = {
  symbol: string;
  bias: string;
  volatility: string;
  lastReview: string;
  riskMode: string;
};

const WATCHLIST: WatchRow[] = [
  { symbol: "XAUUSD", bias: "Neutral-Bullish", volatility: "High", lastReview: "12m ago", riskMode: "Paper · 1%" },
  { symbol: "US100", bias: "Bullish", volatility: "Medium", lastReview: "34m ago", riskMode: "Paper · 1%" },
  { symbol: "EURUSD", bias: "Neutral", volatility: "Low", lastReview: "1h ago", riskMode: "Paper · 0.5%" },
  { symbol: "WTI", bias: "Bearish", volatility: "High", lastReview: "2h ago", riskMode: "Paper · 0.5%" },
  { symbol: "NVDA", bias: "Bullish", volatility: "High", lastReview: "3h ago", riskMode: "Paper · 1%" },
  { symbol: "BTC", bias: "Range", volatility: "High", lastReview: "5h ago", riskMode: "Paper · 0.5%" },
];

const WATCH_LABELS = ["Review", "Paper", "Journal"] as const;

// ── Section 7: Setup Journal ───────────────────────────────────────────────
// MOBILE-AI-004 — Setup Journal mock (display-only, paper/simulation only).

// Journal dashboard summary (static mock metrics).
const JOURNAL_SUMMARY: { label: string; value: string; tone?: "ok" | "warn" | "info" }[] = [
  { label: "Saved setups", value: "12" },
  { label: "Pending review", value: "3", tone: "info" },
  { label: "Reviewed this week", value: "7", tone: "ok" },
  { label: "Best setup type", value: "Retest continuation", tone: "ok" },
  { label: "Most common risk pattern", value: "Over-analysis before candle close", tone: "warn" },
  { label: "Safety mode", value: "Paper only", tone: "ok" },
];

type JournalStatusTone = "ok" | "warn" | "info" | "muted";

type JournalEntry = {
  instrument: string;
  timeframe: string;
  setup: string;
  bias: string;
  risk: string;
  status: string;
  statusTone: JournalStatusTone;
  emotion: string;
  plan: string;
  outcome: string;
};

const JOURNAL_ENTRIES: JournalEntry[] = [
  {
    instrument: "XAUUSD",
    timeframe: "M15",
    setup: "Retest continuation",
    bias: "Neutral-Bullish",
    risk: "0.5%",
    status: "Pending review",
    statusTone: "info",
    emotion: "Calm",
    plan: "Wait for retest confirmation",
    outcome: "Not reviewed yet",
  },
  {
    instrument: "US100",
    timeframe: "M5",
    setup: "Breakout fakeout avoided",
    bias: "Mixed",
    risk: "0.25%",
    status: "Skipped",
    statusTone: "muted",
    emotion: "FOMO risk",
    plan: "Wait for candle close",
    outcome: "Skipped correctly",
  },
  {
    instrument: "EURUSD",
    timeframe: "H1",
    setup: "Range rejection",
    bias: "Neutral",
    risk: "0.5%",
    status: "TP1 simulated",
    statusTone: "ok",
    emotion: "Patient",
    plan: "Paper only after confirmation",
    outcome: "TP1 paper path reached",
  },
  {
    instrument: "WTI",
    timeframe: "M15",
    setup: "High-risk news trade",
    bias: "Volatile",
    risk: "0%",
    status: "Invalidated",
    statusTone: "warn",
    emotion: "News caution",
    plan: "No trade during news spike",
    outcome: "Invalidated before entry",
  },
];

// Outcome review chips (static mock, not state-mutating controls).
const OUTCOME_CHIPS = [
  "TP1",
  "TP2",
  "SL",
  "Skipped",
  "Invalidated",
  "Still waiting",
] as const;

// Emotion / behavior tag cloud (links FOMO Guard + Weekly Review).
const EMOTION_TAGS = [
  "Calm",
  "FOMO risk",
  "Revenge risk",
  "News caution",
  "Patient",
  "Over-analysis",
  "Chased entry avoided",
  "Waited for candle close",
] as const;

// Journal timeline (chronological, display-only).
const JOURNAL_TIMELINE: { time: string; event: string }[] = [
  { time: "09:10", event: "XAUUSD reviewed" },
  { time: "10:25", event: "US100 skipped" },
  { time: "12:40", event: "EURUSD TP1 paper path" },
  { time: "14:00", event: "WTI invalidated" },
  { time: "16:30", event: "Weekly report generated" },
];

// ── Section 8: Before/After Review chips ───────────────────────────────────
const REVIEW_CHIPS = ["TP1", "TP2", "SL", "Skipped", "Invalidated"] as const;

// ── Section 10: Weekly Report preview ──────────────────────────────────────
const WEEKLY_BEST = [
  "Retest continuation",
  "Breakout fakeout avoided",
  "High-risk news trades skipped",
] as const;

// Weekly learning summary (MOBILE-AI-004).
const WEEKLY_LEARNING: { label: string; value: string }[] = [
  { label: "Best setup", value: "Retest continuation" },
  { label: "Best behavior", value: "Waited for candle close" },
  { label: "Mistake avoided", value: "Breakout fakeout" },
  { label: "Highest risk pattern", value: "Analyzing same asset repeatedly" },
  { label: "Next focus", value: "Fewer low-quality analyses, more confirmed retests" },
];

const WEEKLY_METRICS: { label: string; value: string; tone: "ok" | "warn" | "info" }[] = [
  { label: "Discipline score", value: "78/100", tone: "info" },
  { label: "Overtrading risk", value: "Medium", tone: "warn" },
  { label: "Review completion", value: "7/10", tone: "info" },
  { label: "Paper-only compliance", value: "100%", tone: "ok" },
];

// ── Section 9: FOMO Guard + Risk Coach (MOBILE-AI-005) ─────────────────────
// All data below is static mock behavior feedback. No timers, no state,
// no network calls, no trading execution.

const FOMO_METRICS: { label: string; value: string; tone: "ok" | "warn" | "info" }[] = [
  { label: "Repeated analysis", value: "High", tone: "warn" },
  { label: "Candle-close discipline", value: "Medium", tone: "info" },
  { label: "News-risk awareness", value: "High", tone: "ok" },
  { label: "Overtrading risk", value: "Medium", tone: "warn" },
  { label: "Cooldown suggestion", value: "15 min", tone: "info" },
  { label: "Current mode", value: "Paper only", tone: "ok" },
];

const COOLDOWN_ROWS: { label: string; value: string }[] = [
  { label: "Cooldown", value: "15 min suggested" },
  { label: "Current state", value: "Waiting for confirmation" },
  { label: "Next allowed review", value: "After candle close" },
];

const BEHAVIOR_RULES = [
  "One clean setup > five rushed analyses",
  "Wait for candle close",
  "No revenge analysis after invalidation",
  "No trade during high-impact news spike",
  "Risk must stay ≤ 1%",
  "Paper plan before any decision",
] as const;

const COACH_SUBMETRICS: { label: string; value: string; tone: "ok" | "warn" | "info" }[] = [
  { label: "Discipline", value: "78", tone: "info" },
  { label: "Patience", value: "72", tone: "info" },
  { label: "Over-analysis control", value: "64", tone: "warn" },
  { label: "News caution", value: "86", tone: "ok" },
  { label: "Journal completion", value: "70", tone: "info" },
  { label: "Paper-only compliance", value: "100", tone: "ok" },
];

const COACH_MESSAGES = [
  "Wait for confirmation. The plan is stronger after the candle closes.",
  "You already reviewed this setup. Re-checking too often can create FOMO.",
  "Paper plan first. Live orders are blocked.",
  "Good skip. Avoiding bad trades is part of edge-building.",
] as const;

const ANTI_FOMO_SCRIPT = [
  "What is the setup?",
  "What invalidates it?",
  "Is risk ≤ 1%?",
  "Is this after candle close?",
  "Would I still take this if I had not seen the last candle?",
] as const;

const WATCHLIST_NUDGES: { symbol: string; nudge: string }[] = [
  { symbol: "XAUUSD", nudge: "High volatility · wait for M15 close" },
  { symbol: "US100", nudge: "FOMO risk · avoid chasing breakout candle" },
  { symbol: "EURUSD", nudge: "Range mode · wait for rejection" },
  { symbol: "WTI", nudge: "News risk · paper-only review" },
  { symbol: "BTC", nudge: "Volatile · reduce analysis frequency" },
];

const COACH_SUMMARY: { label: string; value: string }[] = [
  { label: "Best behavior", value: "Skipped invalidated setup" },
  { label: "Risk improvement", value: "Used 0.5% paper risk" },
  { label: "FOMO pattern", value: "Repeated analysis before close" },
  { label: "Next focus", value: "Fewer reviews, better confirmations" },
];

// ── Section 11: Monte Carlo Simulation Snapshot (static existing summary) ──
const MONTE_CARLO_ROWS: { label: string; value: string }[] = [
  { label: "Simulated paper paths", value: "1,000" },
  { label: "Expected range", value: "-1.0% to +1.8% (paper)" },
  { label: "Tail risk", value: "~5% paths beyond -1% (capped by 1% risk)" },
  { label: "Status", value: "Existing Monte Carlo summary · demo snapshot" },
];

// Compact quick-navigation preserved from the existing shell. Only routes
// that exist in App.tsx are linked here (no broken links, no trading actions).
const QUICK_LINKS: { label: string; to: string }[] = [
  { label: "Terminal", to: "/terminal" },
  { label: "Watchlist", to: "/watchlist" },
  { label: "Paper Run Preview", to: "/terminal/paper-run-preview" },
  { label: "Audit Trail", to: "/audit" },
];

export function MobileAppPage() {
  return (
    <div className="mobile-app-page">
      <main
        className="mobile-app-shell"
        aria-label="MellyTrade mobile AI chart review"
      >
        {/* ── 1. Header ─────────────────────────────────────────────────── */}
        <header className="mobile-app-header">
          <p className="mobile-app-eyebrow">Mobile Command Center</p>
          <h1 className="mobile-app-title">MellyTrade Mobile</h1>
          <p className="mobile-app-subtitle">
            AI chart review, paper plans, journal, and FOMO guard.
          </p>
          <div className="mobile-safety-strip" aria-label="Active safety constraints">
            {SAFETY_BADGES.map((badge) => (
              <span key={badge} className="mobile-safety-badge">
                {badge}
              </span>
            ))}
          </div>
        </header>

        {/* ── 2. Mobile action grid ─────────────────────────────────────── */}
        <section aria-label="Mobile actions">
          <h2 className="mobile-section-title">Quick actions</h2>
          <div className="mobile-action-grid">
            {ACTION_CARDS.map((card) => (
              <div
                key={card.title}
                className="mobile-action-card"
                role="group"
                aria-label={`${card.title} (mock)`}
              >
                <span className="mobile-action-name">{card.title}</span>
                <span className="mobile-action-hint">{card.hint}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ── 3. AI Chart Review mock ───────────────────────────────────── */}
        <section aria-label="AI chart review" className="mobile-card mobile-card--accent">
          <div className="mobile-card-head">
            <h2 className="mobile-card-title">AI Chart Review</h2>
            <span className="mobile-pill mobile-pill--amber">Mock</span>
          </div>
          <dl className="mobile-fact-list">
            {CHART_REVIEW_FACTS.map((fact) => (
              <div key={fact.label} className="mobile-fact-row">
                <dt className="mobile-fact-label">{fact.label}</dt>
                <dd className="mobile-fact-value">{fact.value}</dd>
              </div>
            ))}
          </dl>
          <div className="mobile-checklist" aria-label="Confirmation checklist">
            <p className="mobile-subhead">Confirmation checklist</p>
            <ul className="mobile-check-items">
              {CONFIRMATION_CHECKLIST.map((item) => (
                <li key={item} className="mobile-check-item">
                  <span className="mobile-check-box" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <p className="mobile-disclaimer">Analysis only. Not financial advice.</p>
        </section>

        {/* ── 3b. AI Screenshot Review (MOBILE-AI-007C) ─────────────────── */}
        <ScreenshotPreviewCard />

        {/* ── 4. Safety Score ───────────────────────────────────────────── */}
        <section aria-label="Safety score" className="mobile-card">
          <div className="mobile-card-head">
            <h2 className="mobile-card-title">Safety Score</h2>
            <span className="mobile-score" aria-label="Safety score 82 of 100">
              82<span className="mobile-score-max">/100</span>
            </span>
          </div>
          <dl className="mobile-fact-list">
            {SAFETY_ROWS.map((row) => (
              <div key={row.label} className="mobile-fact-row">
                <dt className="mobile-fact-label">{row.label}</dt>
                <dd className={`mobile-fact-value mobile-tone--${row.tone}`}>
                  {row.value}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        {/* ── 5. Paper Game Plan ────────────────────────────────────────── */}
        <section aria-label="Paper game plan" className="mobile-card">
          <div className="mobile-card-head">
            <h2 className="mobile-card-title">Paper Game Plan</h2>
            <span className="mobile-pill mobile-pill--green">PAPER ONLY</span>
          </div>
          <dl className="mobile-fact-list">
            {GAME_PLAN_ROWS.map((row) => (
              <div key={row.label} className="mobile-fact-row">
                <dt className="mobile-fact-label">{row.label}</dt>
                <dd className="mobile-fact-value">{row.value}</dd>
              </div>
            ))}
          </dl>
          <div className="mobile-chip-row" aria-label="Mock labels (not active)">
            {GAME_PLAN_LABELS.map((label) => (
              <span key={label} className="mobile-static-chip" aria-disabled="true">
                {label}
              </span>
            ))}
          </div>
          <p className="mobile-disclaimer">
            Paper plan only. No live orders. Human review required.
          </p>
        </section>

        {/* ── 6. Mobile Watchlist ───────────────────────────────────────── */}
        <section aria-label="Mobile watchlist">
          <h2 className="mobile-section-title">Watchlist</h2>
          <div className="mobile-watch-grid">
            {WATCHLIST.map((row) => (
              <div key={row.symbol} className="mobile-watch-card">
                <div className="mobile-watch-top">
                  <span className="mobile-watch-symbol">{row.symbol}</span>
                  <span className="mobile-watch-vol">{row.volatility} vol</span>
                </div>
                <p className="mobile-watch-meta">
                  Bias: {row.bias} · Last AI review: {row.lastReview}
                </p>
                <p className="mobile-watch-meta">Risk mode: {row.riskMode}</p>
                <div className="mobile-chip-row">
                  {WATCH_LABELS.map((label) => (
                    <span
                      key={label}
                      className="mobile-static-chip mobile-static-chip--sm"
                      aria-disabled="true"
                    >
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── 7. Setup Journal ──────────────────────────────────────────── */}
        <section aria-label="Setup journal">
          <h2 className="mobile-section-title">Setup Journal</h2>

          {/* 7a. Journal dashboard summary */}
          <div className="mobile-card mobile-card--accent">
            <div className="mobile-card-head">
              <h3 className="mobile-card-title">Journal summary</h3>
              <span className="mobile-pill mobile-pill--green">Paper only</span>
            </div>
            <dl className="mobile-fact-list">
              {JOURNAL_SUMMARY.map((row) => (
                <div key={row.label} className="mobile-fact-row">
                  <dt className="mobile-fact-label">{row.label}</dt>
                  <dd
                    className={
                      row.tone
                        ? `mobile-fact-value mobile-tone--${row.tone}`
                        : "mobile-fact-value"
                    }
                  >
                    {row.value}
                  </dd>
                </div>
              ))}
            </dl>
            <p className="mobile-disclaimer">
              Journal is for review and learning only. No live orders.
            </p>
          </div>

          {/* 7b. Saved setup cards */}
          <h3 className="mobile-subhead mobile-subhead--spaced">Saved setups</h3>
          <div className="mobile-journal-grid">
            {JOURNAL_ENTRIES.map((entry) => (
              <article
                key={`${entry.instrument}-${entry.setup}`}
                className="mobile-card mobile-journal-card"
              >
                <div className="mobile-card-head">
                  <h4 className="mobile-card-title">
                    {entry.instrument} {entry.timeframe}
                  </h4>
                  <span
                    className={`mobile-pill mobile-pill--${
                      entry.statusTone === "muted" ? "muted" : entry.statusTone
                    }`}
                  >
                    {entry.status}
                  </span>
                </div>
                <p className="mobile-journal-line">Setup: {entry.setup}</p>
                <p className="mobile-journal-line">Bias: {entry.bias}</p>
                <p className="mobile-journal-line">Risk: {entry.risk}</p>
                <p className="mobile-journal-line">Plan: {entry.plan}</p>
                <p className="mobile-journal-line mobile-tone--info">
                  Outcome: {entry.outcome}
                </p>
                <div className="mobile-chip-row">
                  <span
                    className="mobile-static-chip mobile-static-chip--sm"
                    aria-disabled="true"
                  >
                    {entry.emotion}
                  </span>
                </div>
              </article>
            ))}

            {/* 7e. Empty state example (mock placeholder, does not replace data) */}
            <article
              className="mobile-card mobile-journal-card mobile-journal-card--empty"
              aria-label="Journal empty state example"
            >
              <h4 className="mobile-card-title">No journal entries yet</h4>
              <p className="mobile-journal-line mobile-tone--info">
                Save an analysis to review the setup later.
              </p>
            </article>
          </div>

          {/* 7c. Outcome review panel */}
          <div className="mobile-card">
            <div className="mobile-card-head">
              <h3 className="mobile-card-title">Review outcome</h3>
              <span className="mobile-pill mobile-pill--blue">Review</span>
            </div>
            <div className="mobile-chip-row" aria-label="Outcome review chips">
              {OUTCOME_CHIPS.map((chip) => (
                <span
                  key={chip}
                  className="mobile-static-chip"
                  aria-disabled="true"
                >
                  {chip}
                </span>
              ))}
            </div>
            <p className="mobile-disclaimer">
              Outcome review teaches the model/user what happened after the
              plan. It does not execute trades.
            </p>
          </div>

          {/* 7d. Emotion / behavior tags */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Emotion &amp; behavior tags</h3>
            <p className="mobile-card-sub">
              Connects to FOMO Guard and Weekly Review.
            </p>
            <div className="mobile-chip-row" aria-label="Emotion and behavior tags">
              {EMOTION_TAGS.map((tag) => (
                <span
                  key={tag}
                  className="mobile-static-chip mobile-static-chip--sm"
                  aria-disabled="true"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* 7f. Journal timeline */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Today&rsquo;s journal timeline</h3>
            <ol className="mobile-timeline" aria-label="Journal timeline">
              {JOURNAL_TIMELINE.map((item) => (
                <li key={`${item.time}-${item.event}`} className="mobile-timeline-item">
                  <span className="mobile-timeline-time">{item.time}</span>
                  <span className="mobile-timeline-event">{item.event}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* ── 8. Before/After Review ────────────────────────────────────── */}
        <section aria-label="Before and after review" className="mobile-card">
          <h2 className="mobile-card-title">Did the setup play out?</h2>
          <p className="mobile-card-sub">
            Status chips only — paper review, no trading action.
          </p>
          <div className="mobile-chip-row" aria-label="Outcome status chips">
            {REVIEW_CHIPS.map((chip) => (
              <span key={chip} className="mobile-static-chip" aria-disabled="true">
                {chip}
              </span>
            ))}
          </div>
        </section>

        {/* ── 9. FOMO Guard + Risk Coach ────────────────────────────────── */}
        <section aria-label="FOMO guard and risk coach">
          <h2 className="mobile-section-title">FOMO Guard &amp; Risk Coach</h2>

          {/* 9.1 FOMO Guard dashboard card */}
          <div className="mobile-card mobile-card--warn">
            <div className="mobile-card-head">
              <h3 className="mobile-card-title">FOMO Guard</h3>
              <span className="mobile-pill mobile-pill--warn">ACTIVE</span>
            </div>
            <p className="mobile-card-body">
              You analyzed XAUUSD 4 times in 30 minutes.
            </p>
            <p className="mobile-card-body mobile-tone--warn">
              Wait for the next M15 candle close before reviewing again.
            </p>
            <dl className="mobile-fact-list">
              {FOMO_METRICS.map((row) => (
                <div key={row.label} className="mobile-fact-row">
                  <dt className="mobile-fact-label">{row.label}</dt>
                  <dd className={`mobile-fact-value mobile-tone--${row.tone}`}>
                    {row.value}
                  </dd>
                </div>
              ))}
            </dl>
            <p className="mobile-disclaimer">
              FOMO Guard is behavior feedback only. It does not execute trades.
            </p>
          </div>

          {/* 9.2 Cooldown meter (static, no timers) */}
          <div className="mobile-card">
            <div className="mobile-card-head">
              <h3 className="mobile-card-title">Cooldown</h3>
              <span className="mobile-pill mobile-pill--amber">15 min</span>
            </div>
            <div
              className="mobile-cooldown-meter"
              role="img"
              aria-label="Cooldown suggested, waiting for confirmation"
            >
              <div className="mobile-cooldown-fill" />
            </div>
            <dl className="mobile-fact-list">
              {COOLDOWN_ROWS.map((row) => (
                <div key={row.label} className="mobile-fact-row">
                  <dt className="mobile-fact-label">{row.label}</dt>
                  <dd className="mobile-fact-value">{row.value}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* 9.3 Behavior rules panel */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Rules before review</h3>
            <ul className="mobile-rule-list">
              {BEHAVIOR_RULES.map((rule) => (
                <li key={rule} className="mobile-rule-item">
                  <span className="mobile-rule-mark" aria-hidden="true">
                    ✓
                  </span>
                  {rule}
                </li>
              ))}
            </ul>
          </div>

          {/* 9.4 Risk Coach Score card */}
          <div className="mobile-card mobile-card--accent">
            <div className="mobile-card-head">
              <h3 className="mobile-card-title">Risk Coach Score</h3>
              <span className="mobile-score" aria-label="Risk coach score 78 of 100">
                78<span className="mobile-score-max">/100</span>
              </span>
            </div>
            <div className="mobile-metric-grid" aria-label="Risk coach sub-metrics">
              {COACH_SUBMETRICS.map((metric) => (
                <div key={metric.label} className="mobile-metric-chip">
                  <span className="mobile-metric-label">{metric.label}</span>
                  <span className={`mobile-metric-value mobile-tone--${metric.tone}`}>
                    {metric.value}
                  </span>
                </div>
              ))}
            </div>
            <p className="mobile-journal-line mobile-tone--ok">
              Strongest behavior this week: skipping high-risk news setups.
            </p>
            <p className="mobile-journal-line mobile-tone--warn">
              Weakest behavior this week: repeated analysis before candle close.
            </p>
          </div>

          {/* 9.5 Melly Pet coach messages */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Melly Pet coach</h3>
            <p className="mobile-card-sub">
              Melly Pet reviews risk behavior and journal outcomes. It never
              places orders and never enables live trading.
            </p>
            <ul className="mobile-coach-list">
              {COACH_MESSAGES.map((msg) => (
                <li key={msg} className="mobile-coach-message">
                  {msg}
                </li>
              ))}
            </ul>
          </div>

          {/* 9.6 Anti-FOMO review script */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Before you review again</h3>
            <ol className="mobile-script-list">
              {ANTI_FOMO_SCRIPT.map((q) => (
                <li key={q} className="mobile-script-item">
                  {q}
                </li>
              ))}
            </ol>
            <p className="mobile-disclaimer">
              Static review checklist. No trading action. Live orders blocked.
            </p>
          </div>

          {/* 9.7 Watchlist risk nudges */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Watchlist risk nudges</h3>
            <ul className="mobile-nudge-list">
              {WATCHLIST_NUDGES.map((item) => (
                <li key={item.symbol} className="mobile-nudge-item">
                  <span className="mobile-nudge-symbol">{item.symbol}</span>
                  <span className="mobile-nudge-text">{item.nudge}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 9.8 Journal connection copy */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Linked to your Setup Journal</h3>
            <p className="mobile-card-body">
              FOMO Guard reads your mock journal pattern: repeated XAUUSD
              reviews, skipped news trades, and pending outcome reviews.
            </p>
          </div>

          {/* 9.9 Weekly coach summary */}
          <div className="mobile-card">
            <h3 className="mobile-card-title">Coach Summary This Week</h3>
            <dl className="mobile-fact-list">
              {COACH_SUMMARY.map((row) => (
                <div key={row.label} className="mobile-fact-row">
                  <dt className="mobile-fact-label">{row.label}</dt>
                  <dd className="mobile-fact-value">{row.value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* ── 10. Weekly Report + learning summary ──────────────────────── */}
        <section aria-label="Weekly report and learning summary" className="mobile-card">
          <h2 className="mobile-card-title">Your best setups this week</h2>
          <ul className="mobile-bullet-list">
            {WEEKLY_BEST.map((item) => (
              <li key={item} className="mobile-bullet-item">
                {item}
              </li>
            ))}
          </ul>
          <p className="mobile-card-body mobile-tone--warn">
            Most common risk pattern: over-analysis before candle close.
          </p>

          <h3 className="mobile-subhead mobile-subhead--spaced">
            Weekly learning summary
          </h3>
          <dl className="mobile-fact-list">
            {WEEKLY_LEARNING.map((row) => (
              <div key={row.label} className="mobile-fact-row">
                <dt className="mobile-fact-label">{row.label}</dt>
                <dd className="mobile-fact-value">{row.value}</dd>
              </div>
            ))}
          </dl>

          <div className="mobile-metric-grid" aria-label="Weekly discipline metrics">
            {WEEKLY_METRICS.map((metric) => (
              <div key={metric.label} className="mobile-metric-chip">
                <span className="mobile-metric-label">{metric.label}</span>
                <span className={`mobile-metric-value mobile-tone--${metric.tone}`}>
                  {metric.value}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* ── 11. Monte Carlo Simulation Snapshot (existing static summary) ─ */}
        <section
          aria-label="Monte Carlo simulation snapshot"
          className="mobile-card"
        >
          <div className="mobile-card-head">
            <h2 className="mobile-card-title">Monte Carlo Simulation Snapshot</h2>
            <span className="mobile-pill mobile-pill--blue">Snapshot</span>
          </div>
          <dl className="mobile-fact-list">
            {MONTE_CARLO_ROWS.map((row) => (
              <div key={row.label} className="mobile-fact-row">
                <dt className="mobile-fact-label">{row.label}</dt>
                <dd className="mobile-fact-value">{row.value}</dd>
              </div>
            ))}
          </dl>
          <p className="mobile-disclaimer">
            Existing simulation summary only. No new engine, no backend call.
            Paper/simulation only.
          </p>
        </section>

        {/* ── 12. Melly Pet Coach ───────────────────────────────────────── */}
        <section
          className="mobile-melly-pet-card"
          aria-label="Melly Pet read-only risk coach"
        >
          <MellyPetMascot />
          <p className="mobile-melly-pet-copy">
            Melly Pet reviews your saved setups, flags FOMO behavior, and helps
            you learn from paper outcomes. It never places orders or enables
            live trading.
          </p>
        </section>

        {/* Quick navigation (existing routes only) */}
        <section aria-label="Quick navigation">
          <h2 className="mobile-section-title">Quick navigation</h2>
          <nav className="mobile-quick-links">
            {QUICK_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="mobile-quick-link">
                {link.label}
              </Link>
            ))}
          </nav>
        </section>

        <footer className="mobile-app-footer">
          <p>
            This mobile shell is a read-only, paper/simulation-only demo
            surface. Analysis only. Not financial advice. No broker execution.
            No wallet/private keys. Human review required.
          </p>
        </footer>
      </main>
    </div>
  );
}
