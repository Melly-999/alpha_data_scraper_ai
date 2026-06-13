# Mobile / PWA Evidence Refresh 001

SOURCE STATUS: Public-safe documentation. Read-only GET-only smoke evidence and
manual checklists. No private data, no secrets, no account IDs, no broker
credentials.

## 1. Purpose

Refresh the mobile / PWA demo-readiness evidence for MellyTrade against the
current hosted surfaces, consolidating the existing mobile/PWA docs into one
current snapshot. Documentation-only: this task changes no runtime, frontend,
backend, config, or deployment behaviour. It records what is observable today
via safe GET-only checks plus manual checklists for device review.

This refresh complements — and does not replace — the existing evidence:

- [demo_009_ipad_pwa_smoke_evidence.md](demo_009_ipad_pwa_smoke_evidence.md) and [demo_009_ipad_pwa_screenshot_checklist.md](demo_009_ipad_pwa_screenshot_checklist.md)
- [../devices/ipad_pwa_smoke_test.md](../devices/ipad_pwa_smoke_test.md), [../devices/mobile_app_ios_smoke_checklist.md](../devices/mobile_app_ios_smoke_checklist.md)
- [../deployment/hosted_mobile_demo_smoke_checklist.md](../deployment/hosted_mobile_demo_smoke_checklist.md), [../deployment/vercel_mobile_frontend_runbook.md](../deployment/vercel_mobile_frontend_runbook.md)
- [../showcase/ipad_pwa_paper_run_preview.md](../showcase/ipad_pwa_paper_run_preview.md)

## 2. Current milestone status

- M4 Repo hygiene / stale-PR arc — **DONE**
- M5 Render hosted backend — **DONE**
- M8 Demo / portfolio pack — **DONE**
- M8.5 Public launch readiness (PR #300) — **DONE**
- **M7 Mobile / PWA evidence — refreshed by this doc** (hosted GET-only smoke verified)

## 3. Hosted surfaces

| Surface | URL |
|---|---|
| Web demo (Vercel) | <https://alpha-data-scraper-ai.vercel.app> |
| Terminal route | <https://alpha-data-scraper-ai.vercel.app/terminal> |
| PWA manifest | <https://alpha-data-scraper-ai.vercel.app/manifest.webmanifest> |
| Backend health (Render) | <https://alpha-data-scraper-ai.onrender.com/api/health> |
| Backend safety status (Render) | <https://alpha-data-scraper-ai.onrender.com/api/safety/status> |

## 4. Mobile / PWA readiness summary

- The hosted frontend serves on mobile viewports and exposes a web app manifest
  with `"display": "standalone"`, enabling Add-to-Home-Screen / installable PWA
  behaviour on supported browsers.
- The terminal route loads over HTTPS and the manifest declares app name, theme
  colours and icon set (128/256 px).
- The hosted backend is healthy and reports the read-only / dry-run safety
  posture on a dedicated status endpoint.
- This is a **demo-ready, portfolio-ready** mobile/PWA surface — not an
  app-store build and not a guaranteed install on every device/browser.

## 5. GET-only smoke evidence

Performed `2026-06-13` from a developer workstation using read-only HTTP GET
requests. No POST/PUT/PATCH/DELETE, no broker credentials, no order paths.

| Check | Method | Result |
|---|---|---|
| Frontend root | GET `/` | HTTP 200 |
| Terminal route | GET `/terminal` | HTTP 200 |
| PWA manifest | GET `/manifest.webmanifest` | HTTP 200 (`display: standalone`) |
| Backend health | GET `/api/health` | HTTP 200 (`status: ok`, `dry_run: true`, `auto_trade: false`, `fallback_mode: true`) |
| Backend safety status | GET `/api/safety/status` | HTTP 200 (see posture below) |
| Backend safety config | GET `/api/safety/config` | HTTP 404 (endpoint not exposed on this surface) |

Safety status payload (key fields, verbatim from the live response):

```json
{
  "dry_run": true,
  "auto_trade": false,
  "read_only": true,
  "live_orders_blocked": true,
  "max_risk_per_trade_pct": 1.0,
  "pillars": ["DRY_RUN_ACTIVE","READ_ONLY_ACTIVE","AUTO_TRADE_DISABLED","LIVE_ORDERS_BLOCKED","MAX_RISK_CAPPED"]
}
```

The live `safety_note` states the surface is read-only / dry-run, live orders are
blocked, autotrade is disabled, per-trade risk is capped at 1%, and no code path
on this surface can submit an order to a real broker.

## 6. Manual iPhone / iPad smoke checklist

Run on a real device against the hosted frontend. (See the device-specific
templates in [../devices/](../devices/) for fuller per-device variants.)

- [ ] Hosted web demo loads on iPhone Safari
- [ ] Hosted web demo loads on iPad Safari
- [ ] Terminal / workspace view renders without layout breakage
- [ ] Text / number inputs and selects do not trigger zoom on focus
- [ ] Safety chips visible: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF`, `HUMAN REVIEW REQUIRED`
- [ ] No `Buy` / `Sell` / `Execute` / `Place Order` controls anywhere
- [ ] No broker connect / credential prompts
- [ ] "Analysis only. Not financial advice." disclaimer is present

## 7. Installability checklist

- [ ] `/manifest.webmanifest` loads (HTTP 200) — verified GET-only on 2026-06-13
- [ ] Manifest declares `display: standalone`
- [ ] App name / short name present (`MellyTrade Terminal` / `MellyTrade`)
- [ ] Icons resolve (128 / 256 px)
- [ ] iOS Safari: "Add to Home Screen" creates an installed shell
- [ ] Launched standalone shell opens the terminal in full-screen (no browser chrome)
- [ ] Standalone shell still shows the read-only safety chips

## 8. Safety posture

Confirmed unchanged and live-verified via `/api/safety/status` and `/api/health`:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max_risk_per_trade <= 1%
no broker execution
no live trading UX
```

## 9. What not to claim

- Do not claim real users or adoption — this is a portfolio demo
- Do not claim live trading, broker execution, or autonomous order placement
- Do not claim production trading readiness
- Do not claim guaranteed installability on all devices/browsers
- Do not claim app-store readiness or a published native app
- Do not claim profit, returns, ROI, win-rate, or passive income
- Do not claim financial advice or a regulated financial product

## 10. Known limitations

- Live smoke here is HTTP-status + payload level only; full visual/interaction
  verification still requires the manual device checklists in §6–§7.
- Render free-tier may cold-start; a first request can be slow — re-check before
  any demo.
- `/api/safety/config` is not exposed on this surface (404); the authoritative
  live posture is `/api/safety/status`.
- PWA install behaviour varies by browser/OS; iOS Safari Add-to-Home-Screen is
  the documented happy path.

## 11. Next steps

1. Run the §6 / §7 manual checklists on a physical iPhone and iPad and record
   results in the [../devices/](../devices/) result templates.
2. Optionally refresh the public-demo mobile screenshot
   (`docs/assets/screenshots/public-demo/mobile-pwa.png`) if the UI has changed.
3. Keep this doc's GET-only evidence current after any hosted redeploy.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
