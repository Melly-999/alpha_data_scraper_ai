# brokers/registry.py
"""BRK-007 — Read-only :class:`BrokerRegistry`.

A small in-memory registry that holds read-only broker adapters
implementing :class:`brokers.protocol.BrokerAdapter`.

Design contract:

* Read-only. No execution / order / risk-mutation methods.
* No FastAPI routes, no network calls, no broker SDK imports
  (``MetaTrader5``, ``ib_insync``, ``ibapi``, ``alpaca``, ``ccxt``,
  ``requests``, ``httpx``, ``websockets``).
* Default registry contains a safe disconnected adapter and optional
  read-only adapters:
  :class:`brokers.safe_disconnected.SafeDisconnectedBrokerAdapter`,
  registered under the id ``"safe-disconnected"``, which is also the
  default, and read-only broker integrations such as
  :class:`brokers.ibkr_paper_readonly.IBKRPaperReadOnlyAdapter`.
  The default registry can never return an executable adapter.
* ``get()`` raises :class:`KeyError` for unknown ids;
  ``get_optional()`` returns ``None`` for callers that prefer that
  shape.
* Future BRK-XXX tasks can ``register()`` additional read-only
  adapters (MT5 read-only, IBKR Paper read-only, ...). The default
  factory stays safe by construction.
"""

from __future__ import annotations

from typing import Iterable

from .ibkr_readonly_client import (
    IBKRPaperReadOnlyClient,
    ibkr_paper_config_from_env,
    ibkr_paper_readonly_enabled,
)
from .ibkr_paper_readonly import IBKRPaperReadOnlyAdapter
from .protocol import BrokerAdapter
from .safe_disconnected import SafeDisconnectedBrokerAdapter

DEFAULT_ADAPTER_ID: str = "safe-disconnected"


class BrokerRegistry:
    """In-memory read-only registry of :class:`BrokerAdapter` instances."""

    def __init__(self, default_adapter_id: str = DEFAULT_ADAPTER_ID) -> None:
        self._adapters: dict[str, BrokerAdapter] = {}
        self._default_adapter_id: str = default_adapter_id

    # ------------------------------------------------------------------
    # Registration (local, in-memory only)
    # ------------------------------------------------------------------
    def register(self, adapter: BrokerAdapter) -> None:
        """Add ``adapter`` to the registry, keyed by its ``adapter_id``.

        Raises :class:`ValueError` on duplicate ids — re-registering a
        running adapter under the same id is almost always a bug.
        """
        adapter_id = adapter.adapter_id
        if not isinstance(adapter_id, str) or not adapter_id:
            raise ValueError("adapter.adapter_id must be a non-empty string")
        if adapter_id in self._adapters:
            raise ValueError(f"adapter_id already registered: {adapter_id!r}")
        self._adapters[adapter_id] = adapter

    # ------------------------------------------------------------------
    # Read-only access
    # ------------------------------------------------------------------
    def has(self, adapter_id: str) -> bool:
        return adapter_id in self._adapters

    def get(self, adapter_id: str) -> BrokerAdapter:
        try:
            return self._adapters[adapter_id]
        except KeyError as exc:  # re-raise with a clearer message
            known = sorted(self._adapters)
            raise KeyError(
                f"No broker adapter registered with id {adapter_id!r}. "
                f"Known ids: {known!r}"
            ) from exc

    def get_optional(self, adapter_id: str) -> BrokerAdapter | None:
        return self._adapters.get(adapter_id)

    def get_default(self) -> BrokerAdapter:
        return self.get(self._default_adapter_id)

    @property
    def default_adapter_id(self) -> str:
        return self._default_adapter_id

    def list_adapter_ids(self) -> list[str]:
        return sorted(self._adapters)

    def list_adapters(self) -> list[BrokerAdapter]:
        # Sorted by adapter_id for deterministic ordering.
        return [self._adapters[name] for name in self.list_adapter_ids()]

    def __contains__(self, adapter_id: object) -> bool:
        return isinstance(adapter_id, str) and adapter_id in self._adapters

    def __len__(self) -> int:
        return len(self._adapters)

    def __iter__(self) -> Iterable[str]:  # type: ignore[override]
        return iter(self.list_adapter_ids())


# ---------------------------------------------------------------------------
# Default factory
# ---------------------------------------------------------------------------
def _create_ibkr_paper_adapter() -> IBKRPaperReadOnlyAdapter:
    """Create the optional IBKR Paper read-only adapter safely.

    Real local TWS/Gateway reads are disabled unless
    ``IBKR_PAPER_READONLY_ENABLED=true``. If env parsing or client
    construction fails, the registry falls back to the no-client safe
    disconnected adapter.
    """
    if not ibkr_paper_readonly_enabled():
        return IBKRPaperReadOnlyAdapter()

    try:
        config = ibkr_paper_config_from_env()
        client = IBKRPaperReadOnlyClient(config=config)
    except Exception:
        return IBKRPaperReadOnlyAdapter()

    return IBKRPaperReadOnlyAdapter(config=config, readonly_client=client)


def create_default_registry() -> BrokerRegistry:
    """Build a fresh registry containing read-only broker adapters.

    A new instance is returned on every call so tests and callers cannot
    accidentally share mutable state.
    """
    registry = BrokerRegistry(default_adapter_id=DEFAULT_ADAPTER_ID)
    registry.register(SafeDisconnectedBrokerAdapter())
    registry.register(_create_ibkr_paper_adapter())
    return registry


def default_broker_registry() -> BrokerRegistry:
    """Alias for :func:`create_default_registry` to match either naming."""
    return create_default_registry()


__all__ = [
    "BrokerRegistry",
    "DEFAULT_ADAPTER_ID",
    "create_default_registry",
    "default_broker_registry",
]
