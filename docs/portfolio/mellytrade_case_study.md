# MellyTrade — Technical Case Study

> Portfolio / demo project. Read-only and demo-safe. Not a live trading
> system, not investment advice, no profit claims.

## 1. Project title

MellyTrade — a safety-first, read-only AI trading terminal and portfolio risk
platform (portfolio project).

## 2. One-sentence summary

A hosted, read-only fintech demo that demonstrates safety-first backend
architecture, AI-assisted engineering, and disciplined PR-based delivery — a
trading-domain system designed so that it provably cannot place a trade.

## 3. Project background

Built as a learning and portfolio project to demonstrate full-stack fintech
engineering with a safety-first mindset. The goal was not to trade, but to
show how a trading-adjacent system can be architected so its guardrails are
enforced and observable rather than merely promised.

## 4. Architecture overview

- **Backend:** Python · FastAPI · Pydantic. Trading surfaces are GET-only; an
  OpenAPI test asserts the memory routes stay `{get}`.
- **Frontend:** React · TypeScript · Vite, with a read-only safety rail; plus
  a mobile route and a Tauri v2 desktop shell on the same backend.
- **Data layer:** read-only Neon/ACE memory introspection with a SQL guard
  and `SET TRANSACTION READ ONLY`; degrades safely when the driver or
  database is unavailable.
- **Hosting:** Render (API) + Vercel (web), CORS scoped to documented origins.

## 5. Safety-first constraints

Enforced simultaneously in config, backend, UI, and tests:

```text
autotrade=false · dry_run=true · read_only=true
live_orders_blocked=true · execution_enabled=false
max_risk_per_trade <= 1% · human_review=required
```

No buy/sell/order/execute controls exist on any surface; no code path can
reach a real broker.

## 6. Backend / API evidence

Live GET-only smoke (2026-06-13, main `a2754ac`):
`GET /api/health` → 200, `GET /api/safety/status` → 200 (all flags + safety
pillars), `GET /api/neon-memory/status` → 200 in safe degraded read-only mode.
No secrets in any response. Full record:
[demo_evidence_pack_001.md](../demo/demo_evidence_pack_001.md).

## 7. Frontend / demo evidence

Hosted frontend `/` → 200 and the `/terminal` SPA deep link → 200. The UI
shows the read-only safety rail and degraded/fallback states honestly.

## 8. Deployment story

The hosted backend went stale when Render could not clone the repo (a GitHub
access blocker). The issue was diagnosed **from public endpoints alone** (a
missing route proved the deployed build was old), then resolved with one
user-approved manual deploy and verified by re-running the smoke — the Neon
route flipped 404 → 200 in safe degraded mode. Recorded in
[render_current_status.md](../deployment/render_current_status.md).

## 9. Validation and CI story

`scripts/validate_safety_config.py` plus a pytest safety-invariants suite gate
every change locally; CI runs quality (black/flake8/mypy), tests, build,
Playwright e2e, Bandit SAST, secret scanning, and a dependency audit. All
required checks were green before each merge in the recent arc.

## 10. Challenges solved

- Designing trading-domain APIs that are safe by construction (GET-only,
  read-only transactions, blocked execution)
- Graceful degradation: keeping the backend bootable and read-only when an
  optional driver/database is absent
- Real deployment debugging without dashboard access — diagnosing a stale
  build from public signals
- Maintaining scope discipline across a long multi-PR arc with review gates

## 11. What this project proves

Backend engineering (FastAPI/Pydantic), frontend integration, deployment and
ops debugging, CI/safety-validation discipline, risk-first product design,
documentation maturity, and a repeatable AI-assisted engineering workflow.

## 12. Limitations and honest caveats

- It is a demo / portfolio project, not a regulated or production trading
  platform.
- Real broker execution is intentionally blocked at every layer.
- The Neon memory database is intentionally not connected (safe degraded mode)
  — connecting a production DB would be a separate, gated task.
- Several integrations run in fallback mode because optional API keys are not
  configured.
- No claims of profit, ROI, win-rate, returns, or user adoption are made.

## 13. Future roadmap

Mobile/PWA evidence refresh, desktop/Tauri evidence pack, repo hygiene
cleanup, and optional agent-lessons backfill. Any move toward live data or a
connected database would be explicitly gated and out of scope for the demo.
