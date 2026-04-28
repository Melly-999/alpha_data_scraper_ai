"""Safe factory for the paper-first broker adapter layer.

This is intentionally separate from the legacy
:mod:`brokers.broker_factory` (which imports ``ib_insync`` at module
load time via :mod:`brokers.ibkr_broker`) and from the aspirational
:mod:`brokers.factory` (which references adapter modules that do not
exist yet). Importing this module never imports ``ib_insync`` and the
returned adapters are always safe to call.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Protocol, runtime_checkable

from brokers.adapter_models import (
    BrokerAccountSnapshot,
    BrokerExecutionReport,
    BrokerHealth,
    ExecutionDecision,
)
from brokers.ibkr_paper import ADAPTER_NAME as IBKR_PAPER_NAME
from brokers.ibkr_paper import IBKRPaperAdapter

logger = logging.getLogger("trading.brokers.paper_factory")


@runtime_checkable
class PaperBrokerAdapter(Protocol):
    """Minimal surface every safe broker adapter must expose."""

    name: str

    def connect(self) -> BrokerHealth: ...

    def disconnect(self) -> None: ...

    def health(self) -> BrokerHealth: ...

    def account_snapshot(self) -> BrokerAccountSnapshot: ...

    def submit_dry_run_report(
        self, decision: ExecutionDecision
    ) -> BrokerExecutionReport: ...

    def supports_live_orders(self) -> bool: ...


class _NullPaperAdapter:
    """Safe default returned when no broker is selected.

    Useful for environments that only run the MT5 demo path - the
    FastAPI broker routes can still answer with a typed disabled
    payload instead of raising.
    """

    name = "mt5_demo"

    def connect(self) -> BrokerHealth:
        return self.health()

    def disconnect(self) -> None:
        return None

    def health(self) -> BrokerHealth:
        return BrokerHealth(
            adapter=self.name,
            mode="disabled",
            connected=False,
            host="-",
            port=0,
            client_id=0,
            read_only=True,
            supports_live_orders=False,
            last_error=None,
            status="disabled",
        )

    def account_snapshot(self) -> BrokerAccountSnapshot:
        return BrokerAccountSnapshot(
            adapter=self.name,
            connected=False,
            account=None,
            last_error="adapter_disabled",
        )

    def submit_dry_run_report(
        self, decision: ExecutionDecision
    ) -> BrokerExecutionReport:
        return BrokerExecutionReport(
            adapter=self.name,
            broker=self.name,
            dry_run=True,
            accepted=False,
            decision_id=decision.decision_id,
            signal_id=decision.signal_id,
            symbol=decision.symbol,
            direction=decision.direction,
            confidence=decision.confidence,
            quantity=decision.quantity,
            sl=decision.sl,
            tp=decision.tp,
            reason="adapter_disabled",
            payload={},
        )

    def supports_live_orders(self) -> bool:
        return False


# Public registry of names this factory can build. Adding entries here
# does *not* import the underlying module until the name is requested.
KNOWN_ADAPTERS: tuple[str, ...] = ("mt5_demo", "ibkr-paper", "ibkr_paper")


def normalise_name(name: str | None) -> str:
    return (name or "").strip().lower().replace("_", "-")


def get_paper_broker_adapter(
    name: str | None = None,
    *,
    overrides: dict[str, Any] | None = None,
) -> PaperBrokerAdapter:
    """Return a safe broker adapter for the given name.

    Falls back to a typed disabled adapter for unknown or empty names so
    the FastAPI surface keeps a stable response shape. Never raises on a
    missing optional dependency - the adapter itself reports the issue
    via :meth:`health`.
    """
    selected = normalise_name(name) or normalise_name(os.getenv("BROKER_ADAPTER"))
    if selected in {"ibkr-paper", IBKR_PAPER_NAME}:
        adapter = IBKRPaperAdapter.from_env(**(overrides or {}))
        return adapter
    if selected in {"mt5-demo", "mt5", "", "none"}:
        return _NullPaperAdapter()
    logger.info("Unknown paper broker adapter '%s', using safe default", name)
    return _NullPaperAdapter()
