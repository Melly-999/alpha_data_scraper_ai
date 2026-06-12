# Render Hosted Backend — Current Status

- **Last updated:** 2026-06-12
- **Status:** ✅ **UNBLOCKED / CURRENT** — the hosted backend serves current
  `main` (includes the Neon/ACE routes from PRs #286 + #293)
- **Task trail:** RENDER-DEPLOY-UNBLOCK-001 (read-only verification) →
  RENDER-DASHBOARD-ACCESS-CHECK-AND-DEPLOY-SMOKE-001 (human-guided deploy)

---

## 1. What changed

The previous stale-container condition is resolved. Render's GitHub repository
access was confirmed healthy in both dashboards (Render service page: correct
repo `Melly-999/alpha_data_scraper_ai` @ `main`, no clone error, Manual Deploy
available; GitHub → Installed GitHub Apps → Render: installed with repository
access, no warnings). With explicit user approval, the user triggered exactly
**one** `Manual Deploy → Deploy latest commit`. No environment variables,
build/start commands, or cloud settings were changed by anyone, and no repo
files were modified during the deploy.

A public poller observed the new build go live within ~3 minutes.

## 2. Post-deploy smoke evidence (GET-only, public endpoints)

| Endpoint | HTTP | Key observations |
| --- | --- | --- |
| `/api/health` | 200 | `safety.dry_run=true`, `auto_trade=false`, `max_risk_per_trade=1.0`, `fallback_mode=true` (expected — no optional API keys configured) |
| `/api/safety/status` | 200 | `dry_run=true · read_only=true · live_orders_blocked=true · auto_trade=false · max_risk_per_trade_pct=1.0`, all five safety pillars present |
| `/api/neon-memory/status` | 200 | `availability="degraded"`, `source="unconfigured"`, message states `DATABASE_URL` is not set and routes stay read-only; identifiers are placeholders (`example-project` / `example-workspace`); all seven safety flags correct; **no secrets in the response** |

CORS: `Access-Control-Allow-Origin` correctly echoes the Vercel frontend
origin on all three endpoints.

The `/api/neon-memory/status` flip from 404 → 200 is the content-level proof
that the deployed build is at or after `1ecd14f` (PR #293), i.e. effectively
current `main`.

## 3. Important caveat — Neon is intentionally unconfigured on Render

- `DATABASE_URL` is **deliberately not set** on the Render service. The Neon
  routes therefore answer in **safe degraded read-only mode** — this is the
  designed behavior, **not a failure**.
- **Do not add `DATABASE_URL` or any secret to Render just for demo freeze.**
  The public demo requires no secrets at all.
- Connecting a production database is out of scope unless a separate,
  explicitly approved task exists.

## 4. Historical blocker (superseded)

An earlier Render deploy failed **before build at repository clone**
(`fatal: could not read Username for 'https://github.com'` /
"It looks like we don't have access to your repo") — an external
GitHub-account / GitHub-App access restriction, recorded at the time on the
unmerged branch `docs/render-github-access-blocker`. That blocker left an old
container serving while newer `main` commits never deployed.

The access restriction **appears resolved**: the dashboard check found no
clone error and the approved manual deploy succeeded end-to-end. The old
blocker doc/branch should be treated as **historical/superseded** unless new
evidence says otherwise.

## 5. Safety

- No live trading, no broker execution, no order/buy/sell/execute controls —
  posture verified directly on the live API: `autotrade=false`,
  `dry_run=true`, `read_only=true`, `live_orders_blocked=true`,
  max risk ≤ 1%.
- Verification used GET requests only against publicly documented endpoints;
  no secrets were exposed, requested, or configured.

## 6. Roadmap impact

- **M5 Render / Hosted Backend Deploy Unblock → DONE**
- **M8 Demo Freeze / Recruiter Pack → NEXT** (no longer gated on M5)
- M7 Mobile/PWA Evidence remains IN PROGRESS
- M4 Repo Hygiene remains IN PROGRESS / MOSTLY DONE

**Recommended next task:** `DEMO-FREEZE-001`.
