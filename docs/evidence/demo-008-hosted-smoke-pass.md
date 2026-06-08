# Demo-008 — Hosted Demo Smoke: PASS

- **Date:** 2026-06-08
- **Branch:** `docs/demo-008-hosted-smoke-evidence`
- **Base:** `origin/main`
- **Base HEAD:** `6923995` (`6923995 feat(paper): add GET-only Alpaca Paper demo status endpoints`)
- **Result:** ✅ PASS (read-only hosted smoke)
- **Backend:** https://alpha-data-scraper-ai.onrender.com
- **Frontend:** https://alpha-data-scraper-ai.vercel.app

> Scope: read-only GET/browser smoke. No commits, pushes, deploys, environment
> changes, or runtime code changes were made while producing this evidence.

---

## Final PASS summary

- Backend `https://alpha-data-scraper-ai.onrender.com`: `/api/health` and
  `/api/safety/status` both return **200**.
- Frontend `https://alpha-data-scraper-ai.vercel.app` rebuilt: JS bundle hash
  changed from **`index-DHLYNIkv.js`** → **`index-dtctt1dK.js`**.
- Frontend now calls the **correct backend host** `alpha-data-scraper-ai.onrender.com`
  (19/19 API GETs → 200); **no** calls to `mellytrade-api-demo.onrender.com`.
- **CORS fixed** — responses include
  `access-control-allow-origin: https://alpha-data-scraper-ai.vercel.app`.
- `/`, `/terminal`, and `/mobile` render via in-app routing.
- **AI Screenshot Review passed:**
  - Valid PNG/JPEG/WebP → paper-only preview (XAUUSD · M15, `1% · PAPER_ONLY`,
    "Not stored").
  - SVG rejected — "Unsupported file type. Use a PNG, JPEG, or WebP image."
  - PDF rejected — "Unsupported file type. Use a PNG, JPEG, or WebP image."
  - Oversize (>5 MB) rejected — "File is too large. Maximum size is 5 MB."
  - Empty file rejected — "File is empty."
- **`provider_used: false`** confirmed in the
  `POST /api/mobile/ai/screenshot/preview` 200 response.
- **No order/buy/sell/execute controls.**
- **No provider-key UI.**
- **No broker controls.**
- **No console errors.**
- Safety posture preserved: dry-run, read-only, auto-trade off, live orders
  blocked, max risk per trade 1%.

---

## Checks performed

| # | Check | Result |
|---|-------|--------|
| 1 | `GET /api/health` | ✅ 200 (`dry_run:true`, `fallback_mode`) |
| 2 | `GET /api/safety/status` | ✅ 200 (5 pillars, `live_orders_blocked:true`) |
| 3 | Bundle hash changed from `index-DHLYNIkv.js` | ✅ now `index-dtctt1dK.js` |
| 4 | Frontend calls `alpha-data-scraper-ai.onrender.com` | ✅ 19/19 GETs → 200 |
| 5 | No calls to `mellytrade-api-demo.onrender.com` | ✅ none |
| 6 | No CORS errors | ✅ ACAO header present for the Vercel origin |
| 7 | `/` renders | ✅ (redirects to `/terminal`) |
| 8 | `/terminal` renders (in-app route) | ✅ |
| 9 | `/mobile` renders (in-app route) | ✅ |
| 10 | AI Screenshot Review visible | ✅ |
| 11 | Valid image → paper-only preview | ✅ |
| 12 | SVG rejected | ✅ |
| 13 | PDF rejected | ✅ |
| 14 | >5 MB rejected | ✅ |
| 15 | Empty rejected | ✅ |
| 16 | `provider_used:false` | ✅ |
| 17 | No order/buy/sell/execute controls | ✅ |
| 18 | No provider-key UI | ✅ |
| 19 | No broker controls | ✅ |
| 20 | No console errors | ✅ |
| 21 | Safety posture preserved | ✅ |

---

## Evidence screenshots (stored outside the repo)

> Screenshot image files are intentionally **not** committed to the repository.
> They are captured and stored outside the repo (reference-only). The list below
> defines the expected capture set for this smoke.

| # | Suggested name | Must show |
|---|----------------|-----------|
| 01 | `01-backend-health.png` | `GET /api/health` → 200 JSON (`dry_run:true`, `fallback_mode`) |
| 02 | `02-backend-safety-status.png` | `GET /api/safety/status` → 200, 5 pillars + `live_orders_blocked:true` |
| 03 | `03-frontend-terminal.png` | `/terminal` rendered, top safety badges |
| 04 | `04-network-correct-host.png` | API calls to `alpha-data-scraper-ai.onrender.com` all 200; bundle `index-dtctt1dK.js` |
| 05 | `05-console-clean.png` | Console empty (no CORS/errors); no `mellytrade-api-demo` requests |
| 06 | `06-mobile-screenshot-review-valid.png` | `/mobile` valid PNG paper-only preview ("1% · PAPER_ONLY", "Not stored") |
| 07 | `07-provider-used-false.png` | `POST /api/mobile/ai/screenshot/preview` 200 JSON with `provider_used:false` |
| 08 | `08-reject-svg-pdf.png` | "Unsupported file type. Use a PNG, JPEG, or WebP image." |
| 09 | `09-reject-oversize.png` | "File is too large. Maximum size is 5 MB." |
| 10 | `10-reject-empty.png` | "File is empty." |
| 11 | `11-safety-no-exec-controls.png` | Orders: Denied / Live execution: denied; no buy/sell/execute/broker/key controls |
| 12 | `12-b2-deeplink-404.png` | Vercel 404 on direct deep-load of `/terminal` or `/mobile` |

---

## B2 caveat (known, non-blocking)

Direct deep-links to client routes (`/terminal`, `/mobile`, and other non-root
routes) still return a **Vercel edge 404 (`NOT_FOUND`)**. Only `/` is served by
the host; all other routes render correctly **only via in-app client-side
navigation**. Root cause: the Vercel deployment is missing an SPA catch-all
rewrite (`/* → /index.html`).

Impact: does not affect the demo flow (entry via `/`), but breaks shared/
bookmarked deep links and refresh-on-route.

---

## Recommended next PR

**Add an SPA catch-all rewrite for Vercel** so all non-asset paths serve
`index.html`, letting the client router resolve deep links. Example `vercel.json`:

```json
{ "rewrites": [{ "source": "/((?!assets/|.*\\..*).*)", "destination": "/index.html" }] }
```

Then re-verify direct deep-loads of `/terminal` and `/mobile` return 200 and
render (re-run smoke item 12). Scope: hosting config only — no app-code or
backend change.
