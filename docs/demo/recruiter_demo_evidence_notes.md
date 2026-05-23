# Recruiter Demo Evidence Notes

Date/time: 2026-05-23 18:31-18:32 Europe/Warsaw

Local repo SHA: `5f71309c411eabce2e72651d14331305429df590`

Screenshot folder outside repo:

`C:\AI\MellyTrade_Workspace\screenshots\recruiter-demo-pack\20260523-183134`

## What Was Tested

- Local backend startup in safe read-only/dry-run mode.
- Local Vite frontend startup pointed at the local backend.
- Recruiter screenshot routes from `docs/demo/recruiter_screenshot_checklist.md`.
- Public-safe README/architecture evidence preview.
- Visible safety posture and absence of live trading UX.

## Startup Summary

Backend:

- URL: `http://127.0.0.1:8001`
- Command used: `powershell -ExecutionPolicy Bypass -File scripts/start_backend_local.ps1 -Port 8001`
- Startup banner confirmed read-only/dry-run posture.
- Confirmed safety posture included `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, and max risk cap <= 1%.

Frontend:

- URL: `http://127.0.0.1:5173`
- Command used: `powershell -ExecutionPolicy Bypass -File scripts/start_frontend_local.ps1 -BackendPort 8001 -FrontendPort 5173`
- Frontend startup banner confirmed no execution buttons and no order routes.
- Vite served the UI successfully.

## Routes Smoked

| Route | Result | Notes |
|---|---:|---|
| `/` | 200 | Rendered terminal shell. |
| `/terminal` | 200 | Rendered main terminal overview. |
| `/workspace` | 200 | Rendered AI Workspace. |
| `/signals` | 200 | Rendered signal quality view. |
| `/risk` | 200 | Rendered risk manager view. |
| `/brokers` | 200 | Rendered broker read-only state. |
| `/audit` | 200 | Rendered audit/events feed. |
| `/portfolio` | 200 | Rendered paper/read-only portfolio view. |

Additional backend API smoke:

- `/api/health`: 200
- `/api/terminal/summary`: 200
- `/api/market/overview`: 200
- `/api/risk/policy`: 200
- `/api/terminal/events`: 200

The guessed endpoint `/api/brokers/ibkr/status` returned 404 and was not used as evidence. Broker safety evidence was verified through the frontend `/brokers` view.

## Degraded / Fallback States

- Backend startup reported safe degraded/fallback states for unavailable optional services.
- Supabase/audit writer was unavailable in local mode, but startup continued safely.
- Broker surfaces displayed safe degraded/read-only states instead of live broker connectivity.
- The `/risk` screenshot showed some degraded `undefined` values inside risk cards; global safety badges and `execution_enabled=false` were still visible. Treat this as a future UI polish item.

## Privacy Scan Result

Screenshots were visually reviewed. No screenshot contained:

- private email
- phone number
- full address
- API key, token, password, or private key
- private broker account ID
- real balance or account value
- private CV data
- desktop notifications
- browser bookmarks with personal information

The initial GitHub README screenshot was rejected because it showed a public 404/sign-in page instead of useful project evidence. The final README evidence was retaken as a local rendered preview outside the repository with public-safe content only.

## Safety Scan Result

- No order buttons were found.
- No buy/sell/execute/place-order controls were found.
- No connect-live UX was found.
- No broker execution was used.
- No live trading was used.
- Safety badges were visible across the recruiter screenshot set: READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, and HUMAN REVIEW where present.

## Recommended Next Step

Record the recruiter Loom using `docs/demo/recruiter_loom_demo_script.md` and reference the screenshots from the outside-repo screenshot folder. Keep binary screenshots outside the repository unless a future task explicitly asks for a curated, redacted asset pack.

## Loom Evidence Status

- Loom recording: not recorded yet.
- Planned script: `docs/demo/recruiter_loom_demo_script.md`.
- Recording checklist: `docs/demo/recruiter_loom_evidence_checklist.md`.
- Video files should stay outside the repository.
- Only a public-safe Loom link may be added to repo docs later after manual privacy and safety review.
