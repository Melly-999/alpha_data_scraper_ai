# DEMO-008 — Post-SIG-004B Signal Quality UI Evidence

## Purpose

This document is a docs-only evidence summary for the Signal Quality
Summary UI smoke audit completed after PR #176 merged SIG-004B. It records
the endpoint, browser, UI, and safety checks used to verify the read-only
Signal Quality card after the backend SIG-004 API and frontend SIG-004B
card were merged.

## Evidence source

| Item | Value |
|---|---|
| Repo SHA | `f1b5ab23e9d7fe9d7021cc1cf668a0aac2773150` |
| PR | `#176` merged: `feat(frontend): add signal quality summary card (SIG-004B)` |
| Direct backend URL | `http://127.0.0.1:8026` |
| Vite proxy backend URL | `http://127.0.0.1:8001` |
| Frontend URL | `http://127.0.0.1:5173` |
| Smoke worktree | `C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai-post-sig-004b-smoke` |
| Screenshot folder | `C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui` |
| Manifest | `C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui\manifest.md` |

Screenshots are stored outside the repository and are intentionally not
committed as binary assets.

## What was verified

- Direct backend smoke against `http://127.0.0.1:8026`.
- Vite proxy smoke through `http://127.0.0.1:8001`.
- Browser route smoke for dashboard, workspace, terminal, signals, audit,
  brokers, and portfolio routes.
- Signal Quality Summary card content on `/workspace` and `/terminal`.
- Console and network checks for API errors, browser runtime errors, and
  component crashes.
- Cleanliness checks confirming no files were edited in the isolated smoke
  worktree, the canonical dirty repo was unchanged, the original Desktop
  repo was untouched, no commits or PRs were created during the smoke, and
  screenshots remained outside the repository.

## Endpoint smoke summary

| Endpoint | Expected | Result |
|---|---|---|
| `/api/signals/quality/summary` | `GET 200` | Passed |
| `/api/signals/quality/summary` | `POST 405` | Passed |
| `/api/terminal/summary` | `GET 200` | Passed |
| `/api/market/overview` | `GET 200` | Passed |
| `/api/watchlist` | `GET 200` | Passed |
| `/api/risk/policy` | `GET 200` | Passed |
| `/api/news/sentiment` | `GET 200` | Passed |
| `/api/signals/scanner/preview` | `GET 200` | Passed |
| `/api/signals/scanner/universes` | `GET 200` | Passed |

## Browser route smoke summary

| Route | Rendered | Blank page | Overflow | Errors | Network failures |
|---|---|---|---|---|---|
| `/` | Yes | No | No | No | No |
| `/workspace` | Yes | No | No | No | No |
| `/terminal` | Yes | No | No | No | No |
| `/signals` | Yes | No | No | No | No |
| `/audit` | Yes | No | No | No | No |
| `/brokers` | Yes | No | No | No | No |
| `/portfolio` | Yes | No | No | No | No |

Console and network checks found 0 API 404s, 0 API 500s, 0 network
failures, 0 TypeErrors, 0 ReferenceErrors, and 0 component crashes. The
only observed console messages were expected React Router future-flag
warnings.

## Signal Quality card values

| Field | Value |
|---|---|
| Total signals | `6` |
| Average confidence | `61.8%` |
| Quality label | `MODERATE` |
| Confidence band | `MEDIUM` |
| Freshness | `LIVE` |
| Risk posture | `BLOCKED` |
| Execution mode | `DRY RUN ONLY` |
| Quality score | `61.8` |
| Chips | `READ ONLY`, `DRY RUN`, `RISK BLOCKED`, `HUMAN REVIEW`, `DRY RUN ONLY` |

## Screenshot inventory

Primary screenshots:

- `01_dashboard_post_sig_004b_1366x768.png`
- `02_workspace_signal_quality_card_1366x768.png`
- `03_terminal_signal_quality_card_1366x768.png`
- `04_signals_post_sig_004b_1366x768.png`
- `05_audit_post_sig_004b_1366x768.png`
- `06_brokers_post_sig_004b_1366x768.png`
- `07_portfolio_post_sig_004b_1366x768.png`

Supplementary screenshots:

- `01b_dashboard_fullpage.png`
- `02_signal_quality_card_visible_1366x768.png`
- `02b_workspace_fullpage.png`
- `02c_workspace_scrolled.png`
- `03_signal_quality_card_visible_1366x768.png`
- `03b_terminal_fullpage.png`
- `03c_terminal_scrolled.png`

## Safety confirmation

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- max risk `<=1%`
- No order, buy, sell, or execute controls found.
- No broker execution controls found.
- No live trading UX found.
- No external API calls added.
- No profit guarantees or trade recommendations found.

## Notes for reviewers

- Evidence screenshots are intentionally outside the repository.
- The canonical dirty repo was not used for edits.
- A docs-only PR for this evidence should not include runtime files.
- This document is a portfolio/demo evidence index, not a trading
  recommendation.
