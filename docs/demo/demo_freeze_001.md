# MellyTrade Demo Freeze 001

## 1. Freeze status

- **Date:** 2026-06-12
- **Main SHA at freeze:** `c9b303edb321a83e7e7158d4c0c0d65ca7f60578`
- **Status:** Demo-ready · read-only · safe-degraded where noted
- **What this is:** an official demo checkpoint — a documented, verifiable
  state that can be shown to recruiters, clients, and technical reviewers.
- **What this is not:** a production trading system. Nothing here places
  trades, connects live broker credentials, or promises returns.

Companion docs: [demo_freeze_001_checklist.md](demo_freeze_001_checklist.md) ·
[demo_freeze_001_recruiter_script.md](demo_freeze_001_recruiter_script.md)

## 2. Product summary

MellyTrade is a **read-only AI trading terminal and portfolio risk platform**.
It shows market, portfolio, and safety information, AI workspace concepts,
paper/sandbox previews, audit/event posture, and live hosted-backend safety
status. It exists to demonstrate fintech architecture, AI-assisted
engineering workflows, safety-first trading-system design, and disciplined
delivery through reviewed GitHub PRs.

It is deliberately **not** a live trading system, not an auto-trading
platform, and makes no profit claims of any kind.

## 3. Live surfaces

All URLs below are the ones documented in `README.md` and
`docs/deployment/` — nothing invented:

| Surface | Where | State at freeze |
| --- | --- | --- |
| Hosted backend (FastAPI) | `https://alpha-data-scraper-ai.onrender.com` | ✅ serving current main (verified 2026-06-12) |
| Hosted frontend (web/PWA) | `https://alpha-data-scraper-ai.vercel.app` (+ `/terminal`, `/mobile`, `/brokers`) | ✅ live |
| GitHub repository | `github.com/Melly-999/alpha_data_scraper_ai` | ✅ portfolio-grade README, full PR trail |
| Terminal / portfolio / AI workspace / paper sandbox / audit surfaces | frontend routes above | ✅ read-only demo mode with safety badges |
| Neon/ACE memory route | `GET /api/neon-memory/status` | ✅ **safe degraded read-only** (by design — see caveats) |
| Safety endpoints | `GET /api/health`, `GET /api/safety/status` | ✅ live with correct flags |
| Desktop (Tauri) shell | `frontend/src-tauri/` (PR #271) | ✅ merged, demo-level |

## 4. Backend smoke evidence (GET-only, public, 2026-06-12)

| Endpoint | Status | Key flags | What it proves | Caveat |
| --- | --- | --- | --- | --- |
| `/api/health` | 200 | `safety.dry_run=true`, `auto_trade=false`, `max_risk_per_trade=1.0`, `fallback_mode=true` | Backend alive, safety config embedded in the payload | `fallback_mode` is expected — optional API keys (MT5/Claude/news) are deliberately not configured |
| `/api/safety/status` | 200 | `dry_run · read_only · live_orders_blocked = true`, `auto_trade=false`, `max_risk_per_trade_pct=1.0`, 5 safety pillars | Machine-readable safety invariants served live | none |
| `/api/neon-memory/status` | 200 | all 7 safety flags correct; `availability="degraded"`, `source="unconfigured"` | The memory subsystem **degrades safely** when its database is unavailable — graceful-degradation design working in production | degraded **by design**: `DATABASE_URL` is intentionally unset on Render |

CORS `Access-Control-Allow-Origin` correctly echoes the Vercel frontend on
all three endpoints. The Neon route's earlier 404 → 200 flip is the
content-level proof the deployed build includes PRs #286/#293.

**On the degraded Neon route:** this is a feature being demonstrated, not a
bug being excused. The route proves the backend stays healthy and read-only
when an optional dependency is missing — exactly the behavior a reviewer
should want to see in a safety-first system.

## 5. Safety posture

| Flag | Expected | Meaning |
| --- | --- | --- |
| `autotrade` / `auto_trade` | `false` | No automated trading, ever, on this demo |
| `dry_run` | `true` | All trading logic runs in simulation only |
| `read_only` | `true` | No mutation paths on demo surfaces |
| `live_orders_blocked` | `true` | No code path can reach a real broker |
| max risk per trade | `<= 1%` | Risk cap enforced in config and asserted by tests |
| `execution_enabled` | `false` (where applicable) | Execution surfaces disabled by contract |
| `requires_human_review` | `true` (where applicable) | Every workflow assumes a human decision-maker |

This demo is intentionally read-only and advisory. **It does not place
trades.** The posture is enforced simultaneously in config
(`config.json`), backend responses, UI badges, the safety validator
(`scripts/validate_safety_config.py`), and the pytest safety regression
suite.

## 6. Evidence trail (key PRs)

| PR | What it proves |
| --- | --- |
| #284–#290 | Brand/showcase/README chain: locked visual identity, SVG/PNG asset pipeline, favicon/PWA wiring, branded portfolio-grade README |
| #291 | Fable 5 agent operating contract: codified safe AI-assisted engineering (review gates, honesty rules, lessons memory) |
| #286 | Neon/ACE read-only memory introspection: GET-only routes, SQL guard, read-only transactions |
| #293 | Neon/ACE hardening: restored repo hygiene files, graceful psycopg degradation, placeholder identifiers, +5 tests |
| #294 | Roadmap status baseline after cleanup |
| #295 | Render current-status record: hosted backend verified current after one approved manual deploy |

Each merged through Draft PR → review gate → validation → squash merge — the
process itself is part of the portfolio story.

## 7. What to show in a demo (suggested flow)

1. Open the GitHub repo — the branded README is the landing page.
2. Walk the **Product Snapshot** table (type, status, safety posture, stack).
3. Open the hosted frontend (`/terminal`) — institutional dashboard with the
   READ ONLY / DRY RUN / LIVE ORDERS BLOCKED safety rail.
4. Show portfolio/brokers/mobile surfaces as desired — all read-only.
5. Open `/api/health` — live safety config in the payload.
6. Open `/api/safety/status` — the five safety pillars, machine-readable.
7. Open `/api/neon-memory/status` — explain degraded-by-design.
8. Explain the safety posture (section 5 above) in one breath.
9. Explain the engineering process: small scoped PRs, Fable review gates,
   validators, CI, docs — point at the PR trail.
10. Close with the roadmap: demo freeze → evidence pack → recruiter/public
    launch.

## 8. What not to show / not to claim

- Do **not** claim live trading, broker execution, or production readiness.
- Do **not** claim real user adoption, profit, win-rate, or ROI.
- Do **not** show env vars, secrets, Render/Vercel dashboards, or tokens.
- Do **not** connect real broker credentials for any demo.
- Do **not** connect `DATABASE_URL` just to make the Neon route show
  "connected" — degraded mode is the demo.
- Do **not** click any buy/sell/order/execute control if one ever appears —
  none should exist, and finding one is a bug to report, not a feature to
  demo.

## 9. Known caveats (state them honestly)

- The Neon memory route is intentionally degraded (`DATABASE_URL` unset).
- Several integrations run in fallback mode because optional API keys are
  deliberately not configured on the public demo (MT5, Claude, news).
- Render free tier cold-starts: the first request after idle may take
  ~30–60 s.
- This is a portfolio/demo system, not a regulated trading platform.
- Mobile/PWA evidence may still need a refresh pass (M7 in the roadmap).
- The desktop/Tauri demo is merged and smoke-tested but its local evidence
  pack can be polished later.
- Some stale PRs/branches remain for future hygiene cleanup (M4 leftovers).

## 10. Demo-ready definition

This checkpoint counts as demo-ready because all of the following are true:

- the public backend responds (`/api/health` 200)
- the safety endpoint responds with correct flags (`/api/safety/status` 200)
- the Neon route responds in safe degraded read-only mode (200)
- the docs explain every caveat honestly (this file)
- **no secrets are required anywhere** in the demo path
- no live execution exists on any surface
- the GitHub PR trail proves the engineering work end-to-end

## 11. Next recommended tasks

1. **DEMO-EVIDENCE-PACK-001** — capture screenshots/evidence of the frozen state
2. **MOBILE-PWA-EVIDENCE-REFRESH-001** — iPad/PWA evidence refresh (M7)
3. **DESKTOP-EXE-EVIDENCE-PACK-001** — land the desktop evidence docs
4. **RECRUITER-PORTFOLIO-PACK-001** — final recruiter-facing pack
5. **STALE-PR-CLOSEOUT-001** — decide PRs #283 / #18 / #17 / #12 / #10 / #7
6. **FABLE-LESSONS-BACKFILL-001** — write the first `docs/knowledge/fable_lessons/` entries
