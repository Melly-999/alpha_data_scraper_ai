import { Link } from "react-router-dom";

import { MellyPetMascot } from "../components/branding/MellyPetMascot";
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

// ── Section 7: Setup Journal preview ───────────────────────────────────────
type JournalEntry = {
  instrument: string;
  timeframe: string;
  setup: string;
  risk: string;
  plan: string;
  outcome: string;
  emotion: string;
};

const JOURNAL_ENTRIES: JournalEntry[] = [
  {
    instrument: "XAUUSD",
    timeframe: "M15",
    setup: "Retest continuation",
    risk: "0.5%",
    plan: "Wait for retest",
    outcome: "Pending review",
    emotion: "Calm",
  },
  {
    instrument: "US100",
    timeframe: "M15",
    setup: "Breakout pullback",
    risk: "1%",
    plan: "Wait for candle close",
    outcome: "Pending review",
    emotion: "FOMO risk",
  },
  {
    instrument: "WTI",
    timeframe: "H1",
    setup: "Range rejection",
    risk: "0.5%",
    plan: "Skip during news",
    outcome: "Pending review",
    emotion: "News caution",
  },
];

// ── Section 8: Before/After Review chips ───────────────────────────────────
const REVIEW_CHIPS = ["TP1", "TP2", "SL", "Skipped", "Invalidated"] as const;

// ── Section 10: Weekly Report preview ──────────────────────────────────────
const WEEKLY_BEST = [
  "Retest continuation",
  "Breakout fakeout avoided",
  "High-risk news trades skipped",
] as const;

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

        {/* ── 7. Setup Journal preview ──────────────────────────────────── */}
        <section aria-label="Setup journal preview">
          <h2 className="mobile-section-title">Setup Journal</h2>
          <div className="mobile-journal-grid">
            {JOURNAL_ENTRIES.map((entry) => (
              <article
                key={`${entry.instrument}-${entry.setup}`}
                className="mobile-card mobile-journal-card"
              >
                <div className="mobile-card-head">
                  <h3 className="mobile-card-title">
                    {entry.instrument} {entry.timeframe}
                  </h3>
                  <span className="mobile-pill mobile-pill--blue">
                    {entry.emotion}
                  </span>
                </div>
                <p className="mobile-journal-line">Setup: {entry.setup}</p>
                <p className="mobile-journal-line">Risk: {entry.risk}</p>
                <p className="mobile-journal-line">Plan: {entry.plan}</p>
                <p className="mobile-journal-line mobile-tone--info">
                  Outcome: {entry.outcome}
                </p>
              </article>
            ))}
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

        {/* ── 9. FOMO Guard ─────────────────────────────────────────────── */}
        <section
          aria-label="FOMO guard"
          className="mobile-card mobile-card--warn"
        >
          <div className="mobile-card-head">
            <h2 className="mobile-card-title">FOMO Guard active</h2>
            <span className="mobile-pill mobile-pill--warn">Guard</span>
          </div>
          <p className="mobile-card-body">
            You analyzed XAUUSD 4 times in 30 minutes. Suggestion: wait for
            candle close.
          </p>
          <p className="mobile-coach-quote">
            Melly Pet: &ldquo;Do not chase. Wait for confirmation.&rdquo;
          </p>
        </section>

        {/* ── 10. Weekly Report preview ─────────────────────────────────── */}
        <section aria-label="Weekly report preview" className="mobile-card">
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
            Melly Pet is your paper-only risk coach: chart review, risk guard,
            FOMO guard, and journal review. It never places orders and never
            enables live trading.
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
