# brokers/ibkr_readonly_client.py
"""Optional local IBKR Paper read-only client wrapper.

This module is import-safe when ``ib_insync`` is missing. It contains no
execution surface and never reads credentials. A socket connection is
attempted only when a runtime caller injects this client into
``IBKRPaperReadOnlyAdapter`` and asks for status/account/positions.

The wrapper is intentionally smaller than a broker adapter. It exposes
the same duck-typed read-only interface the existing adapter already
accepts from tests:

* ``connected`` / ``is_connected()``
* ``account_snapshot()``
* ``positions()``

It does not expose order, cancel, modify, buy, sell, connect, or
disconnect methods.
"""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .ibkr_config import IBKRPaperConfig

PAPER_PORTS: frozenset[int] = frozenset({7497, 4002})
LOCAL_HOSTS: frozenset[str] = frozenset({"127.0.0.1", "localhost", "::1"})


def _bool_env(name: str, default: bool, env: Mapping[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    raw = source.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int, env: Mapping[str, str] | None = None) -> int:
    source = env if env is not None else os.environ
    raw = source.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float_env(
    name: str, default: float, env: Mapping[str, str] | None = None
) -> float:
    source = env if env is not None else os.environ
    raw = source.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def ibkr_paper_readonly_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Return true only for the explicit opt-in runtime flag."""
    return _bool_env("IBKR_PAPER_READONLY_ENABLED", False, env)


def ibkr_paper_config_from_env(
    env: Mapping[str, str] | None = None,
) -> IBKRPaperConfig:
    """Build safe non-secret config from IBKR Paper read-only env vars."""
    source = env if env is not None else os.environ
    return IBKRPaperConfig(
        host=source.get("IBKR_PAPER_HOST", "127.0.0.1") or "127.0.0.1",
        port=_int_env("IBKR_PAPER_PORT", 7497, source),
        client_id=_int_env("IBKR_PAPER_CLIENT_ID", 101, source),
        timeout_s=_float_env("IBKR_PAPER_TIMEOUT_S", 5.0, source),
        enabled=ibkr_paper_readonly_enabled(source),
        paper=True,
        read_only=True,
    )


def _finite_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out != out or out in (float("inf"), float("-inf")):
        return None
    return out


def _summary_rows_to_account(summary: object) -> Mapping[str, Any] | None:
    if not isinstance(summary, (list, tuple)):
        return None

    values: dict[str, str] = {}
    currency = "USD"
    for row in summary:
        tag = getattr(row, "tag", None)
        value = getattr(row, "value", None)
        row_currency = getattr(row, "currency", None)
        if tag is not None and value is not None:
            values[str(tag)] = str(value)
        if isinstance(row_currency, str) and row_currency:
            currency = row_currency

    def read(tag: str) -> float:
        return _finite_float(values.get(tag)) or 0.0

    return {
        "currency": currency,
        "cash": read("TotalCashValue"),
        "equity": read("NetLiquidation"),
        "buying_power": read("BuyingPower"),
    }


def _position_to_mapping(position: object) -> Mapping[str, Any] | None:
    contract = getattr(position, "contract", None)
    symbol = getattr(contract, "symbol", None)
    if not isinstance(symbol, str) or not symbol:
        return None

    quantity = _finite_float(getattr(position, "position", None))
    if quantity is None:
        return None

    out: dict[str, Any] = {
        "symbol": symbol,
        "quantity": quantity,
    }

    average_price = _finite_float(getattr(position, "avgCost", None))
    if average_price is not None:
        out["average_price"] = average_price

    currency = getattr(contract, "currency", None)
    if isinstance(currency, str) and currency:
        out["currency"] = currency

    return out


@dataclass
class IBKRPaperReadOnlyClient:
    """Local TWS/Gateway Paper read-only client.

    Constructor performs no network I/O. The first status/account/position
    read may attempt a localhost paper-port socket connection if the
    config is explicitly enabled and safe.
    """

    config: IBKRPaperConfig = field(default_factory=IBKRPaperConfig)
    ib_factory: Callable[[], Any] | None = None
    module_loader: Callable[[str], Any] = importlib.import_module
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    _ib: Any = field(default=None, init=False, repr=False)
    _last_error: str | None = field(default=None, init=False, repr=False)

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def connected(self) -> bool:
        return self.is_connected()

    def is_connected(self) -> bool:
        session = self._ensure_session()
        if session is None:
            return False
        try:
            return bool(session.isConnected())
        except Exception as exc:
            self._last_error = f"status_failed: {exc.__class__.__name__}"
            return False

    def account_snapshot(self) -> Mapping[str, Any] | None:
        session = self._ensure_session()
        if session is None:
            return None
        try:
            return _summary_rows_to_account(list(session.accountSummary()))
        except Exception as exc:
            self._last_error = f"account_snapshot_failed: {exc.__class__.__name__}"
            return None

    def positions(self) -> list[Mapping[str, Any]]:
        session = self._ensure_session()
        if session is None:
            return []
        try:
            raw_positions = list(session.positions())
        except Exception as exc:
            self._last_error = f"positions_failed: {exc.__class__.__name__}"
            return []

        out: list[Mapping[str, Any]] = []
        for position in raw_positions:
            mapped = _position_to_mapping(position)
            if mapped is not None:
                out.append(mapped)
        return out

    def _ensure_session(self) -> Any | None:
        if self._ib is not None:
            return self._ib if self._session_connected(self._ib) else None

        block_reason = self._configuration_block_reason()
        if block_reason is not None:
            self._last_error = block_reason
            return None

        try:
            session = self._new_session()
            session.connect(
                self.config.host,
                self.config.port,
                clientId=self.config.client_id,
                readonly=True,
                timeout=self.config.timeout_s,
            )
        except ImportError:
            self._last_error = "missing_dependency"
            return None
        except Exception as exc:
            self._last_error = f"connect_failed: {exc.__class__.__name__}"
            return None

        if not self._session_connected(session):
            self._last_error = "connect_failed: not_connected"
            return None

        self._ib = session
        self._last_error = None
        return self._ib

    def _new_session(self) -> Any:
        if self.ib_factory is not None:
            return self.ib_factory()
        module = self.module_loader("ib_insync")
        return module.IB()

    def _configuration_block_reason(self) -> str | None:
        if self.config.enabled is not True:
            return "disabled"
        if self.config.paper is not True or self.config.read_only is not True:
            return "unsafe_config"
        if self.config.host not in LOCAL_HOSTS:
            return "non_local_host_blocked"
        if self.config.port not in PAPER_PORTS:
            return "non_paper_port_blocked"
        return None

    @staticmethod
    def _session_connected(session: Any) -> bool:
        try:
            return bool(session.isConnected())
        except Exception:
            return False


__all__ = [
    "IBKRPaperReadOnlyClient",
    "PAPER_PORTS",
    "ibkr_paper_config_from_env",
    "ibkr_paper_readonly_enabled",
]
