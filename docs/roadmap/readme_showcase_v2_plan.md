# README / Showcase V2 — Financial Terminal Inspired

Status: PLANNED · Docs-only milestone · Added 2026-06-10
Base main SHA at planning time: `03d39b6a637b7bdfb69607f58285724fb88b68de`

> Note: this plan complements the broader showcase growth roadmap proposed in
> PR #261 (`docs/roadmap/mellytrade_showcase_growth_roadmap.md`,
> `docs/roadmap/module_priority_matrix.md`). Those files are not on `main`
> yet, so this milestone is documented here as a self-contained plan.

---

## 1. Goal

Upgrade the GitHub README into a professional financial-terminal showcase
inspired by OpenBB, Freqtrade, Hummingbot, Superalgos, and operational
dashboard products (Grafana/Kibana style) — while keeping MellyTrade's
safety-first, read-only, paper-only identity front and center.

MellyTrade is **not** a live trading bot. It is a safety-first AI trading
terminal and paper-risk workspace: web app, mobile/PWA route, desktop
EXE/Tauri thin-shell, FastAPI backend, read-only broker surfaces, paper-only
previews, and audit/safety evidence. No live order execution, no broker
execution, no real-money trading.

## 2. Why

The current README proves the project works (live links, hosted screenshots,
merged feature PRs), but it should better communicate:

- product value in the first 30 seconds,
- the safety posture (read-only / dry-run / live-orders-blocked) near the top,
- the live demo surface matrix (web, mobile, desktop, API),
- architecture and feature surfaces,
- portfolio value for recruiters, clients, and technical reviewers.

## 3. Inspiration mapping (inspiration only — never copy-paste)

| Source | What to borrow |
|---|---|
| OpenBB | Professional financial data platform positioning; multi-surface architecture (Workspace/API-style framing of web + mobile + desktop + REST API) |
| Freqtrade | Dry-run/risk disclaimer discipline; prominent "use at your own risk, paper first" tone |
| Hummingbot | Quick links block; docs/community-first README layout |
| Superalgos | Visual platform feel; online demo + tutorials; paper/backtesting language; safety/trust warnings ("Before You Begin" style) |
| Grafana / Kibana | Real operational dashboard captures — actual product UI, not fake AI mockups |

## 4. Planned tasks

| Task ID | Scope | Phase |
|---|---|---|
| README-SHOWCASE-V2-001 | Rewrite README into financial-terminal showcase structure | Demo freeze |
| SCREENSHOTS-REALISM-001 | Replace weak/desktop-width captures with true-viewport real app captures | Demo freeze |
| MOBILE-PWA-POLISH-002 | P1 mobile polish (sticky header, inert actions, PWA wording) | After freeze |
| DEMO-FREEZE-REPORT-001 | Final demo freeze status report | Demo freeze |
| PORTFOLIO-CASE-STUDY-001 | Recruiter/client-facing case study doc | After freeze |

## 5. README target structure

1. Hero — title, one-line value proposition, safety badges
2. Live Demo Matrix — web / terminal / mobile / brokers / API health / API safety / desktop EXE evidence
3. Product Screenshots — real captures with "what this proves" captions
4. What MellyTrade Does — concise bullets
5. Safety Contract — near the top, explicit invariants
6. Architecture Overview — simple text diagram
7. Feature Surface Table — surface / route / what it proves / safety mode
8. Tech Stack
9. Current Status — live/merged/blocked table
10. Roadmap — demo polish · paper safety · observability/audit · future-only gated real-money readiness
11. What This Project Proves — recruiter/client framing
12. Disclaimer — not financial advice; no live execution; demo/paper/read-only only

## 6. Screenshot target

- Real app captures only — no AI-generated mockups, no fake mobile frames
- No private dashboards (Render/Vercel/GitHub settings stay out of frame)
- No tokens, cookies, API keys, account IDs, broker order IDs
- Replace `docs/assets/screenshots/public-demo/mobile-pwa.png` with a true
  mobile-viewport capture (390x844 or 393x852 emulation)
- Replace `docs/assets/screenshots/public-demo/ai-screenshot-review-result.png`
  with a true mobile capture scrolled to the AI Screenshot Review result
- Optional: add an Alpaca Paper Order Preview capture from `/terminal`
  (preview-only panel from PR #275 is live in production)
- Keep safety badges visible in frame where possible

## 7. Sequencing

1. ✅ PR #275 (Alpaca Paper preview-only order preview) merged
2. ✅ Mobile/PWA audit (MOBILE-PWA-POLISH-001) completed — PASS
3. ➡️ ROADMAP-FINTERM-001 — this document
4. README-SHOWCASE-V2-001
5. SCREENSHOTS-REALISM-001
6. DEMO-FREEZE-REPORT-001
7. Optional after freeze: MOBILE-PWA-POLISH-002 (P1 items)

## 8. Done criteria

- README has a professional first 30 seconds
- Screenshots look real (true viewports, actual product UI)
- Live links are clear and grouped
- Safety posture visible near the top
- No financial advice or profit claims anywhere
- No live trading claims anywhere
- A recruiter or client can understand the product in under 60 seconds

## 9. Mobile/PWA audit summary (MOBILE-PWA-POLISH-001, 2026-06-10)

Verdict: the `/mobile` route itself is real-product quality. The weakness was
the screenshot capture method, not the product.

- Viewports tested: 390x844, 412x915, 768x1024 — no horizontal scroll, layout adapts
- Safety UI visible: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · HUMAN REVIEW REQUIRED
- Forbidden controls absent: no Buy/Sell/Place Order/Execute/Submit Order, no live-trading switch, no broker execution button
- Privacy: no API keys, tokens, cookies, account IDs, or broker order IDs visible
- Console: clean (no errors)

Priorities:

- **P0 (demo freeze):** replace `mobile-pwa.png` and
  `ai-screenshot-review-result.png` with true mobile-viewport captures;
  optional Alpaca Paper Order Preview capture
- **P1 (after freeze, MOBILE-PWA-POLISH-002):** collapse/reduce sticky mobile
  header (~28–35% of viewport while scrolling); make quick-action cards
  anchor-scroll or restyle as non-interactive; restyle inert
  `mobile-static-chip` pills as demo placeholders; clarify "PWA" wording or
  add a minimal service worker later
- **P2 (later):** raise smallest mobile text to ≥12px; custom upload control
  for consistent English screenshot labels

The P1/P2 items are not demo-freeze blockers.

## 10. Safety posture (unchanged by this milestone)

All README/showcase work must preserve and visibly communicate:

- autotrade=false · dry_run=true · read_only=true · live_orders_blocked=true
- execution_enabled=false · paper_only=true · requires_human_review=true
- max risk ≤ 1%
- no live trading, no broker execution, no real-money trading
- no buy/sell/order/execute controls
- no financial advice, no profit guarantees
- no secrets, provider keys, account IDs, or broker order IDs
