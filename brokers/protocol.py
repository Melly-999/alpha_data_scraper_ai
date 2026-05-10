# brokers/protocol.py
"""BRK-001 — Read-only ``BrokerAdapter`` protocol.

This module defines a *read-only* :class:`BrokerAdapter` Protocol that
future broker integrations (``SafeDisconnectedBrokerAdapter``, MT5
read-only, IBKR Paper read-only, ...) must implement.

Safety contract — preserved by construction:
- No execution / order placement methods.
- No autotrade / dry-run mutation methods.
- No risk-policy mutation methods.
- Pure data-read surface only.

The protocol is intentionally narrow. Typed return schemas
(``AccountSnapshot``, ``Position``, ``Capabilities``, ...) will be
introduced by a follow-up task (BRK-003); for now the protocol uses
``Mapping[str, Any]`` so callers can already depend on the *shape* of
the contract without forcing a schema decision today.

The legacy :class:`brokers.base.BrokerAdapter` Protocol (which exposes
``place_order``) is unrelated to this read-only protocol and is left
untouched. The two live in different modules on purpose.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Lightweight type aliases — temporary placeholders.
# BRK-003 will replace these with typed dataclasses / pydantic schemas.
# ---------------------------------------------------------------------------
AdapterCapabilities = Mapping[str, Any]
AdapterStatus = Mapping[str, Any]
AccountSnapshot = Mapping[str, Any]
PositionSnapshot = Mapping[str, Any]


@runtime_checkable
class BrokerAdapter(Protocol):
    """Read-only broker adapter contract.

    Implementations expose only data-read methods. They MUST NOT expose
    any order-placement, order-modification, position-mutation,
    autotrade-toggle, or risk-policy-mutation method.
    """

    @property
    def adapter_id(self) -> str:
        """Stable identifier for this adapter (e.g. ``"mt5_readonly"``)."""
        ...

    def capabilities(self) -> AdapterCapabilities:
        """Return a read-only description of what this adapter supports."""
        ...

    def status(self) -> AdapterStatus:
        """Return a read-only health/connection status snapshot."""
        ...

    def account_snapshot(self) -> AccountSnapshot:
        """Return a read-only snapshot of account-level fields."""
        ...

    def positions(self) -> list[PositionSnapshot]:
        """Return a read-only list of current positions."""
        ...


# ---------------------------------------------------------------------------
# Forbidden method names — checked by ``tests/app/test_broker_adapter_protocol.py``.
# Defined here as the single source of truth so the test cannot drift
# from the safety contract.
# ---------------------------------------------------------------------------
FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
    "place_order",
    "cancel_order",
    "modify_order",
    "execute",
    "submit_order",
    "close_position",
    "open_position",
    "broker_execute",
    "enable_autotrade",
    "disable_dry_run",
    "change_config_runtime",
    "modify_risk_policy",
)


EXPECTED_READ_ONLY_METHOD_NAMES: tuple[str, ...] = (
    "adapter_id",
    "capabilities",
    "status",
    "account_snapshot",
    "positions",
)


__all__ = [
    "BrokerAdapter",
    "AdapterCapabilities",
    "AdapterStatus",
    "AccountSnapshot",
    "PositionSnapshot",
    "FORBIDDEN_METHOD_NAMES",
    "EXPECTED_READ_ONLY_METHOD_NAMES",
]
