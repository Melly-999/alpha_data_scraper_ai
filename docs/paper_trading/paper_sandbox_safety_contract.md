# PAPER-GUARD-001 — Paper Sandbox Safety Contract

## Purpose

This contract defines guardrails for future paper-only decision support and
controlled paper sandbox work.  It is enforced by
`tests/app/test_paper_sandbox_guardrails.py` and reviewed at every PR that
touches the paper trading namespace.

Any future paper-sandbox implementation must comply with every rule in this
document.  Adding an endpoint, service, or schema that violates a rule
requires an explicit review event and a corresponding update to this contract.

---

## What the paper sandbox is NOT

| Capability | Status |
|---|---|
| Live trading | **NEVER** |
| Real broker execution | **NEVER** — no MT5, IBKR, or any real broker |
| MT5 / IBKR order routing | **NEVER** |
| Autotrade enablement | **NEVER** |
| `dry_run=false` path | **NEVER** |
| `read_only=false` path | **NEVER** |
| `live_orders_blocked=false` | **NEVER** |
| Automated order placement | **NEVER** |

---

## Invariants that must never change

| Invariant | Required value | Enforced by |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json`, `test_safety_invariants.py`, guardrails |
| `autotrade.dry_run` | `true` | `config.json`, `test_safety_invariants.py`, guardrails |
| `TradeTicketDraft.paper_only` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.dry_run` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.read_only` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.live_orders_blocked` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.requires_human_review` | `True` | `Literal[True]` in schema |
| `TradeTicketDraft.broker_execution_allowed` | `False` | `Literal[False]` in schema |
| `TradeTicketDraft.risk_allowed` | `False` | `Literal[False]` in schema |
| `max_risk_pct` | `<= 1.0` | Schema `le=1.0`, validator runtime check |
| Stop loss | required | Schema required field, `gt=0`, geometry-validated |
| Take profit | required | Schema required field, `gt=0`, geometry-validated |
| Human review | required | `requires_human_review=True` always |

---

## Allowed future namespace

All future paper sandbox endpoints must live within:

```
/api/paper/**
/paper/**          (if needed for non-API routing)
```

No paper-adjacent endpoint may be placed outside this namespace.

---

## Forbidden namespace

The following path patterns must **never** be added as execution routes:

```
/api/orders
/api/order
/api/execute
/api/execution
/api/trade
/api/trades
/api/broker/execute
/api/broker/order
/api/mt5/order
/api/ibkr/order
/api/autotrade/enable
/api/live
/api/live-trade
/api/live_trade
```

Any path containing these fragments outside `/api/paper` or `/paper` that
also uses a mutating HTTP method (`POST`, `PUT`, `PATCH`, `DELETE`) or
contains live-execution metadata will fail the guardrail tests.

---

## Rules for future paper endpoint design

Every endpoint under `/api/paper/**` must comply with all of the following:

### Identity rules
- Path name, `summary`, `description`, or `operationId` must include at
  least one of: `paper`, `sandbox`, `dry_run`, `simulated`.
- Must not contain `live broker`, `real broker`, `mt5 execution`,
  `ibkr execution`, `live order`, or `place live` in metadata unless in an
  explicit negative/safety context (e.g. "does NOT call live broker").

### Implementation rules
- Must never call real broker adapters (MT5, IBKR, or any real exchange API).
- Must require human approval before any simulated execution step.
- Must never bypass `TradeTicketValidator`.
- Must emit an audit event (enforced once SUPA-003 audit writer ships).
- Must return `paper_only=true` in every response.
- Must return `dry_run=true` in every response.
- Must return `read_only=true` in every response.
- Must return `live_orders_blocked=true` in every response.
- Must never return `broker_execution_allowed=true`.
- Must never return `risk_allowed=true` until a separate reviewed
  risk-gate design has been approved and merged.

### Field rules
- Must not include any of the following in response schemas:
  `order_id`, `fill_id`, `execution_id`, `broker_order_id`,
  `account_id`, `credential`, `token`, `secret`.

---

## OpenAPI guardrail test coverage

`tests/app/test_paper_sandbox_guardrails.py` asserts:

| Check | What it catches |
|---|---|
| Schema is non-empty | Prevents vacuous passes if OpenAPI breaks |
| No live execution route outside paper namespace | Catches accidentally-placed order/execute/broker paths |
| Paper namespace endpoints are paper-only | Catches paper endpoints that forget safety metadata |
| No mutating methods on trading paths outside paper namespace | Catches POST/PUT/PATCH/DELETE on order/broker/execute paths |
| No autotrade-enable route | Catches any route that could flip autotrade on |
| `config.json` invariants | Belt-and-braces: autotrade=false, dry_run=true |
| Schema safety fields cannot be overridden | Validates `Literal[True/False]` protection |
| Validator never flips risk_allowed | Prevents accidental validator weakening |
| Draft service always forces safety fields | End-to-end safety field invariant |
| No live execution fields in paper models | Prevents model drift toward execution semantics |

---

## Roadmap relation

### PDS series (ticket contract and draft pipeline)

| ID | Title | Status |
|---|---|---|
| **PDS-001** | Paper-only TradeTicket schema & validator | ✅ Merged |
| **PDS-002** | Ticket Draft Service from Scanner Preview | ✅ Merged |
| **PAPER-GUARD-001** | This document + guardrail tests | ✅ Merged |
| **PDS-003** | Draft endpoint (read-only, no execution) | ✅ Merged |
| **PDS-004** | AI Workspace ticket preview | ✅ Merged |

### PAPER series (in-memory paper sandbox)

The PAPER series is split into focused, scope-safe increments.  No increment
may add broker execution, MT5/IBKR calls, live order placement, or mutating
(POST/PUT/PATCH/DELETE) sandbox routes unless explicitly approved via a
contract update to this document.

| ID | Title | Status | Notes |
|---|---|---|---|
| **PAPER-001A** | Backend in-memory paper sandbox foundation | ✅ Merged | `app/schemas/paper_sandbox.py`, `app/services/paper_sandbox.py`, 47 tests. No route wired. |
| **PAPER-001B** | GET-only paper sandbox preview endpoint | ✅ Merged | `GET /api/paper/sandbox/preview`. Read-only, dry-run-only. No POST/PUT/PATCH/DELETE. No frontend UI. |
| **PAPER-001C** | AI Workspace paper sandbox preview panel | ✅ Merged | Frontend read-only panel consuming PAPER-001B. Display only — no order/buy/sell/execute buttons. |
| **PAPER-002A** | Backend in-memory paper sandbox history service | ✅ Merged | `app/schemas/paper_sandbox_history.py`, `app/services/paper_sandbox_history.py`. **Backend/schema/tests only — no route wired, no frontend UI.** |
| **PAPER-002B** | GET-only paper sandbox history endpoint | ✅ Merged | `GET /api/paper/sandbox/history`. Read-only, dry-run-only. No POST/PUT/PATCH/DELETE. No frontend UI. |
| **PAPER-002C** | AI Workspace paper sandbox activity/audit rail | ✅ Merged | Frontend read-only audit trail panel consuming PAPER-002B. Display only — no order/buy/sell/execute buttons. |
| **PAPER-003** | Local demo script: draft → sandbox preview → history/audit → UI | 🔄 Current | `scripts/demo_paper_sandbox_local.ps1`, `docs/demo/paper_sandbox_local_demo.md`, `scripts/demo_paper_sandbox_readonly_smoke.ps1`, `docs/demo/paper_sandbox_readonly_smoke.md`. Local smoke/demo only — no broker execution, no backend route added, no frontend trading control. |

### Supporting infrastructure

| ID | Title | Status |
|---|---|---|
| **SUPA-003** | Audit writer service | ⬜ Planned |
| **OPENCLAW-005** | Discord phone smoke tests | ⬜ Planned |

---

## PAPER-001B implementation rules

PAPER-001B adds exactly one endpoint: `GET /api/paper/sandbox/preview`.

### What PAPER-001B does

- Returns the current in-memory `PaperSandboxState` (entries, count, safety flags).
- Explicit empty-state response when no records exist (`count=0`, `entries=[]`).
- Intended for consumption by the PAPER-001C read-only frontend panel.

### What PAPER-001B must NOT do

- **No POST, PUT, PATCH, or DELETE routes** — GET only.
- **No frontend UI** — that is PAPER-001C.
- **No broker execution** — no MT5, IBKR, or any real exchange API.
- **No live order placement** — the endpoint is observational only.
- **No autotrade/dry-run/read-only policy changes**.
- **No secrets, credentials, account IDs, or API tokens** in responses.

### Safety flags the endpoint must always return

| Flag | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_mode` | `"dry_run_only"` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |

### PAPER-001C constraints

PAPER-001C is frontend visibility only:

- May only consume `GET /api/paper/sandbox/preview`.
- Must not add any order/buy/sell/execute/place-order frontend controls.
- Panel is read-only — display of paper simulation state only.

---

## PAPER-002A implementation rules

PAPER-002A adds the in-memory paper sandbox activity/audit history foundation.

### What PAPER-002A delivers

- `app/schemas/paper_sandbox_history.py` — `PaperAuditEvent` and
  `PaperAuditHistory` Pydantic schemas with locked safety flags.
- `app/services/paper_sandbox_history.py` — `PaperAuditHistoryService`
  in-memory singleton; sequential local event IDs (`paper_audit_000001`);
  forbidden-field metadata sanitization; 250-event cap; thread-safe.
- `tests/app/test_paper_sandbox_history.py` — comprehensive test suite.

### What PAPER-002A must NOT do

- **No route wired** — GET endpoint is deferred to PAPER-002B.
- **No frontend UI** — panel is deferred to PAPER-002C.
- **No broker execution** — no MT5, IBKR, or any real exchange API.
- **No database / Supabase / network** — in-memory only.
- **No secrets, credentials, account IDs, or API tokens** — forbidden keys
  are sanitized out of event metadata.
- **No POST/PUT/PATCH/DELETE routes** — none added in this increment.
- **No autotrade/dry-run/read-only policy weakening**.

### Safety flags every event must carry

| Flag | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_mode` | `"dry_run_only"` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |

---

## PAPER-002B implementation rules

PAPER-002B adds exactly one endpoint: `GET /api/paper/sandbox/history`.

### What PAPER-002B delivers

- `GET /api/paper/sandbox/history` route wired into `app/api/routes/paper_sandbox.py`.
- Returns the current `PaperAuditHistory` snapshot from the `PaperAuditHistoryService`
  in-memory singleton.
- Explicit empty-state response when no events exist (`count=0`, `events=[]`).
- `tests/app/test_paper_sandbox_history_endpoint.py` — endpoint test suite.
- Updated roadmap in this document.

### What PAPER-002B must NOT do

- **No POST, PUT, PATCH, or DELETE routes** — GET only.
- **No frontend UI** — that is PAPER-002C.
- **No broker execution** — no MT5, IBKR, or any real exchange API.
- **No live order placement** — the endpoint is observational only.
- **No autotrade/dry-run/read-only policy changes**.
- **No secrets, credentials, account IDs, or API tokens** in responses.
- **No mutation of history** — endpoint is read-only; history is append-only via the service.

### Safety flags the endpoint must always return

| Flag | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_mode` | `"dry_run_only"` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |

---

## PAPER-002C implementation rules

PAPER-002C adds the read-only AI Workspace activity/audit rail panel.

### What PAPER-002C delivers

- `frontend/src/lib/paperSandboxApi.ts` — Extended with `PaperAuditEvent`,
  `PaperAuditHistory`, `PaperHistoryApiResult` TypeScript types and
  `getPaperSandboxHistory()` GET-only client function.
- `frontend/src/components/terminal/PaperSandboxActivityRail.tsx` — New
  read-only panel. Polls `GET /api/paper/sandbox/history` every 20 s.
  Displays event count, audit event rows (newest first), severity chips,
  safety badges, safety contract snapshot, empty/error/loading states.
- `frontend/src/components/terminal/AIWorkspacePanel.tsx` — Mounts
  `<PaperSandboxActivityRail />` in the workspace main column, adjacent to
  `<PaperSandboxPreviewPanel />`.
- `frontend/src/components/terminal/index.ts` — Exports the new component.
- `frontend/src/components/terminal/terminal.css` — Adds `paper-audit-*`
  CSS classes consistent with the terminal design system.
- `docs/paper_trading/paper_sandbox_safety_contract.md` — Updated roadmap.

### What PAPER-002C must NOT do

- **No POST, PUT, PATCH, or DELETE frontend calls** — GET only.
- **No order/buy/sell/execute/place-order/submit-order buttons** — display only.
- **No broker execution UI** — no MT5, IBKR, or any real exchange controls.
- **No connect-live UX** — panel is purely observational.
- **No autotrade/dry-run/read-only policy changes**.
- **No secrets, credentials, account IDs, or API tokens** in UI state.
- **No backend route changes** — all backend work was completed in PAPER-002A/B.

### Safety flags the panel must always display

| Flag | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_mode` | `"dry_run_only"` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |

---

## PAPER-003 implementation rules

PAPER-003 adds a local demo smoke script and documentation only.

### What PAPER-003 delivers

- `scripts/demo_paper_sandbox_local.ps1` — PowerShell smoke script that
  validates the local paper sandbox dashboard flow end-to-end:
  safety config → backend health → preview endpoint → history endpoint →
  frontend workspace route → screenshot checklist.
- `docs/demo/paper_sandbox_local_demo.md` — Human-readable demo guide
  with startup instructions, screenshot checklist, and safety statement.
- `docs/paper_trading/paper_sandbox_safety_contract.md` — Updated roadmap.

### What PAPER-003 must NOT do

- **No new backend route** — calls only existing `GET /api/paper/sandbox/preview`
  and `GET /api/paper/sandbox/history`.
- **No broker execution** — no MT5, IBKR, or any real exchange API.
- **No live order placement** — demo script is observational only.
- **No frontend trading controls** — no order/buy/sell/execute/place-order
  buttons added or changed.
- **No mutation** — no POST/PUT/PATCH/DELETE calls in the script.
- **No secrets, credentials, account IDs, or API tokens** stored or passed.
- **No autotrade/dry-run/read-only policy changes**.
- **No database, Supabase, or external network calls** — localhost only.

### Safety posture the script always verifies

| Flag | Required value |
|---|---|
| `paper_only` | `true` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `execution_mode` | `"dry_run_only"` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |

---

## Updating this contract

If a future PR needs to relax any rule above, the PR must:

1. Update this document with a clear justification.
2. Update the guardrail test to reflect the new approved rule.
3. Get explicit review and approval from the project owner before merging.

Silently bypassing a guardrail without updating this document is a
safety regression by definition.

---

## Related demo docs

- [`docs/demo/demo_002_screenshot_pack.md`](../demo/demo_002_screenshot_pack.md)
- [`docs/demo/demo_002_screenshot_inventory.md`](../demo/demo_002_screenshot_inventory.md)
- [`docs/demo/demo_002_portfolio_story.md`](../demo/demo_002_portfolio_story.md)
