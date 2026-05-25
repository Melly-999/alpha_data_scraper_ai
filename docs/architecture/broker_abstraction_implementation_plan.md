# MellyTrade — Broker Abstraction Implementation Plan

A focused architecture and implementation plan for the broker abstraction
layer. **This document is a plan, not a record of completed work.** As of
`main` at `e758f18`, none of the components below are implemented; they
are planned for the steps named in `docs/roadmap/mellytrade_next_20_steps.md`
(Phase B, Steps 8–13).

---

## Why broker abstraction must come before IBKR

Building IBKR support directly into `app/api/routes/ibkr.py` would lock
the dashboard's UX to one broker's quirks and would replicate any safety
plumbing per adapter. A thin `BrokerAdapter` layer:

1. **Surfaces capabilities uniformly.** Every adapter answers the same
   question the same way: am I connected? am I paper or live? do I
   permit execution? are live orders blocked? The Dashboard can render
   any adapter without per-broker code.
2. **Forces safety at the type level.** The protocol deliberately
   omits `place_order` / `cancel_order` / `modify_order`. A future
   adapter author **cannot** add those methods without changing the
   protocol — and changing the protocol is a deliberate, reviewed,
   safety-relevant act.
3. **Enables the safe-disconnected default.** With abstraction, the
   dashboard works perfectly even when no real broker is reachable.
   Without abstraction, every page that touches broker state has to
   handle "broker missing" itself.
4. **Decouples test surface from real network.** Adapters are mockable
   at the protocol boundary; tests don't need a live IBKR Gateway.

**Implication:** PR #57 (SAFE-001) → `BrokerAdapter` protocol →
safe-disconnected default → schemas → registry → endpoints → frontend
card → MT5 wrapper → IBKR skeleton. Strict order.

---

## Component overview

```
┌──────────────────────────────────────────────────────────────────┐
│                   Dashboard (read-only frontend)                 │
│                                                                  │
│  <BrokerCard adapter="safe-disconnected" />                      │
│  <BrokerCard adapter="ibkr-paper" />                             │
│  <BrokerCard adapter="mt5-paper" />                              │
└──────────────────────────────────────────────────────────────────┘
                  ▲           ▲             ▲
                  │  GET-only │             │
                  │  apiGet() │             │
                  ▼           ▼             ▼
┌──────────────────────────────────────────────────────────────────┐
│              GET-only HTTP endpoints (FastAPI)                   │
│                                                                  │
│  GET /api/brokers                                                │
│  GET /api/brokers/{id}/status                                    │
│  GET /api/brokers/{id}/account                                   │
│  GET /api/brokers/{id}/positions                                 │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Broker registry                            │
│                                                                  │
│  registry.list()      → ["safe-disconnected", "mt5-paper", ...]  │
│  registry.get(id)     → <BrokerAdapter instance>                 │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            BrokerAdapter Protocol (no execution methods)         │
│                                                                  │
│  id() → str                                                      │
│  capabilities() → BrokerCapabilities                             │
│  status() → BrokerStatus                                         │
│  account_snapshot() → BrokerAccount                              │
│  positions() → list[BrokerPosition]                              │
│                                                                  │
│  ┌──────────────────────────────┬────────────────────────────┐   │
│  │ SafeDisconnectedBrokerAdapter│ MT5PaperAdapter            │   │
│  │   (default fallback)         │   (read-only)              │   │
│  └──────────────────────────────┴────────────────────────────┘   │
│                                  │                               │
│                  ┌───────────────┴───────────────┐               │
│                  │      IBKRPaperAdapter         │               │
│                  │      (read-only, paper)       │               │
│                  └───────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

---

## `BrokerAdapter` protocol design

Defined in `brokers/protocol.py` as a `typing.Protocol` (preferred over
`ABC` so we don't force inheritance on third-party clients):

```python
from __future__ import annotations
from typing import Protocol, runtime_checkable

from app.schemas.broker import (
    BrokerCapabilities,
    BrokerStatus,
    BrokerAccount,
    BrokerPosition,
)


@runtime_checkable
class BrokerAdapter(Protocol):
    """Read-only broker contract. No execution methods, by design."""

    def id(self) -> str: ...
    def capabilities(self) -> BrokerCapabilities: ...
    def status(self) -> BrokerStatus: ...
    def account_snapshot(self) -> BrokerAccount: ...
    def positions(self) -> list[BrokerPosition]: ...
```

**Explicit non-features**:

> **The `BrokerAdapter` protocol must NOT expose `place_order`,
> `cancel_order`, `modify_order`, `submit_order`, `execute`, or any other
> live trading method. Adding such a method is a protocol-level safety
> change requiring its own review and tests.**

A test in `tests/app/test_broker_protocol.py` enforces this by asserting
that `BrokerAdapter.__annotations__` does **not** contain any of those
names.

---

## `SafeDisconnectedBrokerAdapter`

The default no-op adapter, registered out of the box. Returns a
realistic-looking but inert response so the UI can render without a real
broker. Lives in `brokers/safe_disconnected.py`.

```python
class SafeDisconnectedBrokerAdapter:
    def id(self) -> str:
        return "safe-disconnected"

    def capabilities(self) -> BrokerCapabilities:
        return BrokerCapabilities(
            read_only=True,
            paper=True,
            execution_enabled=False,
            live_orders_blocked=True,
            safety_note=(
                "Default safe-disconnected adapter. No real broker is "
                "configured; the dashboard renders an inert state."
            ),
        )

    def status(self) -> BrokerStatus:
        return BrokerStatus(
            id=self.id(),
            connected=False,
            last_heartbeat=None,
            latency_ms=None,
            degraded_reason="No broker configured",
        )

    def account_snapshot(self) -> BrokerAccount:
        # All zeros, currency placeholder.
        return BrokerAccount(cash=0.0, buying_power=0.0, equity=0.0, currency="USD")

    def positions(self) -> list[BrokerPosition]:
        return []
```

---

## Schemas

All schemas use Pydantic v2 with `model_config = ConfigDict(extra="forbid")`.
None contain execution-shaped fields. Live in `app/schemas/broker.py`.

### `BrokerCapabilities`

| Field | Type | Notes |
|---|---|---|
| `read_only` | `bool` | Always `True` for Terminal V1. |
| `paper` | `bool` | `True` if the adapter is paper-trading; `False` if live (V1: never `False`). |
| `execution_enabled` | `bool` | **Hardcoded `False` for Terminal V1.** |
| `live_orders_blocked` | `bool` | **Hardcoded `True` for Terminal V1.** |
| `safety_note` | `str` | Short human explanation. |

### `BrokerStatus`

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | Adapter id (e.g. `"ibkr-paper"`). |
| `connected` | `bool` | True iff a heartbeat was received within TTL. |
| `last_heartbeat` | `datetime \| None` | UTC. |
| `latency_ms` | `int \| None` | Round-trip; null when disconnected. |
| `degraded_reason` | `str \| None` | Human-readable; null when healthy. |

### `BrokerAccount`

| Field | Type | Notes |
|---|---|---|
| `cash` | `float` | Account cash balance. |
| `buying_power` | `float` | Available buying power. |
| `equity` | `float` | Total account equity. |
| `currency` | `str` | ISO 4217. |

**No `account_id` field** — it's a privacy / leakage risk in screenshots.
Adapters store the account id internally for reconciliation but the
public schema does not expose it.

### `BrokerPosition`

| Field | Type | Notes |
|---|---|---|
| `symbol` | `str` | Instrument identifier. |
| `quantity` | `float` | Signed: positive = long, negative = short. |
| `avg_price` | `float` | Average fill price. |
| `unrealized_pnl` | `float` | Mark-to-market unrealised P/L. |

**No `order_id`, `ticket`, `status`, `filled_at` field.** Positions are
*current state*, not order history.

---

## Broker registry

`brokers/registry.py`. Single source of truth for which adapters are
registered.

```python
class BrokerRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, BrokerAdapter] = {}

    def register(self, adapter: BrokerAdapter) -> None:
        self._adapters[adapter.id()] = adapter

    def list(self) -> list[BrokerAdapter]:
        return list(self._adapters.values())

    def get(self, broker_id: str) -> BrokerAdapter | None:
        return self._adapters.get(broker_id)


def build_default_registry() -> BrokerRegistry:
    """Always includes safe-disconnected. Other adapters opt in."""
    registry = BrokerRegistry()
    registry.register(SafeDisconnectedBrokerAdapter())
    return registry
```

The `AppContainer` wires up the registry at startup. Adapters that need
external dependencies (MT5 module, IBKR Gateway) are conditionally
registered based on import / config success.

---

## GET-only HTTP endpoints

Defined in `app/api/routes/brokers.py` (note: a separate file from the
existing `app/api/routes/broker.py` which serves the legacy single-broker
endpoints; the new file uses the **plural** `brokers` namespace).

| Method | Path | Response |
|---|---|---|
| `GET` | `/api/brokers` | List of `{id, capabilities}` for every registered adapter. |
| `GET` | `/api/brokers/{id}/status` | `BrokerStatus` for one adapter. 404 if unknown id. |
| `GET` | `/api/brokers/{id}/account` | `BrokerAccount` for one adapter. 404 if unknown id. |
| `GET` | `/api/brokers/{id}/positions` | `list[BrokerPosition]` for one adapter. 404 if unknown id. |

**Test contract** (parametrized):

- `GET` returns 200 for every registered adapter.
- `POST/PUT/DELETE/PATCH` against any of these paths returns **405**.
- Schema responses validate (round-trip via the model).
- 404 for unknown `id`.

These four endpoints will be picked up automatically by the existing
`test_terminal_v1_prefixes_are_get_only` test in
`tests/app/test_safety_invariants.py` — failure to keep them GET-only
will fail the safety regression suite.

---

## Frontend GET-only broker client

`frontend/src/hooks/useBroker.ts` extension:

```typescript
import { apiGet } from "../lib/api";
import type {
  BrokerListItem, BrokerStatus, BrokerAccount, BrokerPosition,
} from "../types/api";
import { usePollingResource } from "./usePollingResource";

const POLL_MS = 10_000;

export function useBrokers() {
  return usePollingResource(() => apiGet<BrokerListItem[]>("/brokers"), POLL_MS);
}

export function useBrokerStatus(id: string) {
  return usePollingResource(
    () => apiGet<BrokerStatus>(`/brokers/${id}/status`),
    POLL_MS,
  );
}

export function useBrokerAccount(id: string) {
  return usePollingResource(
    () => apiGet<BrokerAccount>(`/brokers/${id}/account`),
    POLL_MS,
  );
}

export function useBrokerPositions(id: string) {
  return usePollingResource(
    () => apiGet<BrokerPosition[]>(`/brokers/${id}/positions`),
    POLL_MS,
  );
}
```

There is **no** `apiPost` / `apiPut` / `apiDelete` import in this hook.
The existing safety regression test
(`test_terminal_pages_do_not_import_mutating_api_helpers`) extends
naturally to assert this.

---

## `<BrokerCard>` component plan

`frontend/src/components/cards/BrokerCard.tsx`. Single shared component
reused per broker. Uses the existing shared `<Card>`, `<Badge>`,
`<ResourceState>` building blocks.

Visual:

```
╔═══════════════════════════════════════════════════════╗
║ Interactive Brokers (paper)                  ●        ║
║                                                       ║
║ [READ-ONLY]  [PAPER]  [LIVE ORDERS BLOCKED]  [GET]    ║
║                                                       ║
║ Status:    Connected  ·  37 ms                        ║
║ Cash:      USD 100,000                                ║
║ Equity:    USD 100,000                                ║
║ Buying P:  USD 400,000                                ║
║ Positions: 0                                          ║
║                                                       ║
║ Last updated at 14:23:51                              ║
╚═══════════════════════════════════════════════════════╝
```

- `●` colour: green = connected, amber = degraded, red = disconnected.
- `[READ-ONLY]` / `[PAPER]` / `[LIVE ORDERS BLOCKED]` are derived from
  `capabilities()`. They are never overridable from the frontend.
- **No "Trade" button. No "New Order" affordance. No clickable rows.**
  The card is data-only.

When the adapter reports `connected=false`, the body switches to the
`<ResourceState>` "Backend unavailable" panel (degraded variant). The
header capability pills remain visible.

---

## MT5 adapter plan

Wraps the existing `app/services/mt5_service.py` in the new protocol.
Lives in `brokers/mt5_paper.py`.

- **Connection check:** wraps `mt5.initialize()` in try/except; returns
  `connected=False` with a `degraded_reason` if the import fails or the
  terminal isn't running.
- **Account snapshot:** maps `mt5.account_info()` → `BrokerAccount`.
- **Positions:** maps `mt5.positions_get()` → `list[BrokerPosition]`.
  Filters out closed positions.
- **No write methods.** The adapter must not call `mt5.order_send()`
  even from a private helper. Static analysis (a grep test in
  `tests/app/test_mt5_adapter.py`) will assert this.

The existing `mt5_service.py` keeps its current interface so legacy
`MT5BridgePage` continues to work; the broker abstraction is additive.

---

## IBKR read-only paper adapter plan

Lives in `brokers/ibkr_paper.py`. Builds on the existing
`docs/IBKR_PAPER_ADAPTER.md` design but constrained to the read-only
contract.

- **Library choice:** `ib_insync` (or `ib_async` successor) is the
  recommended client; verified at PR-time.
- **Connection:** `IB()` instance, `connect(host, port, client_id)`.
  Default port `7497` for TWS paper, `4002` for Gateway paper.
- **Disconnected fallback:** if `connect()` raises, the adapter reports
  `connected=False` and a populated `degraded_reason`. **No exception
  bubbles to the route.**
- **Account / positions:** read-only via `accountValues()` and
  `positions()`. Mapped to the broker schemas.
- **No order methods.** The adapter must not import `Order`,
  `MarketOrder`, `LimitOrder`, `placeOrder`, or any other execution
  symbol from `ib_insync`. A static grep test enforces this.

For full phase plan see `docs/roadmap/ibkr_read_only_phase_plan.md`.

---

## Tests required

| Test file | Asserts |
|---|---|
| `tests/app/test_broker_protocol.py` | `BrokerAdapter` doesn't declare execution methods; `runtime_checkable` works against the safe-disconnected adapter. |
| `tests/app/test_broker_safe_disconnected.py` | Capability flags correct; empty positions; populated `safety_note`; `connected=False`. |
| `tests/app/test_broker_schemas.py` | `extra="forbid"` round-trip; no order-shaped field accepted; required fields enforced. |
| `tests/app/test_broker_registry.py` | Default contains `["safe-disconnected"]`; `get()` returns `None` for unknown id; multiple registrations work. |
| `tests/app/test_broker_routes.py` | All four GET endpoints return 200; POST/PUT/DELETE/PATCH return 405; 404 for unknown id; response models validate. |
| `tests/app/test_mt5_adapter.py` | Mocked `MetaTrader5` import; disconnected fallback works; no `mt5.order_send` reference in the adapter source. |
| `tests/app/test_ibkr_adapter.py` | Mocked IB client; disconnected fallback works; no order-symbol imports in the adapter source. |

The full app suite must remain ≥ existing baseline (158 after PR #57)
+ the new tests added by each phase step.

---

## Failure modes & safe degradation

| Failure | Safe behaviour |
|---|---|
| `MetaTrader5` module not installed | MT5 adapter not registered. Registry still returns safe-disconnected. UI continues to render. |
| MT5 terminal not running | Adapter registered but `status()` returns `connected=False`, `degraded_reason="MT5 terminal not reachable"`. UI shows degraded card. |
| TWS / IB Gateway not running | IBKR adapter `connect()` raises; caught; adapter returns `connected=False`. UI shows degraded card. |
| TWS port wrong | Same as above. |
| Network blip mid-session | Adapter reports `degraded_reason="last heartbeat 37 s ago"`; UI shows amber pill but does not remove the card. |
| Adapter throws during a method call | Caught at the route layer; route returns `503` with a structured error. The card switches to `<ResourceState>` error panel. |
| Adapter returns malformed data | Pydantic validation fails; route returns `500`; the card shows the standard error panel. |

**No failure mode triggers an order, a write, or a connection retry storm.** Reconnection is bounded (exponential backoff with cap; documented in the adapter's `__init__`).

---

## "No execution" policy

The following are explicitly **out of scope** for this entire layer and
must never be added:

- `place_order`, `cancel_order`, `modify_order`, `submit_order`,
  `execute_order` methods on the protocol or any concrete adapter.
- HTTP `POST/PUT/DELETE/PATCH` routes anywhere under `/api/brokers/*`.
- Any frontend hook that calls a mutating endpoint.
- Any UI button that submits an order.
- Storage of order intent in any schema.
- Any field on `BrokerPosition` that conveys *order* state (`order_id`,
  `ticket`, `filled_at`, `status`).

Adding any of the above will fail the safety regression suite and
must be discussed as a separate, escalation-level change.

---

## Future extension map

After Terminal V1 ships and broker abstraction stabilises, possible
extensions (each its own multi-PR milestone, each requiring explicit
human approval):

1. **Read-only order history** — a *new* `BrokerOrderHistory` schema
   for *closed* orders only. Dry-run journal style. Strictly historical.
2. **Multi-account display** — adapter reports `accounts()`; UI shows
   a per-account selector. Still no execution.
3. **OAuth / token-rotated credentials** — credentials in OS keychain,
   never repo. Tested via mock.
4. **Dry-run order simulation** — `OrderIntent` / `OrderPreview` /
   `DryRunExecutionResult` schemas (DRY-001..003 in backlog). **Still
   no live execution.**
5. **Live execution** — far future; explicitly gated by
   `execution_enabled` capability flag, manual approval flow, kill
   switch, and a separate safety review. Not in any current roadmap
   horizon.

---

**Last updated**: 2026-05-09
