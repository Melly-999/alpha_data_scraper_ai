# Safe Full Auto AI Dev System — Phased Rollout

**Version:** 1.0.0
**Status:** Active planning document
**Last updated:** 2026-05-09
**Safety class:** DEV-AUTOMATION — all phases are read-only unless explicitly stated

---

## Overview

This roadmap defines the phased rollout of the Safe Full Auto AI Dev System for MellyTrade. Each phase builds on the last. No phase introduces live trading, broker execution, or secret exposure.

**Golden rule:** Each phase must leave the repository in a state where all safety flags remain enforced:
```
autotrade=false  dry_run=true  read_only=true  live_orders_blocked=true  max_risk_pct<=1%
```

---

## Phase 0 — Docs and Safety Alignment

**Goal:** Establish the documentation foundation and safety architecture for the entire dev system before any code is written.

**Status:** In Progress (this sprint)

**Branch:** `docs/full-auto-ai-dev-system`

**Dependencies:** PR #55 merged (Terminal V1 milestone) ✓

### Tasks

| Task ID | Title | Owner | Status |
|---|---|---|---|
| DOC-001 | `full_auto_ai_dev_system.md` architecture doc | Claude Code | Done |
| DOC-002 | `mellytrade_mcp_tools.md` MCP tool reference | Claude Code | Done |
| DOC-003 | `mobile_full_auto_runbook.md` | Claude Code | Done |
| DOC-004 | `codex_task_queue.md` | Claude Code | Done |
| DOC-005 | `ai_dev_control_center.md` design doc | Claude Code | Done |
| DOC-006 | `mcp_local_skeleton_plan.md` | Claude Code | Done |
| DOC-007 | `full_auto_ai_dev_system_rollout.md` | Claude Code | Done |
| DOC-008 | `current_pr_stack.md` | Claude Code | Done |
| SAFE-008 | Safety architecture decision record | Claude Code | Ready (next) |

### Validation

- [ ] All files under `docs/`
- [ ] No source code, no config, no workflow YAML changed
- [ ] Secret scan clean
- [ ] `git diff --name-only` shows only `docs/` paths

### Acceptance Criteria

- All 8 docs exist and are complete
- Each doc references safety constraints explicitly
- Mermaid diagrams render correctly
- Local commit made on `docs/full-auto-ai-dev-system`

### Do-Not-Do-Yet

- No MCP implementation
- No frontend `/dev` route
- No validation scripts
- No broker code

---

## Phase 1 — Local Validation Scripts

**Goal:** Build local-only Python/PowerShell scripts that validate safety config, diff scope, OpenAPI forbidden routes, and audit alignment — replacing GitHub Actions while they remain disabled.

**Branch:** `test/local-validation-suite`

**Dependencies:** Phase 0 complete

### Tasks

| Task ID | Title | Owner | Size |
|---|---|---|---|
| TEST-001 | OpenAPI forbidden path scan | Codex | S |
| TEST-003 | Safety config validation script | Codex | XS |
| TEST-004 | Git diff scope validator | Codex | XS |
| TEST-010 | Audit filter alignment test | Codex | XS |
| OBS-001 | Audit event constants module | Codex | XS |
| OBS-002 | Smoke test runner script | Codex | XS |

### Validation

```powershell
py -3.11 scripts/validate_safety_config.py   # exits 0
py -3.11 scripts/validate_diff_scope.py      # exits 0 when docs-only
py -3.11 scripts/openapi_scan.py             # exits 0, no forbidden routes
py -3.11 scripts/smoke_test.py               # exits 0 when backend healthy
py -3.11 -m pytest tests/app/test_audit_filter.py -v
py -3.11 -m pytest tests/app/test_openapi_forbidden.py -v
```

### Acceptance Criteria

- All scripts exit 0 on clean state
- Scripts exit non-zero with clear error messages on violations
- No scripts write to config or source code
- Safety config validator correctly catches `autotrade=true` as a violation

### Safety Checks

- Scripts are read-only filesystem operations
- No scripts invoke broker APIs
- No scripts modify config
- Secret scan passes on all new files

### Do-Not-Do-Yet

- No MCP server
- No frontend changes
- No broker code

---

## Phase 2 — MCP Read-Only Skeleton

**Goal:** Build the minimal MCP server package — disabled by default, local-only, read-only tools, with startup validation that rejects forbidden tool names.

**Branch:** `feat/mcp-skeleton`

**Dependencies:** Phase 1 complete; `docs/architecture/mcp_local_skeleton_plan.md` approved

### Tasks

| Task ID | Title | Owner | Size |
|---|---|---|---|
| MCP-001 | MCP server skeleton | Codex | M |
| MCP-002 | MCP registry validator test | Codex | XS |
| + | Implement all 12 allowed tools | Codex | M |
| + | Auth middleware (bearer token) | Codex | S |
| + | Rate limiting middleware | Codex | S |
| + | Audit JSONL writer | Codex | XS |

### Validation

```powershell
py -3.11 -m mellytrade_mcp --validate          # exits 0
py -3.11 -m mellytrade_mcp --list-tools        # shows 12 tools, no forbidden names
py -3.11 -m pytest tests/mcp/ -v              # all pass
# Start server, run smoke test:
py -3.11 -m mellytrade_mcp --dev
py -3.11 scripts/smoke_test.py --mcp
```

### Acceptance Criteria

- Server starts only when explicitly invoked
- `--validate` exits non-zero if any forbidden tool name is registered
- All 12 allowed tools return correct structure
- Audit JSONL written for every tool call
- Token authentication enforced on all endpoints
- Rate limits enforced
- Zero network calls to broker APIs from any tool

### Safety Checks

- Tool registry scan in CI (when Actions re-enabled)
- Forbidden tool name scan on all tool files
- Auth middleware tested with invalid tokens → 401

### Do-Not-Do-Yet

- No frontend integration
- No Tailscale serve setup
- No broker tools

---

## Phase 3 — Dashboard AI Dev Control Center Planning

**Goal:** Design the `/dev` route in detail, define all components, agree on data contracts between frontend and backend before writing any frontend code.

**Branch:** `docs/ai-dev-control-center-planning`

**Dependencies:** Phase 0 complete (docs exist); Phase 2 MCP skeleton reviewed

### Tasks

| Task ID | Title | Owner | Size |
|---|---|---|---|
| DEV-CC-001 | Route structure and widget layout (done in Phase 0) | Claude Code | XS |
| DEV-CC-002 | Frontend component tree design doc | Claude Code | S |
| DEV-CC-003 | Backend API contract for `/dev` data sources | Claude Code | S |
| DEV-CC-004 | Mobile layout design | Claude Code | S |

### Validation

- [ ] Design docs complete and reviewed
- [ ] No frontend code changes yet
- [ ] Widget list matches Phase 0 spec

### Acceptance Criteria

- All component types defined with data sources
- Audit event list finalised
- Mobile layout priority order agreed
- No execution buttons in design

### Do-Not-Do-Yet

- No React code
- No new backend endpoints

---

## Phase 4 — Dashboard Read-Only Shell

**Goal:** Implement the `/dev` React route with all widgets as a read-only shell. Phase 4a: static mock data. Phase 4b: live backend polling.

**Branch:** `feat/dev-control-center-shell`

**Dependencies:** Phase 3 planning complete; Phase 2 MCP skeleton merged

### Phase 4a — Static Shell

| Task | Owner | Notes |
|---|---|---|
| Add `/dev` route to React Router | Codex | No live data yet |
| Implement all widget components with mock data | Codex | Static JSON fixtures |
| Implement Safety Posture badge | Codex | Critical widget; hardcode safe values |
| Implement DryRunBanner | Codex | Always shows "DRY RUN ACTIVE" |
| Mobile responsive layout | Codex | Priority widget order enforced |

### Phase 4b — Live Polling

| Task | Owner | Notes |
|---|---|---|
| Wire BackendHealthCard to `GET /api/health` | Codex | 15s poll |
| Wire SafetyPostureBadge to `GET /api/safety/status` | Codex | 30s poll |
| Wire AuditFeed to `GET /api/audit/events` | Codex | 15s poll |
| Wire remaining cards to MCP tools | Codex | Requires Phase 2 MCP server |

### Validation

```powershell
# Start backend and frontend, navigate to http://localhost:5173/dev
# Verify: all widgets render; no action buttons visible; safety posture shown
py -3.11 -m pytest tests/app/ -q
npm run type-check  # (frontend)
```

### Acceptance Criteria

- `/dev` route renders without errors
- No execution buttons on any widget
- Safety Posture widget always shows correct values
- DryRunBanner always visible
- Mobile layout tested on 390px viewport

### Safety Checks

- Manual review: no buttons that call POST/PUT/DELETE
- OpenAPI scan confirms no new execution routes added
- Safety config validation passes

### Do-Not-Do-Yet

- No Tailscale serve setup (Phase 5)
- No broker widgets (Phase 6)

---

## Phase 5 — Tailscale / Private Mobile Access

**Goal:** Document and implement the Tailscale private access setup so the dashboard is safely accessible from any device on the developer's Tailscale network.

**Branch:** `docs/tailscale-mobile-access`

**Dependencies:** Phase 4 dashboard shell working

### Tasks

| Task | Owner | Notes |
|---|---|---|
| Tailscale Serve configuration guide | Claude Code | Docs |
| Vite host config for Tailscale | Codex | `vite.config.ts` update |
| Backend Tailscale bind config | Codex | `--host` option in runbook |
| Mobile layout final polish | Codex | Test on real phone |

### Validation

- [ ] Dashboard accessible from phone via Tailscale IP
- [ ] HTTPS via `tailscale serve`
- [ ] No public internet exposure
- [ ] Safety posture visible on phone

### Acceptance Criteria

- Phone can access `https://<device>.ts.net/dev`
- All safety widgets visible on phone
- No action buttons accidentally visible on mobile
- Tailscale ACLs restrict access to developer devices

### Do-Not-Do-Yet

- No broker code (Phase 6)
- No IBKR (Phase 7)

---

## Phase 6 — Broker Abstraction

**Goal:** Introduce the `BrokerAdapter` protocol and `SafeDisconnectedBrokerAdapter` — enabling the dashboard to show broker status without any live broker connection.

**Branch:** `feat/broker-adapter-protocol`

**Dependencies:** Phase 4 dashboard shell; Phase 5 mobile access

### Tasks (see `docs/tasks/codex_task_queue.md` for full specs)

| Task ID | Title |
|---|---|
| BRK-001 | BrokerAdapter protocol |
| BRK-002 | SafeDisconnectedBrokerAdapter |
| BRK-003 to BRK-006 | Broker schemas |
| BRK-007 | BrokerAdapter registry |
| BRK-008 to BRK-011 | GET-only broker endpoints |
| BRK-012 | Frontend broker API client |
| BRK-013 | BrokerCard component |

### Validation

```powershell
py -3.11 -m pytest tests/brokers/ -v
py -3.11 scripts/openapi_scan.py  # no forbidden routes
# Navigate to /dev → BrokerCard shows "SafeDisconnected"
```

### Acceptance Criteria

- `GET /api/broker/status` returns SafeDisconnected by default
- No execution endpoints created
- BrokerCard shows status only; no action buttons
- OpenAPI scan passes

### Safety Checks

- All broker adapter methods are read-only
- `SafeDisconnectedBrokerAdapter` makes zero network calls
- Registry default is always safe adapter

### Do-Not-Do-Yet

- No IBKR authentication (Phase 7)
- No live broker connection

---

## Phase 7 — IBKR Read-Only Paper Adapter

**Goal:** Implement a read-only IBKR paper trading adapter that connects to the IBKR paper account for status display only. No order placement, no live account.

**Branch:** `feat/ibkr-paper-adapter`

**Dependencies:** Phase 6 broker abstraction complete and merged

### Tasks

| Task | Owner | Notes |
|---|---|---|
| IBKR paper connection config docs | Claude Code | Paper account only |
| `IBKRPaperAdapter` implementation | Codex | Extends BrokerAdapter protocol |
| Paper account credential handling | Human | Never committed; env only |
| Connection health check | Codex | Read-only heartbeat |
| Disconnect-on-error safeguard | Codex | Falls back to SafeDisconnected |

### Validation

- [ ] IBKR paper adapter returns account info for paper account only
- [ ] No order placement possible through adapter
- [ ] Falls back to SafeDisconnected on connection failure
- [ ] Paper account type explicitly validated in tests

### Acceptance Criteria

- `get_account_info()` returns `account_type="paper"`
- `get_positions()` and `get_open_orders()` return read-only data
- Connection failure → automatic fallback to SafeDisconnectedBrokerAdapter
- Credentials never in source code

### Safety Checks

- Paper account type assertion in adapter init
- If `account_type != "paper"`: raise error, do not connect
- No execution methods implemented

### Do-Not-Do-Yet

- No live account connection (ever)
- No order placement (never)

---

## Phase 8 — Observability Polish

**Goal:** Polish the observability stack — improve audit feed UI, add log viewer widget, improve health polling reliability, add per-widget error boundaries.

**Branch:** `feat/observability-polish`

**Dependencies:** Phase 7 complete

### Tasks

| Task | Owner |
|---|---|
| Error boundaries for all dashboard widgets | Codex |
| Improved audit feed with filtering | Codex |
| Log viewer widget (MCP `mellytrade.logs_tail`) | Codex |
| Health poll retry logic | Codex |
| Dashboard loading states | Codex |
| Audit feed export (JSON download) | Codex |

### Acceptance Criteria

- No widget crash propagates to full dashboard crash
- Audit feed filterable by event type
- Log viewer shows last 50 lines; refreshable
- Loading spinners on all data-fetching widgets

---

## Phase 9 — Quant Research Lab *(Future / TBD)*

**Goal:** A separate research environment for backtesting, signal analysis, and strategy development — completely separate from the trading system.

**Status:** Not planned in detail. Future initiative.

**Constraints:**
- Research environment must never share a process with the trading system
- No research tool may place orders or affect live state
- Data access is read-only historical data only
- No connection to live broker accounts

**Not started. Not designed. Do not implement.**

---

## Rollout Safety Checklist

Before beginning each phase, confirm:

- [ ] Previous phase PRs reviewed and merged by human
- [ ] `git pull --ff-only origin main` succeeds
- [ ] `py -3.11 -m pytest tests/app/ -q` passes
- [ ] `py -3.11 scripts/validate_safety_config.py` passes
- [ ] Safety flags verified: `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`
- [ ] No open PRs with execution code awaiting merge
- [ ] Branch created from clean main
