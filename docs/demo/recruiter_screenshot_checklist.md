# Recruiter Screenshot Checklist

**Purpose:** Capture public-safe screenshots that let a recruiter understand MellyTrade in under 3 minutes.

**Safety rule:** Every screenshot must preserve the read-only/dry-run framing. Do not show private account IDs, private emails, phone numbers, broker credentials, API keys, secrets, live account balances, or any live-trading UX.

## Required Screenshots

| # | Screenshot | Route / page | Must be visible | Safety badges required | Redaction rules | Filename | Recruiter value |
|---:|---|---|---|---|---|---|---|
| 1 | Terminal overview | `/terminal` or dashboard entry route | Terminal shell, safety banner, market/context cards, system state | `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED` or equivalent visible posture | Redact account identifiers, local paths, private URLs, secrets | `01-terminal-overview.png` | Shows product polish, terminal UX and safety-first positioning |
| 2 | AI Workspace | `/terminal/workspace` or AI workspace panel | AI workspace card, advisory-only language, signal context, human review framing | `HUMAN REVIEW REQUIRED`, `READ ONLY`, `DRY RUN` | Redact prompts containing private personal data or credentials | `02-ai-workspace.png` | Shows supervised AI workflow and decision-support framing |
| 3 | Signals / signal quality | `/terminal/signals` or signal quality card | Signal list/quality summary, confidence/risk language, blocked/review states | `READ ONLY`, `RISK BLOCKED` when applicable, `DRY RUN` | Redact external source keys, private notes, account data | `03-signal-quality.png` | Shows data/product thinking and explainable signal review |
| 4 | Risk guardrails | `/terminal/risk` or risk guardrails card | Max risk <=1%, autotrade false, dry_run true, risk limits, no-trade conditions | `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED` | No real broker/account values; use fixture/demo values only | `04-risk-guardrails.png` | Shows mature risk awareness and fintech safety discipline |
| 5 | Broker read-only state | `/terminal/brokers` or broker card | Broker status, safe disconnected/paper state, live orders blocked | `READ ONLY`, `LIVE ORDERS BLOCKED`, paper/disconnected state | Redact account IDs, hostnames, ports if sensitive, private broker data | `05-broker-readonly-state.png` | Shows broker adapter thinking and safe degraded states |
| 6 | Audit/events feed | `/terminal/audit` or audit/event rail | Event rows, timestamps, severity, safety notes, stale/degraded events | `READ ONLY` and `DRY RUN` visible in surrounding shell | Redact user names, private logs, local machine paths | `06-audit-events-feed.png` | Shows observability, auditability and responsible UX |
| 7 | Portfolio/read-only view | `/terminal/portfolio` or positions page | Read-only positions/portfolio presentation, empty/degraded/demo states | `READ ONLY`, `DRY RUN`, no order controls visible | Use fixture/demo data; no real balances or account IDs | `07-portfolio-readonly.png` | Shows UX states without execution affordances |
| 8 | README / architecture evidence | GitHub README and architecture/case-study docs | README For Recruiters section, safety contract, architecture links | Safety posture text visible | No private browser bookmarks, local paths, or signed-in account data | `08-readme-architecture-evidence.png` | Shows documentation quality and recruiter navigation path |

## Capture Rules

- Use a clean browser profile or hide bookmarks and extensions.
- Prefer fixture/demo data over any real account data.
- Keep browser zoom at 100% unless layout requires otherwise.
- Capture desktop viewport first, then optional mobile if useful.
- Use consistent filenames from the table above.
- Store final public screenshots only under a public-safe path such as `docs/assets/screenshots/recruiter/`.
- Do not commit screenshots until they have been manually reviewed for privacy.

## Acceptance Criteria

- Every screenshot can stand alone without implying live trading.
- No screenshot shows order placement, connect-live UX, broker execution, credentials, secrets, account IDs, private contact data, or real balances.
- At least one screenshot shows the safety posture explicitly: `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, max risk <=1%.
- The set tells a coherent story: product overview, AI workflow, signals, risk, broker state, auditability, read-only portfolio, and documentation evidence.
