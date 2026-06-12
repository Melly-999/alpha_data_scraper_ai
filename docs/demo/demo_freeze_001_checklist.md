# Demo Freeze 001 — Pre-Demo Checklist

Practical checklist before showing MellyTrade live. Companion to
[demo_freeze_001.md](demo_freeze_001.md).

## Before demo

- [ ] Open the GitHub README — confirm the banner and Product Snapshot render
- [ ] Open the hosted frontend (`/terminal`) — confirm it loads with the
      safety rail visible (Render/Vercel cold start: open it a few minutes
      early)
- [ ] Open `GET /api/health` — confirm HTTP 200
- [ ] Open `GET /api/safety/status` — confirm HTTP 200 and:
      `dry_run=true`, `read_only=true`, `live_orders_blocked=true`,
      `auto_trade=false`, `max_risk_per_trade_pct=1.0`
- [ ] Open `GET /api/neon-memory/status` — confirm HTTP 200 with
      `availability="degraded"`, `mode="read-only"` (this is correct)
- [ ] Verify no secrets are visible anywhere you plan to show
- [ ] Have the 30-second and 2-minute scripts ready
      ([demo_freeze_001_recruiter_script.md](demo_freeze_001_recruiter_script.md))

## During demo

- [ ] Start with the product summary (one sentence, then the snapshot table)
- [ ] Show GitHub/README — the brand, the safety contract, the PR trail
- [ ] Show the live backend safety endpoints
- [ ] Show the UI surfaces (terminal → brokers → mobile as time allows)
- [ ] Explain the read-only posture early and confidently
- [ ] Explain degraded Neon as **safe design**, not a failure: "this is what
      the system does when an optional database is absent — it stays healthy
      and read-only"
- [ ] Explain what was built and why: safety-first architecture, AI-assisted
      workflow with review gates, docs discipline

## Do not do

- ✋ Do not open `.env` or any environment file
- ✋ Do not show Render/Vercel dashboards or env var pages
- ✋ Do not show GitHub repository secrets/settings
- ✋ Do not click deploy on anything
- ✋ Do not change any setting live
- ✋ Do not claim trading execution exists
- ✋ Do not promise returns, win rates, or performance

## Red flags — stop and investigate before/instead of demoing

- 🚩 `/api/safety/status` is not HTTP 200
- 🚩 `dry_run` is not `true`
- 🚩 `live_orders_blocked` is not `true`
- 🚩 any endpoint response contains anything secret-shaped
- 🚩 a dashboard with env vars is visible on screen
- 🚩 the frontend shows any buy/sell/order/execute control (none should
      exist — this would be a regression to report immediately)

## If something fails mid-demo

- Stay calm and name it: "that surface is in fallback mode — by design the
  system degrades instead of breaking"
- Do **not** debug live in front of a recruiter/client
- Fall back to the GitHub docs and the evidence trail — the PR history and
  freeze doc tell the story without a live system
- Note what failed and create a follow-up task afterwards
