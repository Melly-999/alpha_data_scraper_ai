# MellyTrade — Next 20 Implementation Steps

A prioritized, branch-by-branch implementation plan for the next development
phase. Read top-to-bottom: each step assumes the previous ones have either
landed on `main` or are explicitly noted as parallelizable.

**Global safety rules** (apply to every step — restated once here):
- `autotrade.enabled = false` preserved.
- `dry_run = true` preserved.
- `read_only = true` preserved on the Terminal V1 surface.
- `max_risk_per_trade <= 1.0%` preserved.
- No live order execution. No order buttons. No execution routes.
- No secrets committed. No broker / MT5 / IBKR live execution code added.

---

## Phase A — Immediate next steps (this week)

### Step 1 — Merge / close PR #56

| Field | Value |
|---|---|
| **Task ID** | (none — repo housekeeping) |
| **Goal** | Land the Terminal V1 screenshot assets onto `main`. |
| **Why it matters** | Unblocks the README hero image and the demo walkthrough. The PR has zero production code; review is purely visual. |
| **Dependencies** | Human review only. |
| **Suggested branch** | (existing) `feature/terminal-v1-demo-assets-20260508` |
| **Expected files** | Already pushed: 6 PNGs + `README.md` hero ref + runbook checklist + screenshot plan. |
| **Validation** | None new — `pytest tests/app/ -q` and `npm run build` already verified locally. |
| **Risk** | Low |
| **Owner** | Human |
| **Separate PR?** | Yes (already PR #56) |

### Step 2 — Merge / close PR #57

| Field | Value |
|---|---|
| **Task ID** | SAFE-001 |
| **Goal** | Land the central `/api/safety/status` contract endpoint. |
| **Why it matters** | Single source of truth for the safety posture; enables Step 7 (TERM-001 banner rewiring) and Step 8 (BRK-001) to depend on a stable contract. |
| **Dependencies** | Human review of PR #57. |
| **Suggested branch** | (existing) `feature/safety-status-contract` |
| **Expected files** | 4 files — 3 new + `app/main.py` registration. |
| **Validation** | `pytest tests/app/test_safety_status.py -v` (13 / 13), full suite 158 / 158, frontend build clean. |
| **Risk** | Low |
| **Owner** | Human |
| **Separate PR?** | Yes (already PR #57) |

### Step 3 — Re-enable GitHub Actions

| Field | Value |
|---|---|
| **Task ID** | (account-level fix; not a coding task) |
| **Goal** | Resolve `HTTP 422: Actions has been disabled for this user.` so CI can run on every subsequent PR. |
| **Why it matters** | Until this is fixed, every PR ships without a green CI tick; reviewers must trust local validation. Steps 4 onward become much cheaper to verify once CI works. |
| **Dependencies** | Human-only — repo / account / billing settings. See `docs/dev/github_actions_recovery.md`. |
| **Suggested branch** | (none) |
| **Expected files** | (none) |
| **Validation** | After re-enable: `gh workflow run pytest.yml --ref main` succeeds; `gh pr checks 57` and `gh pr checks 56` show queued/running checks. |
| **Risk** | Low |
| **Owner** | Human |
| **Separate PR?** | No (no code change) |

### Step 4 — TEST-001: OpenAPI forbidden-path scan

| Field | Value |
|---|---|
| **Task ID** | TEST-001 |
| **Goal** | Add a pytest assertion that walks `app.openapi()` and fails if any path contains forbidden segments (`execute`, `live-trade`, `place-order`, `submit-trade`). |
| **Why it matters** | Complements the existing route-segment test by also catching paths registered via FastAPI's OpenAPI extras. Cheap defence in depth. |
| **Dependencies** | None. |
| **Suggested branch** | `test/openapi-forbidden-paths` |
| **Expected files** | `tests/app/test_safety_invariants.py` (extend, +1 parametrized test). |
| **Validation** | `pytest tests/app/test_safety_invariants.py -v` → 40 passed (was 39). |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 5 — TEST-010: Audit filter alignment test

| Field | Value |
|---|---|
| **Task ID** | TEST-010 |
| **Goal** | Static text-scan test that every backend-emitted audit `type` is listed in the frontend `EVENT_TYPES` filter dropdown. |
| **Why it matters** | Closes the cross-cut gap from the Task 2 / Task 3 review: a new event type silently swallowed by the dropdown is otherwise invisible. |
| **Dependencies** | None. |
| **Suggested branch** | `test/audit-filter-alignment` |
| **Expected files** | `tests/app/test_audit_events.py` (extend). |
| **Validation** | `pytest tests/app/test_audit_events.py -v` → all green. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes (small, sibling of Step 4 — could bundle if same day) |

### Step 6 — TEST-003 + TEST-004: Local validation scripts

| Field | Value |
|---|---|
| **Task ID** | TEST-003, TEST-004 |
| **Goal** | `scripts/validate_local.ps1` (Windows PowerShell) and `.sh` (POSIX) running `pytest tests/app/ -q` + `npm run build` + a no-secrets scan, printing a green/red summary. |
| **Why it matters** | A single command for any contributor / future-you to validate before opening a PR. Especially important while CI is unavailable. |
| **Dependencies** | None. |
| **Suggested branch** | `tooling/local-validation-scripts` |
| **Expected files** | `scripts/validate_local.ps1`, `scripts/validate_local.sh`, `docs/dev/local_validation.md`. |
| **Validation** | Run both scripts manually; expect 0 exit code on a clean tree. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 7 — SAFE-008: Safety architecture document

| Field | Value |
|---|---|
| **Task ID** | SAFE-008 |
| **Goal** | A single comprehensive `docs/architecture/SAFETY_POSTURE.md` mapping every invariant to its enforcement point (config / schema / test / runtime / UI). |
| **Why it matters** | Reviewer-readable single page that answers "is this safe?" without reading code. Pairs with PR #57's contract endpoint. |
| **Dependencies** | Step 2 merged (so the doc can reference `/api/safety/status` as live). |
| **Suggested branch** | `docs/safety-posture-architecture` |
| **Expected files** | `docs/architecture/SAFETY_POSTURE.md` (new), `README.md` (one link). |
| **Validation** | Markdown lint clean; word count ≥ 1 500; no real-secret patterns. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

---

## Phase B — Broker abstraction foundation (next 1–2 weeks)

### Step 8 — BRK-001: BrokerAdapter Protocol

| Field | Value |
|---|---|
| **Task ID** | BRK-001 |
| **Goal** | Define `BrokerAdapter` Protocol/ABC with `id()`, `capabilities()`, `status()`, `account_snapshot()`, `positions()`. **No execution methods.** |
| **Why it matters** | Foundational interface that IBKR, MT5, and the safe-disconnected default all implement. Locks down what an adapter can and cannot do at the type level. |
| **Dependencies** | Steps 1, 2, 7 merged. |
| **Suggested branch** | `feature/broker-adapter-protocol` |
| **Expected files** | `brokers/protocol.py` (new), `app/schemas/broker.py` (extend), `tests/app/test_broker_protocol.py` (new). |
| **Validation** | `pytest tests/app/test_broker_protocol.py -v` ≥ 6 assertions (no `place_order`/`cancel_order`/`modify_order` on protocol). |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 9 — BRK-002: SafeDisconnectedBrokerAdapter

| Field | Value |
|---|---|
| **Task ID** | BRK-002 |
| **Goal** | Default no-op adapter that always reports `read_only=True`, `connected=False`, `execution_enabled=False`, `live_orders_blocked=True`, with empty positions and a populated `safety_note`. |
| **Why it matters** | The fallback when no real adapter is registered. Keeps the dashboard working even with zero brokers wired in. |
| **Dependencies** | Step 8 merged. |
| **Suggested branch** | `feature/broker-safe-disconnected` |
| **Expected files** | `brokers/safe_disconnected.py` (new), `tests/app/test_broker_safe_disconnected.py` (new). |
| **Validation** | ≥ 4 assertions: capability flags, empty positions, populated safety_note. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes (can bundle with Step 8 if delivered same day) |

### Step 10 — BRK-003..006: Broker schemas

| Field | Value |
|---|---|
| **Task ID** | BRK-003, BRK-004, BRK-005, BRK-006 |
| **Goal** | `BrokerCapabilities`, `BrokerStatus`, `BrokerAccount`, `BrokerPositions` Pydantic schemas with `extra="forbid"`. None of them carry any execution-shaped field (no `order_id`, `quantity`, `sl`, `tp`). |
| **Why it matters** | Schema-level safety: even if a future adapter author tries to add an order field, it will fail validation. |
| **Dependencies** | Step 8 merged. |
| **Suggested branch** | `feature/broker-schemas` |
| **Expected files** | `app/schemas/broker.py` (extend). |
| **Validation** | `pytest tests/app/test_broker_schemas.py -v` ≥ 8 assertions, including `extra="forbid"` round-trip. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes (can bundle with Step 8 / Step 9) |

### Step 11 — BRK-007: Broker registry

| Field | Value |
|---|---|
| **Task ID** | BRK-007 |
| **Goal** | `brokers/registry.py` — `list()`, `get(id)`. Default registration: `["safe-disconnected"]`. Allow future adapters to register via dependency injection. |
| **Why it matters** | Central place to enumerate adapters; consumed by Step 12 endpoints. |
| **Dependencies** | Steps 8–10 merged. |
| **Suggested branch** | `feature/broker-registry` |
| **Expected files** | `brokers/registry.py` (new), `app/core/container.py` (wire registry), `tests/app/test_broker_registry.py` (new). |
| **Validation** | ≥ 4 assertions: default contains safe-disconnected, registry survives restart, no execution side effects. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 12 — BRK-008..011: GET-only broker endpoints

| Field | Value |
|---|---|
| **Task ID** | BRK-008, BRK-009, BRK-010, BRK-011 |
| **Goal** | Four routes: `GET /api/brokers`, `/api/brokers/{id}/status`, `/api/brokers/{id}/account`, `/api/brokers/{id}/positions`. All GET-only; tests confirm 405 on POST/PUT/DELETE/PATCH. |
| **Why it matters** | Frontend can finally render real broker data via abstraction. The route-inventory test must continue to pass. |
| **Dependencies** | Step 11 merged. |
| **Suggested branch** | `feature/broker-get-endpoints` |
| **Expected files** | `app/api/routes/brokers.py` (new — note: namespace already exists for `broker.py`; add the new collection there), `app/main.py` (register), `tests/app/test_broker_routes.py` (extend). |
| **Validation** | ≥ 12 assertions (3 per route × 4 routes). |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 13 — BRK-012 + BRK-013: Frontend broker client + BrokerCard

| Field | Value |
|---|---|
| **Task ID** | BRK-012, BRK-013 |
| **Goal** | `frontend/src/hooks/useBroker.ts` extension (one hook per endpoint, all `apiGet`), plus shared `<BrokerCard>` component reused per broker. |
| **Why it matters** | Visible UI surface for the broker abstraction. Demonstrates the dashboard works with zero real brokers connected. |
| **Dependencies** | Step 12 merged. |
| **Suggested branch** | `feature/frontend-broker-card` |
| **Expected files** | `frontend/src/hooks/useBroker.ts` (extend), `frontend/src/components/cards/BrokerCard.tsx` (new), `frontend/src/pages/DashboardPage.tsx` (wire one card row). |
| **Validation** | `npm run build` clean; existing safety regression test still passes (no mutating helper imported). |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

---

## Phase C — Existing brokers behind the abstraction (weeks 2–3)

### Step 14 — MT5-001..006: Wrap MT5 read-only behind BrokerAdapter

| Field | Value |
|---|---|
| **Task ID** | MT5-001..006 |
| **Goal** | Wrap the existing MT5 service in the `BrokerAdapter` protocol; expose status, account snapshot, positions read-only; degrade safely when `MetaTrader5` import fails. |
| **Why it matters** | First real adapter implementation against the new contract. Verifies the abstraction holds. |
| **Dependencies** | Step 13 merged. |
| **Suggested branch** | `feature/mt5-readonly-via-broker-adapter` |
| **Expected files** | `brokers/mt5_paper.py` (new), `app/services/mt5_service.py` (refactor), `tests/app/test_mt5_adapter.py` (new). |
| **Validation** | Mocked `MetaTrader5` module import; ≥ 6 assertions including disconnected fallback. |
| **Risk** | Med — touches existing MT5 service. Must preserve current dashboard behaviour. |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 15 — IBKR-001..004: IBKR read-only paper skeleton

| Field | Value |
|---|---|
| **Task ID** | IBKR-001..004 |
| **Goal** | IBKR adapter skeleton with paper config model, connection status, disconnected safe fallback. **No execution methods on the adapter class.** No real network in tests. |
| **Why it matters** | First broker the project explicitly markets as "paper / read-only first." Critical that the disconnected path is the *default* — not the unhappy path. |
| **Dependencies** | Step 13 merged. Step 14 useful for cross-reference but not strict. |
| **Suggested branch** | `feature/ibkr-readonly-skeleton` |
| **Expected files** | `brokers/ibkr_paper.py` (extend existing), `brokers/ibkr_config.py` (new), `tests/app/test_ibkr_*.py` (new). |
| **Validation** | Mocked IBKR client; ≥ 8 assertions including disconnected fallback and explicit "no `placeOrder` method on adapter". |
| **Risk** | Med |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

---

## Phase D — Dashboard polish & risk surface (weeks 3–4)

### Step 16 — TERM-001: Dashboard banner uses `/api/safety/status`

| Field | Value |
|---|---|
| **Task ID** | TERM-001 |
| **Goal** | Migrate `<SafetyBanner>` to read from `/api/safety/status` (PR #57 endpoint) instead of `/health` + `/risk/config`. |
| **Why it matters** | Single source of truth; reduces code paths for posture checking. |
| **Dependencies** | Step 2 merged. |
| **Suggested branch** | `feature/safety-banner-uses-safety-status` |
| **Expected files** | `frontend/src/hooks/useSafetyStatus.ts` (new), `frontend/src/components/SafetyBanner.tsx`, `frontend/src/types/api.ts`. |
| **Validation** | `npm run build` clean; safety regression test still passes. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 17 — TERM-008: Broker status row on Dashboard

| Field | Value |
|---|---|
| **Task ID** | TERM-008 |
| **Goal** | Add a row of `<BrokerCard>`s on the Dashboard, one per registered adapter. |
| **Why it matters** | Visible payoff for the broker abstraction work. |
| **Dependencies** | Steps 13, 14, 15 merged (cards have something real to display). |
| **Suggested branch** | `feature/dashboard-broker-row` |
| **Expected files** | `frontend/src/pages/DashboardPage.tsx`, `frontend/src/index.css` (small layout). |
| **Validation** | `npm run build` clean; visual sanity in `npm run dev`. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 18 — RISK-001 + RISK-002: Canonical RiskPolicy + extended RiskStatus

| Field | Value |
|---|---|
| **Task ID** | RISK-001, RISK-002 |
| **Goal** | Single canonical `RiskPolicy` Pydantic schema (`extra="forbid"`); extend existing `RiskStatus` with `cooldown_remaining_s`, `daily_loss_used_pct`, `open_positions_count`. |
| **Why it matters** | Replaces ad-hoc dicts with a typed contract that powers Steps 19 and any later guardrail UI. |
| **Dependencies** | Step 7 merged. |
| **Suggested branch** | `feature/canonical-risk-policy` |
| **Expected files** | `app/schemas/risk.py` (extend), `app/services/risk_service.py` (use new types), `tests/app/test_risk_*.py` (extend). |
| **Validation** | All existing risk tests still green; new round-trip tests pass. |
| **Risk** | Med — touches the risk service. Must preserve all current test outputs. |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 19 — SIG-001: SignalFeedItem schema upgrade

| Field | Value |
|---|---|
| **Task ID** | SIG-001 |
| **Goal** | Extend `SignalFeedItem` with `explanation`, `confidence_explanation`, `invalidation_level`, `timeframe`, `source` enum. Backwards compatible (new fields optional). |
| **Why it matters** | Foundation for Phase E's signal-explanation UI. Lets us surface *why* a signal exists, not just its direction. |
| **Dependencies** | Step 18 merged. |
| **Suggested branch** | `feature/signal-feed-item-explanation` |
| **Expected files** | `app/schemas/signals.py`, `app/services/signal_service.py`, `tests/app/test_signal_*.py`. |
| **Validation** | All existing 158+ tests still green; new schema tests pass. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

### Step 20 — DOC-001: Terminal V1 release notes

| Field | Value |
|---|---|
| **Task ID** | DOC-001 |
| **Goal** | `docs/RELEASE_NOTES_TERMINAL_V1.md` summarising commits + screenshots + safety contract for portfolio readers. |
| **Why it matters** | Portfolio-grade single-page summary suitable for sharing as a CV link. Closes the Terminal V1 milestone narratively. |
| **Dependencies** | Steps 1, 2 merged. Steps 8–17 ideally merged so the doc can describe "Terminal V1.1". |
| **Suggested branch** | `docs/release-notes-terminal-v1` |
| **Expected files** | `docs/RELEASE_NOTES_TERMINAL_V1.md`, `README.md` (one link). |
| **Validation** | Markdown lint clean; word count ≥ 1 200; no real-secret patterns. |
| **Risk** | Low |
| **Owner** | Claude Code |
| **Separate PR?** | Yes |

---

## Phase E — Later (weeks 5+, not in this 20-step horizon)

Brief reminders of what comes after Step 20, listed here so the roadmap
is clear about what is **not** in scope for this sprint:

- **RISK-006..011** — stop-loss / take-profit / min R:R rules + audit
  events for blocked trades.
- **WL-001..009** — Watchlist / Market Overview.
- **NEWS-001..010** — News / sentiment / economic calendar.
- **BT-001..017** — Backtesting / reports.
- **ALERT-001..012** — Alerts (notification-only, no execution).
- **DATA-001..012** — Market data provider abstraction.
- **AUD-001..009** — Centralized audit event model.
- **MCP-001..014** — AI Dev Control Center.
- **QR-001..015** — Quant Research Lab (Direction C).
- **DRY-001..013** — Dry-run automation **design only**; no live
  execution code in this horizon.

---

## Cadence

| Phase | Calendar | Step IDs |
|---|---|---|
| A — Immediate | This week | 1 → 7 |
| B — Broker foundation | Next 1–2 weeks | 8 → 13 |
| C — Adapters | Weeks 2–3 | 14 → 15 |
| D — Dashboard + risk | Weeks 3–4 | 16 → 20 |
| E — Watchlist / news / backtest / alerts / quant research | Weeks 5+ | (out of scope here) |

---

**Last updated**: 2026-05-09
