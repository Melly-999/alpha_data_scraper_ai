# DEMO-008 — Post-SIG-004B Signal Quality UI Evidence

## Purpose

This document records the evidence from the POST-SIG-004B Signal Quality UI smoke recovery.

The goal is to provide a text-only, repository-safe evidence summary for the Signal Quality Summary card after PR #176 was merged.

This document is not a trading recommendation. It is a demo and QA evidence index for the read-only MellyTrade terminal.

## Evidence source

| Item | Value |
|---|---|
| Repo SHA | `f1b5ab23e9d7fe9d7021cc1cf668a0aac2773150` |
| Short SHA | `f1b5ab2` |
| PR | `#176` |
| PR status | `merged` |
| Feature | `feat(frontend): add signal quality summary card (SIG-004B)` |
| Smoke worktree | `C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai-post-sig-004b-smoke` |
| Direct backend URL | `http://127.0.0.1:8026` |
| Vite proxy backend URL | `http://127.0.0.1:8001` |
| Frontend URL | `http://127.0.0.1:5173` |
| Screenshot evidence folder | `C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui\` |
| Manifest | `C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui\manifest.md` |

Screenshots and manifest are intentionally stored outside the repository and are not committed.

## What was verified

The smoke recovery verified:

- direct backend endpoint behavior
- Vite proxy backend behavior
- browser route rendering at 1366x768
- Signal Quality Summary card content
- network and console health
- absence of execution controls
- repository cleanliness after the smoke

## Endpoint smoke summary

| Endpoint | Method | Expected | Result |
|---|---:|---:|---:|
| `/api/signals/quality/summary` | GET | 200 | 200 |
| `/api/signals/quality/summary` | POST | 405 | 405 |
| `/api/terminal/summary` | GET | 200 | 200 |
| `/api/market/overview` | GET | 200 | 200 |
| `/api/watchlist` | GET | 200 | 200 |
| `/api/risk/policy` | GET | 200 | 200 |
| `/api/news/sentiment` | GET | 200 | 200 |
| `/api/signals/scanner/preview` | GET | 200 | 200 |
| `/api/signals/scanner/universes` | GET | 200 | 200 |

All expected GET endpoints returned 200. POST to `/api/signals/quality/summary` returned 405 as expected.

## Browser route smoke summary

Viewport: `1366x768`

| Route | Rendered | Blank page | Crash | Horizontal overflow |
|---|---:|---:|---:|---:|
| `/` → `/terminal` | Yes | No | No | No |
| `/workspace` | Yes | No | No | No |
| `/terminal` | Yes | No | No | No |
| `/signals` | Yes | No | No | No |
| `/audit` | Yes | No | No | No |
| `/brokers` | Yes | No | No | No |
| `/portfolio` | Yes | No | No | No |

## Signal Quality card values

Verified on `/workspace`.

| Field | Value |
|---|---:|
| Card visible | Yes |
| Total signals | `6` |
| Average confidence | `61.8%` |
| Quality label | `MODERATE` |
| Confidence band | `MEDIUM` |
| Freshness | `LIVE` |
| Risk posture | `BLOCKED` |
| Execution mode | `DRY RUN ONLY` |
| High confidence | `2 / 6` |
| Quality score | `61.8` |

Safety chips visible:

- `READ ONLY`
- `DRY RUN`
- `RISK BLOCKED`
- `HUMAN REVIEW`
- `DRY RUN ONLY`

The card had no action buttons, no trade recommendation wording, and no profit guarantee wording.

## Console and network summary

| Check | Result |
|---|---|
| API 404s | `0` |
| API 500s | `0` |
| Network failures | `0` |
| TypeErrors | `0` |
| ReferenceErrors | `0` |
| Component crashes | `0` |
| Unhandled promise rejections | `0` |

Only expected React Router future-flag warnings were observed.

## Screenshot inventory

The following screenshots were saved outside the repository.

Primary screenshots:

- `01_dashboard_post_sig_004b_1366x768.png`
- `02_workspace_signal_quality_card_1366x768.png`
- `03_terminal_signal_quality_card_1366x768.png`
- `04_signals_post_sig_004b_1366x768.png`
- `05_audit_post_sig_004b_1366x768.png`
- `06_brokers_post_sig_004b_1366x768.png`
- `07_portfolio_post_sig_004b_1366x768.png`

Supplementary screenshots from the earlier recovery run:

- `01b_dashboard_fullpage.png`
- `02_signal_quality_card_visible_1366x768.png`
- `02b_workspace_fullpage.png`
- `02c_workspace_scrolled.png`
- `03_signal_quality_card_visible_1366x768.png`
- `03b_terminal_fullpage.png`
- `03c_terminal_scrolled.png`

These files must remain outside the repository unless a future task explicitly approves adding redacted media assets.

## Safety confirmation

| Safety property | Confirmed value |
|---|---:|
| `autotrade` | `false` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `max_risk_per_trade` | `<= 1%` |
| `execution_mode` | `dry_run_only` |
| `requires_human_review` | `true` |
| `risk_allowed` | `false` |

Additional safety checks:

- no order, buy, sell, execute, or place-order controls found
- no broker execution controls found
- no live trading UX found
- no external API calls added
- no profit guarantees found
- no trade recommendations found
- isolated smoke worktree remained clean
- canonical dirty repo remained unchanged
- original Desktop repo was not accessed

## Notes for reviewers

This is a docs-only evidence summary.

The evidence paths are local operator paths, not committed assets. They are included so a reviewer can locate the external screenshot bundle if they are working on the same machine.

This document does not claim live trading capability and does not provide financial advice or trade recommendations.
