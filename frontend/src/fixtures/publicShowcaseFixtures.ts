/**
 * publicShowcaseFixtures — PUBLIC-SITE-001
 *
 * Static, illustrative sample data for the public landing (`/`) and
 * case-study (`/case-study`) pages. No network calls, no backend endpoints.
 * Every figure here is DEMO / PAPER / SIMULATED and must never be presented
 * as a live account, a live feed, or a real trading result.
 *
 * Facts used in the GitHub Evidence / Case Study sections (repo URL, PR
 * numbers, test counts, CI workflow names) are sourced from README.md and
 * are real repository facts, not performance claims.
 */

import type {
  IBKRStatus,
  MarketItem,
  PositionItem,
  SignalItem,
  TerminalEvent,
  PortfolioRiskSummaryResponse,
} from "../lib/terminalApi";
import type { TerminalShellData } from "../components/terminal/TerminalShell";
import { createScannerPreviewFallback } from "../lib/scannerPreviewApi";

export const GITHUB_REPO_URL = "https://github.com/Melly-999/alpha_data_scraper_ai";

const demoIBKRStatus: IBKRStatus = {
  name: "IBKR Paper",
  status: "paper",
  read_only: true,
  execution_enabled: false,
  data_freshness: "demo",
  latency_ms: 0,
  diagnostics: ["Demo preview — no live broker connection."],
  permissions: {
    market_data: "allowed",
    account_read: "allowed",
    positions_read: "allowed",
    orders: "denied",
    live_execution: "denied",
  },
};

const demoMarkets: MarketItem[] = [
  { symbol: "EURUSD", price: 1.0842, change_pct: 0.18, signal: "WATCH", confidence: 61 },
  { symbol: "XAUUSD", price: 2331.4, change_pct: -0.32, signal: "HOLD", confidence: 54 },
  { symbol: "US500", price: 5321.7, change_pct: 0.41, signal: "WATCH", confidence: 58 },
  { symbol: "GBPUSD", price: 1.2714, change_pct: -0.09, signal: "HOLD", confidence: 49 },
];

const demoSignals: SignalItem[] = [
  {
    id: "demo-signal-1",
    symbol: "XAUUSD",
    direction: "HOLD",
    confidence: 54,
    timeframe: "M15",
    reason: "Sample advisory output — paper/simulated, not financial advice.",
  },
  {
    id: "demo-signal-2",
    symbol: "EURUSD",
    direction: "BUY",
    confidence: 61,
    timeframe: "H1",
    reason: "Illustrative signal reasoning. Human review required. No execution.",
  },
];

const demoPositions: PositionItem[] = [
  {
    id: "demo-position-1",
    symbol: "XAUUSD",
    side: "long",
    quantity: 0.1,
    pnl: 0,
    source: "paper",
    average_price: 2318.2,
    market_price: 2331.4,
    currency: "USD",
  },
];

export const demoAuditEvents: TerminalEvent[] = [
  {
    id: "demo-evt-1",
    event: "analysis_run",
    severity: "info",
    time: "09:41",
    message: "Sample analysis executed on demo data.",
    source: "ai-workspace",
    safety_note: "Advisory only · not financial advice",
  },
  {
    id: "demo-evt-2",
    event: "safety_check_passed",
    severity: "success",
    time: "09:41",
    message: "Read-only invariants confirmed before render.",
    source: "safety-validator",
    safety_note: "read_only=true · autotrade=false",
  },
  {
    id: "demo-evt-3",
    event: "risk_blocked",
    severity: "warning",
    time: "09:40",
    message: "Simulated risk gate would block execution above 1% risk.",
    source: "risk-manager",
    safety_note: "live_orders_blocked=true",
  },
  {
    id: "demo-evt-4",
    event: "config_assertion",
    severity: "success",
    time: "09:39",
    message: "dry_run and live_orders_blocked asserted true on load.",
    source: "config-guard",
    safety_note: null,
  },
];

export const demoTerminalShellData: TerminalShellData = {
  summary: {
    terminal: "MellyTrade V1 Terminal — Demo Preview",
    mode: "read-only",
    backend: "fallback",
    safety: {
      read_only: true,
      dry_run: true,
      auto_trade: false,
      live_orders_blocked: true,
    },
    broker: demoIBKRStatus,
    updated_at: new Date().toISOString(),
  },
  markets: demoMarkets,
  watchlist: demoMarkets,
  signals: demoSignals,
  scannerPreview: createScannerPreviewFallback(),
  riskStatus: {
    max_risk_per_trade_pct: 1,
    dry_run: true,
    auto_trade: false,
    read_only: true,
    stop_loss_required: true,
    take_profit_required: true,
    live_orders_blocked: true,
  },
  riskPolicy: {
    min_confidence: 70,
    daily_loss_cap_pct: 3,
    open_position_cap: 3,
    execution_enabled: false,
    max_risk_per_trade_pct: 1,
    dry_run: true,
    auto_trade: false,
    read_only: true,
    live_orders_blocked: true,
    stop_loss_required: true,
    take_profit_required: true,
  },
  backtest: {
    win_rate: 0,
    max_drawdown_pct: 0,
    profit_factor: 0,
    sample_size: 0,
  },
  news: [],
  positions: demoPositions,
  mt5: {
    connected: false,
    mode: "synthetic",
    data_freshness: "demo",
  },
  events: demoAuditEvents,
  broker: demoIBKRStatus,
};

export const demoPortfolioRiskSummary: PortfolioRiskSummaryResponse = {
  status: "ok",
  mode: "read_only",
  read_only: true,
  dry_run: true,
  live_orders_blocked: true,
  execution_mode: "dry_run_only",
  requires_human_review: true,
  risk_allowed: false,
  source: "portfolio_risk_summary",
  exposure: {
    total_positions: 3,
    open_positions: 1,
    total_notional: 4200,
    gross_exposure_pct: 8.4,
    net_exposure_pct: 8.4,
    cash_buffer_pct: 91.6,
  },
  limits: {
    max_risk_per_trade_pct: 1,
    max_portfolio_risk_pct: 3,
    risk_used_pct: 0.6,
    remaining_risk_capacity_pct: 2.4,
    max_open_positions: 3,
  },
  posture: {
    label: "read_only",
    status: "ok",
    broker_execution_allowed: false,
    live_orders_blocked: true,
    risk_allowed: false,
    requires_human_review: true,
  },
  notes: ["Illustrative demo data — not a live account. Advisory only, not financial advice."],
  updated_at: new Date().toISOString(),
};

export type EvidenceCard = {
  title: string;
  detail: string;
  href: string;
  tag: string;
};

export const githubEvidenceCards: EvidenceCard[] = [
  {
    title: "Source repository",
    detail: "Full commit history, PRs, and architecture — nothing hidden.",
    href: GITHUB_REPO_URL,
    tag: "REPO",
  },
  {
    title: "Safety regression suite",
    detail: "test_safety_invariants.py + test_openapi_forbidden_paths.py — 60 tests passed.",
    href: `${GITHUB_REPO_URL}/blob/main/tests/app/test_safety_invariants.py`,
    tag: "PYTEST",
  },
  {
    title: "Playwright e2e suite",
    detail: "54 tests across iPad and mobile viewports, run in GitHub Actions.",
    href: `${GITHUB_REPO_URL}/blob/main/.github/workflows/frontend-e2e.yml`,
    tag: "E2E",
  },
  {
    title: "Static safety scan",
    detail: "Forbidden-path + denylist scan — no execute/order paths permitted.",
    href: `${GITHUB_REPO_URL}/blob/main/.github/workflows/security.yml`,
    tag: "SCAN",
  },
  {
    title: "Hosted smoke evidence",
    detail: "21-check hosted smoke run against production URLs (demo-008).",
    href: `${GITHUB_REPO_URL}/blob/main/docs/evidence/demo-008-hosted-smoke-pass.md`,
    tag: "EVIDENCE",
  },
  {
    title: "CI: pytest",
    detail: "Every push runs the full pytest suite before merge.",
    href: `${GITHUB_REPO_URL}/blob/main/.github/workflows/pytest.yml`,
    tag: "CI",
  },
];

export type MilestoneCard = {
  label: string;
  detail: string;
  status: "shipped" | "next";
};

export const roadmapMilestones: MilestoneCard[] = [
  { label: "Read-only terminal + safety contract", detail: "Institutional dashboard, safety badges enforced end-to-end.", status: "shipped" },
  { label: "Paper sandbox + audit trail", detail: "GET-only paper preview endpoint, append-only audit event feed.", status: "shipped" },
  { label: "Mobile / iPad PWA companion", detail: "Installable read-only companion, 54-test Playwright coverage.", status: "shipped" },
  { label: "Hosted deploy + SPA deep-link fix", detail: "Vercel + Render hosting, 21-check hosted smoke pass (demo-008).", status: "shipped" },
  { label: "Public landing + case study", detail: "This layer — recruiter/client-facing showcase over the existing platform.", status: "shipped" },
  { label: "Demo media pack", detail: "Hero image + short clips (separate, budgeted media-generation run).", status: "next" },
  { label: "Expanded AI reasoning panel", detail: "Deeper signal-reasoning UI on the existing AI workspace.", status: "next" },
  { label: "EXE / desktop wrapper", detail: "Optional desktop packaging exploration.", status: "next" },
];
