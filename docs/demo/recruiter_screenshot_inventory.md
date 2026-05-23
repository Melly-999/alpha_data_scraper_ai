# Recruiter Screenshot Inventory

Date/time: 2026-05-23 18:31-18:32 Europe/Warsaw

Local repo SHA: `5f71309c411eabce2e72651d14331305429df590`

Screenshot folder outside repo:

`C:\AI\MellyTrade_Workspace\screenshots\recruiter-demo-pack\20260523-183134`

Screenshots are stored outside the repository and are not committed as binary assets.

## Inventory

| # | Filename | Route/page | Purpose for recruiter | Safety badges visible | Redaction status | Notes |
|---:|---|---|---|---|---|---|
| 1 | `01_terminal_overview.png` | `http://127.0.0.1:5173/terminal` | Shows the main institutional terminal shell, navigation, safety banner, AI workspace summary, and execution-denied sidebar. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, HUMAN REVIEW, Orders Denied, Live trade Blocked, Paper RO | No redaction required | Captured in degraded/fallback local mode; still clearly read-only and dry-run. |
| 2 | `02_ai_workspace.png` | `http://127.0.0.1:5173/workspace` | Shows AI Workspace positioning, supervised AI-assisted decision-support workflow, and dry-run advisory. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, HUMAN REVIEW | No redaction required | Useful for explaining AI-assisted engineering without claiming autonomous execution. |
| 3 | `03_signals_quality.png` | `http://127.0.0.1:5173/signals` | Shows signal quality, thesis/evidence view, and no-execution-control messaging. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, HUMAN REVIEW, Dry-run only, Risk gate visible, Broker execution denied | No redaction required | Screenshot reinforces analysis-only signal handling. |
| 4 | `04_risk_guardrails.png` | `http://127.0.0.1:5173/risk` | Shows risk manager view and execution-disabled posture. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, execution_enabled=false | No redaction required | Some risk card fields displayed degraded `undefined` values; treat as a future UI polish item, not a safety exception. |
| 5 | `05_broker_readonly_state.png` | `http://127.0.0.1:5173/brokers` | Shows broker state is read-only/degraded and execution is denied. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, execution_enabled=false, orders denied, live execution denied | No redaction required | No account numbers, balances, credentials, or live broker connection were visible. |
| 6 | `06_audit_events_feed.png` | `http://127.0.0.1:5173/audit` | Shows audit/event feed with safety events and startup posture evidence. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, read_only_mode_confirmed, dry_run_active, autotrade_disabled, live_orders_blocked | No redaction required | Useful evidence for audit-first UX and safety event visibility. |
| 7 | `07_portfolio_readonly_view.png` | `http://127.0.0.1:5173/portfolio` | Shows paper/read-only portfolio snapshot and no order controls. | READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED, Orders Denied, Live trade Blocked, Paper RO | No redaction required | Uses safe demo/fallback values only. |
| 8 | `08_readme_architecture_evidence.png` | Local rendered README evidence preview | Shows recruiter-facing README pitch, technical proof points, 3-minute review path, and safety posture. | READ ONLY, DRY RUN, LIVE TRADING BLOCKED, autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max risk <=1% | Original GitHub 404 capture rejected and retaken; final screenshot requires no redaction | Rendered from public-safe README content into an outside-repo local HTML preview to avoid browser chrome, login prompts, bookmarks, and private account UI. |

## Redaction Rules Applied

- Rejected the initial GitHub README capture because it showed a public GitHub 404/sign-in page instead of project evidence.
- Retook README evidence using an outside-repo local rendered preview with public-safe content only.
- No screenshot contains private email, phone number, full address, API key, token, password, private broker account ID, private CV data, desktop notifications, browser bookmarks, or real account values.
- Local ports such as `127.0.0.1:5173` and public project identifiers are acceptable for this evidence pack.
