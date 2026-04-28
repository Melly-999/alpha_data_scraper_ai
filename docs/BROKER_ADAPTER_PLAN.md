# Broker Adapter Plan

Status: **v1 - paper-first scaffold landed**.

## Why this exists

The repository historically had two parallel broker layers:

1. `brokers/broker_interface.py` + `brokers/broker_factory.py` -
   the legacy interface; imports `ib_insync` at module load time via
   `brokers/ibkr_broker.py`. Crashes on machines without `ib_insync`.
2. `brokers/base.py` + `brokers/factory.py` - an aspirational typed
   factory referencing modules (`mt5_adapter`, `ibkr_adapter`,
   `binance_adapter`) that do not yet exist.

Neither layer is safe to expose from the FastAPI app: a missing
optional dependency (or a typo in the brokers config) would prevent the
app from starting.

The new safety-first layer (this document) introduces a small,
typed, paper-only contract that the FastAPI surface and example runner
can rely on without touching either legacy layer.

## Flow

```
SignalCandidate -> ExecutionDecision -> BrokerAdapter -> ExecutionReport
```

* `SignalCandidate` lives upstream in the AI / signal pipeline.
* `ExecutionDecision` is the lightweight dataclass in
  `brokers/adapter_models.py` (decoupled from the heavier execution
  manager so adapters can be unit-tested in isolation).
* `BrokerAdapter` is the `PaperBrokerAdapter` Protocol in
  `brokers/paper_factory.py`.
* `BrokerExecutionReport` is the dry-run report returned by the
  adapter; never an order confirmation.

## v1 deliverables (this branch)

* `brokers/adapter_models.py` - typed `BrokerHealth`,
  `BrokerAccountSnapshot`, `BrokerExecutionReport`, `ExecutionDecision`.
* `brokers/ibkr_paper.py` - `IBKRPaperAdapter` with optional
  `ib_insync` import and explicit live-port refusal.
* `brokers/paper_factory.py` - `get_paper_broker_adapter()` and a
  typed `_NullPaperAdapter` fallback.
* `app/api/routes/broker.py` - `/api/broker/health`,
  `/api/broker/account`, `/api/broker/dry-run-report`.
* `app/schemas/broker.py` - Pydantic mirrors of the adapter models.
* `.env.example` - non-secret IBKR placeholders.
* `example_runner.py` - `--broker ibkr-paper` demo path.
* `docs/IBKR_PAPER_ADAPTER.md` - operator runbook.
* `tests/test_broker_adapter_models.py`,
  `tests/test_ibkr_paper_adapter.py`,
  `tests/app/test_broker_routes.py`.

## What was deliberately not done in v1

* No edits to `brokers/ibkr_broker.py` (legacy, hard `ib_insync`
  dependency). It is unused on the safe path; cleaning it up belongs
  in a separate refactor.
* No edits to `brokers/factory.py` (aspirational, references missing
  modules). Same reasoning.
* No live IBKR order placement. `IBKRPaperAdapter.supports_live_orders()`
  is hard-coded to `False`.
* No paper bracket orders. `place_paper_bracket_order()` returns a
  refusal documented in the operator runbook.
* No changes to `config.json`, the risk state machine, drawdown guard,
  cooldowns, duplicate-signal guard, or max-open-position limit.

## Future work

* Consolidate the legacy `brokers/ibkr_broker.py` into the safe
  adapter once the unsafe `from ib_insync import *` callers are
  removed.
* Implement `place_paper_bracket_order()` behind
  `IBKR_ALLOW_PAPER_ORDERS=true` with full SL/TP enforcement and
  per-order value caps.
* Add an MT5 adapter that satisfies the same Protocol so the FastAPI
  surface can return real MT5 health when `MetaTrader5` is installed.
* Wire `ExecutionManager` to optionally request a dry-run report from
  the active adapter after the existing risk gates approve a signal.
