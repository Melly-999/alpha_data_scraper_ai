# Codex Task Queue — MellyTrade Safe Full Auto AI Dev System

**Version:** 1.0.0
**Status:** Active planning queue
**Last updated:** 2026-05-09
**Safety class:** DEV-AUTOMATION — all tasks are read-only or test-only unless marked otherwise

---

## Queue Legend

| Field | Meaning |
|---|---|
| Task ID | Unique identifier; prefix indicates category |
| Scope | What the task touches |
| Allowed files | File patterns the task may create or edit |
| Forbidden changes | Explicit exclusions — must not be touched |
| Validation | How to confirm the task succeeded |
| Rollback | How to undo if something goes wrong |
| Owner | Claude Code / Codex / Human |
| Size | XS / S / M / L |
| Status | Planned / Ready / In Progress / Done / Blocked |

---

## Priority 1 — Immediate (Phase 0–1)

---

### TEST-001 — OpenAPI Forbidden Path Scan

| Field | Value |
|---|---|
| **Task ID** | TEST-001 |
| **Title** | OpenAPI forbidden path scan script |
| **Status** | Ready |
| **Scope** | Create a Python script that reads the OpenAPI schema and asserts no forbidden routes exist |
| **Allowed files** | `scripts/openapi_scan.py`, `tests/app/test_openapi_forbidden.py` |
| **Forbidden changes** | No source code, no routes, no config, no workflow YAML |
| **Validation** | `py -3.11 scripts/openapi_scan.py` exits 0; `py -3.11 -m pytest tests/app/test_openapi_forbidden.py -v` passes |
| **Rollback** | `git restore scripts/openapi_scan.py tests/app/test_openapi_forbidden.py` |
| **Safety reminder** | Script is read-only; it reads the schema, it does not create routes |
| **Suggested branch** | `test/openapi-forbidden-path-scan` |
| **Size** | S |
| **Owner** | Codex |
| **Dependencies** | Backend running or OpenAPI JSON exported |

**Forbidden routes to scan for:**
```python
FORBIDDEN_PATHS = [
    "/execute_trade", "/place_order", "/close_position",
    "/cancel_orders", "/modify_positions", "/enable_autotrade",
    "/disable_dry_run", "/modify_risk", "/broker/execute",
]
FORBIDDEN_METHODS = ["DELETE"]  # on trading-adjacent paths
```

---

### TEST-010 — Audit Filter Alignment Test

| Field | Value |
|---|---|
| **Task ID** | TEST-010 |
| **Title** | Audit event filter alignment test |
| **Status** | Ready |
| **Scope** | Verify audit event types returned by backend match defined schema constants |
| **Allowed files** | `tests/app/test_audit_filter.py` |
| **Forbidden changes** | No source code, no audit schema changes, no config |
| **Validation** | `py -3.11 -m pytest tests/app/test_audit_filter.py -v` passes |
| **Rollback** | `git restore tests/app/test_audit_filter.py` |
| **Safety reminder** | Test reads audit events via GET; does not inject or mutate events |
| **Suggested branch** | `test/audit-filter-alignment` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | TEST-001 (defines test patterns) |

---

### TEST-003 — Local Safety Config Validation Script

| Field | Value |
|---|---|
| **Task ID** | TEST-003 |
| **Title** | Local safety config validation script |
| **Status** | Ready |
| **Scope** | Script that reads config and asserts `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, `max_risk_pct <= 0.01` |
| **Allowed files** | `scripts/validate_safety_config.py` |
| **Forbidden changes** | Must not write to config; must not modify any flag |
| **Validation** | `py -3.11 scripts/validate_safety_config.py` exits 0 on safe config; exits 1 with clear error on violation |
| **Rollback** | `git restore scripts/validate_safety_config.py` |
| **Safety reminder** | Script is assertion-only; it never writes or modifies config |
| **Suggested branch** | `test/local-safety-validation` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | None |

---

### TEST-004 — Local Branch / Diff Safety Validator

| Field | Value |
|---|---|
| **Task ID** | TEST-004 |
| **Title** | Git diff docs-only validator |
| **Status** | Ready |
| **Scope** | Script that inspects `git diff --name-only` and asserts all changed files are under `docs/` or `tests/` or `scripts/` |
| **Allowed files** | `scripts/validate_diff_scope.py` |
| **Forbidden changes** | Must not modify git history; read-only git queries only |
| **Validation** | `py -3.11 scripts/validate_diff_scope.py` exits 0 when diff is docs-only |
| **Rollback** | `git restore scripts/validate_diff_scope.py` |
| **Safety reminder** | Must also scan diff for secret strings: `sk-`, `ghp_`, `password=`, `token=` with real-looking values |
| **Suggested branch** | `test/diff-scope-validator` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | None |

---

### SAFE-008 — Safety Architecture Doc

| Field | Value |
|---|---|
| **Task ID** | SAFE-008 |
| **Title** | Safety architecture decision record |
| **Status** | Ready |
| **Scope** | Document the safety architecture decisions: why `dry_run=true` is the default, how the safety gate is enforced, what breaks if any flag is changed |
| **Allowed files** | `docs/architecture/safety_architecture.md` |
| **Forbidden changes** | No source code; no config changes |
| **Validation** | File exists; references `SAFE-001` contract; includes forbidden mutation table |
| **Rollback** | `git restore docs/architecture/safety_architecture.md` |
| **Safety reminder** | Docs-only; no implementation |
| **Suggested branch** | `docs/safety-architecture` |
| **Size** | S |
| **Owner** | Claude Code |
| **Dependencies** | PR #57 (SAFE-001 contract) |

---

## Priority 2 — Broker Abstraction (Phase 6)

---

### BRK-001 — BrokerAdapter Protocol

| Field | Value |
|---|---|
| **Task ID** | BRK-001 |
| **Title** | Define `BrokerAdapter` read-only protocol |
| **Status** | Planned (Phase 6) |
| **Scope** | Python Protocol class defining the interface all broker adapters must implement. Read-only methods only: `get_status()`, `get_account_info()`, `get_positions()`, `get_open_orders()` |
| **Allowed files** | `app/brokers/protocol.py` |
| **Forbidden changes** | No execution methods (`place_order`, `cancel_order`, `modify_position`, `close_position`) — these must raise `NotImplementedError` if defined at all |
| **Validation** | `py -3.11 -m pytest tests/brokers/test_protocol.py -v` passes; scan confirms no execution method bodies |
| **Rollback** | `git restore app/brokers/protocol.py` |
| **Safety reminder** | Protocol must include docstring explicitly stating: "This adapter is read-only. Execution methods must not be implemented." |
| **Suggested branch** | `feat/broker-adapter-protocol` |
| **Size** | S |
| **Owner** | Codex |
| **Dependencies** | None |

---

### BRK-002 — SafeDisconnectedBrokerAdapter

| Field | Value |
|---|---|
| **Task ID** | BRK-002 |
| **Title** | Implement `SafeDisconnectedBrokerAdapter` |
| **Status** | Planned (Phase 6) |
| **Scope** | Concrete adapter that returns safe-default values (empty positions, disconnected status) without connecting to any broker. Used when no broker is configured. |
| **Allowed files** | `app/brokers/safe_disconnected.py` |
| **Forbidden changes** | Must not make network calls; must not import broker client libraries; must not have execution methods |
| **Validation** | `py -3.11 -m pytest tests/brokers/test_safe_disconnected.py -v` passes; confirm zero network calls via mock |
| **Rollback** | `git restore app/brokers/safe_disconnected.py` |
| **Safety reminder** | Default adapter — always safe; never throws; never calls broker |
| **Suggested branch** | `feat/safe-disconnected-broker` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | BRK-001 |

---

### BRK-003 — Broker Status Schema

| Field | Value |
|---|---|
| **Task ID** | BRK-003 |
| **Title** | Pydantic schema for broker status response |
| **Status** | Planned (Phase 6) |
| **Scope** | `BrokerStatusResponse` Pydantic model with: `connected`, `broker_name`, `account_type`, `last_heartbeat`, `error` |
| **Allowed files** | `app/brokers/schemas.py` |
| **Forbidden changes** | No execution-related fields; no secret fields |
| **Validation** | `py -3.11 -m pytest tests/brokers/test_schemas.py -v` passes |
| **Rollback** | `git restore app/brokers/schemas.py` |
| **Suggested branch** | `feat/broker-schemas` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | BRK-001 |

---

### BRK-004 — BrokerAccountInfo Schema

| Field | Value |
|---|---|
| **Task ID** | BRK-004 |
| **Title** | Pydantic schema for account info |
| **Status** | Planned (Phase 6) |
| **Scope** | `BrokerAccountInfoResponse` — balance, currency, account type (paper/demo). No credentials, no auth tokens. |
| **Allowed files** | `app/brokers/schemas.py` |
| **Forbidden changes** | No password/token/secret fields in schema |
| **Validation** | Schema serialises without exposing sensitive data |
| **Rollback** | `git restore app/brokers/schemas.py` |
| **Suggested branch** | `feat/broker-schemas` (same as BRK-003) |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | BRK-003 |

---

### BRK-005 — BrokerPositions Schema

| Field | Value |
|---|---|
| **Task ID** | BRK-005 |
| **Title** | Pydantic schema for open positions (read-only display) |
| **Status** | Planned (Phase 6) |
| **Scope** | `BrokerPositionResponse` — symbol, size, direction, entry price, unrealised PnL. Read-only display. |
| **Allowed files** | `app/brokers/schemas.py` |
| **Forbidden changes** | No mutating fields; no order ID references that could trigger cancellation |
| **Validation** | Schema serialises correctly; no forbidden fields |
| **Rollback** | `git restore app/brokers/schemas.py` |
| **Suggested branch** | `feat/broker-schemas` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | BRK-003 |

---

### BRK-006 — BrokerOpenOrders Schema

| Field | Value |
|---|---|
| **Task ID** | BRK-006 |
| **Title** | Pydantic schema for open orders display |
| **Status** | Planned (Phase 6) |
| **Scope** | `BrokerOpenOrderResponse` — read-only display of pending orders. No cancel/modify fields. |
| **Allowed files** | `app/brokers/schemas.py` |
| **Forbidden changes** | No cancel/modify actions; display-only |
| **Validation** | Schema serialises; no action triggers |
| **Rollback** | `git restore app/brokers/schemas.py` |
| **Suggested branch** | `feat/broker-schemas` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | BRK-003 |

---

### BRK-007 — BrokerAdapter Registry

| Field | Value |
|---|---|
| **Task ID** | BRK-007 |
| **Title** | BrokerAdapter registry and factory |
| **Status** | Planned (Phase 6) |
| **Scope** | Registry that maps broker name → adapter class. Default: `SafeDisconnectedBrokerAdapter`. IBKR paper adapter registered but not auto-connected. |
| **Allowed files** | `app/brokers/registry.py` |
| **Forbidden changes** | No live broker auto-connect; registry does not read credentials at import time |
| **Validation** | `py -3.11 -m pytest tests/brokers/test_registry.py -v` passes; default returns safe disconnected |
| **Rollback** | `git restore app/brokers/registry.py` |
| **Suggested branch** | `feat/broker-adapter-registry` |
| **Size** | S |
| **Owner** | Codex |
| **Dependencies** | BRK-001, BRK-002 |

---

### BRK-008 — GET /api/broker/status Endpoint

| Field | Value |
|---|---|
| **Task ID** | BRK-008 |
| **Title** | Backend GET endpoint: broker status |
| **Status** | Planned (Phase 6) |
| **Scope** | `GET /api/broker/status` — returns `BrokerStatusResponse` from registry |
| **Allowed files** | `app/routers/broker.py` |
| **Forbidden changes** | No POST/PUT/DELETE on broker routes; no execution endpoints |
| **Validation** | `py -3.11 -m pytest tests/app/test_broker_endpoints.py::test_status -v` passes; OpenAPI scan finds no forbidden routes |
| **Rollback** | `git restore app/routers/broker.py` |
| **Suggested branch** | `feat/broker-get-endpoints` |
| **Size** | S |
| **Owner** | Codex |
| **Dependencies** | BRK-007 |

---

### BRK-009 through BRK-011 — Remaining GET Broker Endpoints

| Task ID | Endpoint | Response Schema |
|---|---|---|
| BRK-009 | `GET /api/broker/account` | `BrokerAccountInfoResponse` |
| BRK-010 | `GET /api/broker/positions` | `List[BrokerPositionResponse]` |
| BRK-011 | `GET /api/broker/orders` | `List[BrokerOpenOrderResponse]` |

**All follow same pattern as BRK-008: GET only, no execution, OpenAPI scan must pass.**

**Suggested branch:** `feat/broker-get-endpoints` (same as BRK-008)
**Owner:** Codex
**Dependencies:** BRK-007, BRK-008

---

### BRK-012 — Frontend Broker API Client

| Field | Value |
|---|---|
| **Task ID** | BRK-012 |
| **Title** | Frontend GET-only broker API client |
| **Status** | Planned (Phase 6) |
| **Scope** | TypeScript fetch functions for broker GET endpoints. No POST/execute functions. |
| **Allowed files** | `frontend/src/api/brokerApi.ts` |
| **Forbidden changes** | No execute/trade/cancel functions; GET-only client |
| **Validation** | TypeScript builds without errors; no forbidden function names in file |
| **Rollback** | `git restore frontend/src/api/brokerApi.ts` |
| **Suggested branch** | `feat/broker-frontend-client` |
| **Size** | S |
| **Owner** | Codex |
| **Dependencies** | BRK-008 through BRK-011 |

---

### BRK-013 — BrokerCard Frontend Component

| Field | Value |
|---|---|
| **Task ID** | BRK-013 |
| **Title** | BrokerCard read-only frontend component |
| **Status** | Planned (Phase 6) |
| **Scope** | React component displaying broker status, account info, positions — read-only. No buttons that trigger actions. |
| **Allowed files** | `frontend/src/components/BrokerCard.tsx` |
| **Forbidden changes** | No onClick handlers that call POST/broker-execute; no order placement buttons |
| **Validation** | Component renders in isolation; no action buttons present; visual review |
| **Rollback** | `git restore frontend/src/components/BrokerCard.tsx` |
| **Suggested branch** | `feat/broker-card-component` |
| **Size** | M |
| **Owner** | Codex |
| **Dependencies** | BRK-012 |

---

## MCP Skeleton Tasks (Phase 2)

---

### MCP-001 — MCP Server Skeleton

| Field | Value |
|---|---|
| **Task ID** | MCP-001 |
| **Title** | MCP local server skeleton (disabled by default) |
| **Status** | Planned (Phase 2) |
| **Scope** | Minimal Python MCP server that starts on command only, registers allowed tools, validates tool registry at startup |
| **Allowed files** | `mellytrade_mcp/__init__.py`, `mellytrade_mcp/__main__.py`, `mellytrade_mcp/registry.py`, `mellytrade_mcp/tools/` |
| **Forbidden changes** | No write tools; no execution tools; no auto-start config |
| **Validation** | `py -3.11 -m mellytrade_mcp --list-tools` shows only allowed tools; secret scan passes |
| **Rollback** | `git restore mellytrade_mcp/` |
| **Suggested branch** | `feat/mcp-skeleton` |
| **Size** | M |
| **Owner** | Codex |
| **Dependencies** | MCP-PLAN (mcp_local_skeleton_plan.md complete) |

---

### MCP-002 — MCP Tool Registry Validator

| Field | Value |
|---|---|
| **Task ID** | MCP-002 |
| **Title** | MCP tool registry validation test |
| **Status** | Planned (Phase 2) |
| **Scope** | Test that scans registered tools and asserts zero forbidden tool names |
| **Allowed files** | `tests/mcp/test_tool_registry.py` |
| **Forbidden changes** | No new tools added; test-only |
| **Validation** | `py -3.11 -m pytest tests/mcp/test_tool_registry.py -v` passes |
| **Suggested branch** | `feat/mcp-skeleton` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | MCP-001 |

---

## Dashboard / AI Dev Control Center Tasks (Phase 3+)

---

### DEV-CC-001 — AI Dev Control Center Route Planning

| Field | Value |
|---|---|
| **Task ID** | DEV-CC-001 |
| **Title** | Plan `/dev` route and widget layout |
| **Status** | Planned (Phase 3) |
| **Scope** | Docs-only: define route structure, widget list, data sources for AI Dev Control Center |
| **Allowed files** | `docs/architecture/ai_dev_control_center.md` (already created in this sprint) |
| **Forbidden changes** | No frontend code changes |
| **Validation** | Doc exists; widget list complete; no execution widgets listed |
| **Suggested branch** | Current sprint branch |
| **Size** | XS |
| **Owner** | Claude Code |
| **Dependencies** | None (this sprint) |

---

## Observability / Audit Tasks (Phase 1–2)

---

### OBS-001 — Audit Event Constants Module

| Field | Value |
|---|---|
| **Task ID** | OBS-001 |
| **Title** | Define audit event type constants |
| **Status** | Ready |
| **Scope** | Python module with string constants for all defined audit event types |
| **Allowed files** | `app/audit/events.py` |
| **Forbidden changes** | No modification to audit emission logic; constants only |
| **Validation** | `py -3.11 -c "from app.audit.events import *; print('ok')"` passes; all event types in this doc are represented |
| **Suggested branch** | `feat/audit-event-constants` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | None |

---

### OBS-002 — Smoke Test Runner Script

| Field | Value |
|---|---|
| **Task ID** | OBS-002 |
| **Title** | Local smoke test runner script |
| **Status** | Ready |
| **Scope** | PowerShell or Python script that hits the standard smoke suite endpoints and reports pass/fail |
| **Allowed files** | `scripts/smoke_test.ps1` or `scripts/smoke_test.py` |
| **Forbidden changes** | No POST requests; GET only |
| **Validation** | `py -3.11 scripts/smoke_test.py` exits 0 when all endpoints return 200 |
| **Suggested branch** | `test/smoke-test-runner` |
| **Size** | XS |
| **Owner** | Codex |
| **Dependencies** | None |

---

## Task Queue Summary Table

| Task ID | Title | Phase | Owner | Size | Status |
|---|---|---|---|---|---|
| TEST-001 | OpenAPI forbidden path scan | 1 | Codex | S | Ready |
| TEST-003 | Safety config validation script | 1 | Codex | XS | Ready |
| TEST-004 | Git diff scope validator | 1 | Codex | XS | Ready |
| TEST-010 | Audit filter alignment test | 1 | Codex | XS | Ready |
| SAFE-008 | Safety architecture doc | 0 | Claude Code | S | Ready |
| OBS-001 | Audit event constants | 1 | Codex | XS | Ready |
| OBS-002 | Smoke test runner | 1 | Codex | XS | Ready |
| MCP-001 | MCP server skeleton | 2 | Codex | M | Planned |
| MCP-002 | MCP registry validator | 2 | Codex | XS | Planned |
| DEV-CC-001 | AI Dev Control Center route plan | 3 | Claude Code | XS | Done (this sprint) |
| BRK-001 | BrokerAdapter protocol | 6 | Codex | S | Planned |
| BRK-002 | SafeDisconnectedBrokerAdapter | 6 | Codex | XS | Planned |
| BRK-003 | Broker status schema | 6 | Codex | XS | Planned |
| BRK-004 | Account info schema | 6 | Codex | XS | Planned |
| BRK-005 | Positions schema | 6 | Codex | XS | Planned |
| BRK-006 | Open orders schema | 6 | Codex | XS | Planned |
| BRK-007 | BrokerAdapter registry | 6 | Codex | S | Planned |
| BRK-008 | GET /api/broker/status | 6 | Codex | S | Planned |
| BRK-009 | GET /api/broker/account | 6 | Codex | S | Planned |
| BRK-010 | GET /api/broker/positions | 6 | Codex | S | Planned |
| BRK-011 | GET /api/broker/orders | 6 | Codex | S | Planned |
| BRK-012 | Frontend broker API client | 6 | Codex | S | Planned |
| BRK-013 | BrokerCard component | 6 | Codex | M | Planned |
