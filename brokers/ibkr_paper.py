"""Safety-first Interactive Brokers Paper Adapter (v1).

This adapter is **paper / dry-run first**:

* It imports cleanly even when ``ib_insync`` is not installed.
* It refuses to open a connection to a live TWS / IB Gateway port unless
  ``allow_live_orders`` is explicitly set, which is wired off by default.
* It never places live orders. ``submit_dry_run_report`` produces a
  :class:`BrokerExecutionReport` instead of an order, and the optional
  paper bracket helper is documented as future work.
* All credentials are expected to come from a manually-launched TWS /
  IB Gateway session - this module never reads usernames or passwords.

The legacy :mod:`brokers.ibkr_broker` module (``from ib_insync import *``
at top level) is left untouched. New code should depend on this module
instead so the FastAPI app keeps starting in environments without IBKR.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from brokers.adapter_models import (
    BrokerAccountSnapshot,
    BrokerExecutionReport,
    BrokerHealth,
    ExecutionDecision,
)

logger = logging.getLogger("trading.brokers.ibkr_paper")

# --- optional dependency --------------------------------------------------
try:  # pragma: no cover - environment dependent
    import ib_insync  # type: ignore  # noqa: F401

    _HAS_IB_INSYNC = True
except Exception:  # pragma: no cover - missing dependency is the default in CI
    ib_insync = None  # type: ignore[assignment]
    _HAS_IB_INSYNC = False


PAPER_PORTS: frozenset[int] = frozenset({7497, 4002})
LIVE_PORTS: frozenset[int] = frozenset({7496, 4001})

ADAPTER_NAME = "ibkr_paper"
BROKER_NAME = "ibkr_paper"


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass
class IBKRPaperConfig:
    """Configuration for :class:`IBKRPaperAdapter`."""

    enabled: bool = False
    mode: str = "paper"
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 1
    account: str | None = None
    read_only: bool = True
    allow_paper_orders: bool = False
    allow_live_orders: bool = False
    max_order_value: float = 100.0
    max_position_value: float = 100.0
    timeout_seconds: float = 4.0

    @classmethod
    def from_env(cls, **overrides: Any) -> "IBKRPaperConfig":
        cfg = cls(
            enabled=_bool_env("IBKR_ENABLED", False),
            mode=os.getenv("IBKR_MODE", "paper").strip().lower() or "paper",
            host=os.getenv("IBKR_HOST", "127.0.0.1") or "127.0.0.1",
            port=_int_env("IBKR_PORT", 7497),
            client_id=_int_env("IBKR_CLIENT_ID", 1),
            account=(os.getenv("IBKR_ACCOUNT") or None),
            read_only=_bool_env("IBKR_READ_ONLY", True),
            allow_paper_orders=_bool_env("IBKR_ALLOW_PAPER_ORDERS", False),
            allow_live_orders=_bool_env("IBKR_ALLOW_LIVE_ORDERS", False),
            max_order_value=_float_env("IBKR_MAX_ORDER_VALUE", 100.0),
            max_position_value=_float_env("IBKR_MAX_POSITION_VALUE", 100.0),
        )
        if overrides:
            for key, value in overrides.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
        return cfg


@dataclass
class IBKRPaperAdapter:
    """Paper-first IBKR adapter.

    The constructor performs no I/O; :meth:`connect` is the only method
    that may touch the network and it gracefully degrades when:

    * ``ib_insync`` is missing,
    * TWS / IB Gateway is not running,
    * the configured port is a live port and ``allow_live_orders`` is
      ``False`` (default),
    * the adapter is disabled in configuration.
    """

    config: IBKRPaperConfig = field(default_factory=IBKRPaperConfig)
    name: str = ADAPTER_NAME
    _ib: Any = field(default=None, init=False, repr=False)
    _connected: bool = field(default=False, init=False, repr=False)
    _last_error: str | None = field(default=None, init=False, repr=False)
    _connect_attempted: bool = field(default=False, init=False, repr=False)

    # --- factory helpers --------------------------------------------------
    @classmethod
    def from_env(cls, **overrides: Any) -> "IBKRPaperAdapter":
        return cls(config=IBKRPaperConfig.from_env(**overrides))

    # --- properties -------------------------------------------------------
    @property
    def connected(self) -> bool:
        if self._ib is None:
            return False
        try:
            is_connected = bool(self._ib.isConnected())
        except Exception:  # pragma: no cover - depends on ib_insync internals
            is_connected = False
        self._connected = is_connected
        return is_connected

    def supports_live_orders(self) -> bool:
        # v1 adapter is paper / dry-run only. Live remains explicitly blocked.
        return False

    # --- safety gates -----------------------------------------------------
    def _live_blocked(self) -> str | None:
        """Return a block reason if live trading is being requested."""
        if self.config.mode != "paper":
            return f"live_mode_blocked: mode={self.config.mode}"
        if self.config.port in LIVE_PORTS and not self.config.allow_live_orders:
            return f"live_port_blocked: port={self.config.port}"
        if self.config.allow_live_orders:
            return "live_orders_disabled_in_v1"
        return None

    def _execution_blocked(self) -> str | None:
        """Return a block reason that refuses any execution attempt."""
        if not self.config.enabled:
            return "adapter_disabled"
        return self._live_blocked()

    def _missing_dependency(self) -> str | None:
        if not _HAS_IB_INSYNC:
            return "missing_dependency: ib_insync not installed"
        return None

    # --- lifecycle --------------------------------------------------------
    def connect(self) -> BrokerHealth:
        """Attempt to connect to TWS / IB Gateway. Always safe to call."""
        self._connect_attempted = True
        self._last_error = None

        if not self.config.enabled:
            self._last_error = "adapter_disabled"
            return self.health(status="disabled")

        live_block = self._live_blocked()
        if live_block:
            self._last_error = live_block
            logger.warning("IBKR paper adapter blocked live mode: %s", live_block)
            return self.health(status="live_blocked")

        missing = self._missing_dependency()
        if missing:
            self._last_error = missing
            logger.info("IBKR paper adapter cannot connect: %s", missing)
            return self.health(status="missing_dependency")

        try:  # pragma: no cover - requires real ib_insync + TWS
            from ib_insync import IB  # type: ignore

            self._ib = IB()
            self._ib.connect(
                self.config.host,
                self.config.port,
                clientId=self.config.client_id,
                readonly=self.config.read_only,
                timeout=self.config.timeout_seconds,
            )
            self._connected = self._ib.isConnected()
            self._last_error = None
            logger.info(
                "IBKR paper adapter connected host=%s port=%s client_id=%s",
                self.config.host,
                self.config.port,
                self.config.client_id,
            )
            return self.health(status="connected")
        except Exception as exc:  # pragma: no cover - depends on TWS state
            self._connected = False
            self._last_error = f"connect_failed: {exc.__class__.__name__}: {exc}"
            logger.warning("IBKR paper adapter connect failed: %s", self._last_error)
            return self.health(status="connect_failed")

    def disconnect(self) -> None:
        if self._ib is None:
            return
        try:  # pragma: no cover - depends on ib_insync internals
            if self._ib.isConnected():
                self._ib.disconnect()
        except Exception as exc:  # pragma: no cover
            logger.debug("IBKR paper adapter disconnect noop: %s", exc)
        finally:
            self._connected = False

    # --- read-only surface ------------------------------------------------
    def health(self, *, status: str | None = None) -> BrokerHealth:
        if not self.config.enabled:
            mode = "disabled"
            inferred = "disabled"
        else:
            mode = self.config.mode
            inferred = self._infer_status()
        return BrokerHealth(
            adapter=ADAPTER_NAME,
            mode=mode,
            connected=self.connected,
            host=self.config.host,
            port=self.config.port,
            client_id=self.config.client_id,
            read_only=self.config.read_only,
            supports_live_orders=self.supports_live_orders(),
            last_error=self._last_error,
            status=status or inferred,
        )

    def _infer_status(self) -> str:
        err = self._last_error or ""
        if not err:
            return "connected" if self.connected else "ok"
        if err.startswith("live_port_blocked") or err.startswith("live_mode_blocked"):
            return "live_blocked"
        if err == "live_orders_disabled_in_v1":
            return "live_blocked"
        if err.startswith("missing_dependency"):
            return "missing_dependency"
        if err.startswith("connect_failed"):
            return "connect_failed"
        if err == "adapter_disabled":
            return "disabled"
        return "error"

    def account_snapshot(self) -> BrokerAccountSnapshot:
        if not self.connected or self._ib is None:
            return BrokerAccountSnapshot(
                adapter=ADAPTER_NAME,
                connected=False,
                account=self.config.account,
                last_error=self._last_error or "not_connected",
            )

        try:  # pragma: no cover - requires live ib_insync session
            summary = list(self._ib.accountSummary())
        except Exception as exc:  # pragma: no cover
            self._last_error = f"account_summary_failed: {exc}"
            return BrokerAccountSnapshot(
                adapter=ADAPTER_NAME,
                connected=False,
                account=self.config.account,
                last_error=self._last_error,
            )

        return _summary_to_snapshot(summary, self.config.account)  # pragma: no cover

    # --- execution surface ------------------------------------------------
    def submit_dry_run_report(
        self, decision: ExecutionDecision
    ) -> BrokerExecutionReport:
        """Produce a typed dry-run report. Never places an order."""
        block = self._execution_blocked()
        accepted = block is None
        reason = block or decision.reason or "dry_run_ok"

        payload: dict[str, Any] = {
            "host": self.config.host,
            "port": self.config.port,
            "client_id": self.config.client_id,
            "mode": self.config.mode,
            "read_only": self.config.read_only,
            "ib_insync_available": _HAS_IB_INSYNC,
            "decision_metadata": dict(decision.metadata),
        }

        return BrokerExecutionReport(
            adapter=ADAPTER_NAME,
            broker=BROKER_NAME,
            dry_run=True,
            accepted=accepted,
            decision_id=decision.decision_id,
            signal_id=decision.signal_id,
            symbol=decision.symbol,
            direction=decision.direction,
            confidence=decision.confidence,
            quantity=decision.quantity,
            sl=decision.sl,
            tp=decision.tp,
            reason=reason,
            payload=payload,
        )

    def place_paper_bracket_order(
        self, decision: ExecutionDecision
    ) -> BrokerExecutionReport:
        """Optional paper bracket order helper.

        v1 intentionally never places real orders. The full implementation
        is tracked in ``docs/IBKR_PAPER_ADAPTER.md`` (Future work) and is
        gated behind ``IBKR_ALLOW_PAPER_ORDERS`` and ``IBKR_MODE=paper``.
        Calling this method always returns a dry-run report explaining why.
        """
        if not self.config.allow_paper_orders:
            reason = "paper_orders_disabled"
        elif self.config.mode != "paper":
            reason = "paper_orders_require_paper_mode"
        elif not _HAS_IB_INSYNC:
            reason = "missing_dependency: ib_insync not installed"
        else:
            reason = "paper_order_placement_not_implemented_in_v1"

        report = self.submit_dry_run_report(decision)
        # Re-build with explicit reason so callers see the precise gate.
        return BrokerExecutionReport(
            adapter=report.adapter,
            broker=report.broker,
            dry_run=True,
            accepted=False,
            decision_id=report.decision_id,
            signal_id=report.signal_id,
            symbol=report.symbol,
            direction=report.direction,
            confidence=report.confidence,
            quantity=report.quantity,
            sl=report.sl,
            tp=report.tp,
            reason=reason,
            payload=report.payload,
        )


def _summary_to_snapshot(  # pragma: no cover - requires real ib_insync data
    summary: list[Any], account: str | None
) -> BrokerAccountSnapshot:
    """Translate ``ib_insync`` ``accountSummary()`` rows to a snapshot."""
    values: dict[str, str] = {}
    currency = "USD"
    for item in summary:
        tag = getattr(item, "tag", None)
        value = getattr(item, "value", None)
        cur = getattr(item, "currency", None)
        if tag and value is not None:
            values[str(tag)] = str(value)
        if cur:
            currency = str(cur)

    def _f(tag: str) -> float:
        try:
            return float(values.get(tag, "0") or 0.0)
        except ValueError:
            return 0.0

    return BrokerAccountSnapshot(
        adapter=ADAPTER_NAME,
        connected=True,
        account=account,
        currency=currency,
        net_liquidation=_f("NetLiquidation"),
        cash=_f("TotalCashValue"),
        buying_power=_f("BuyingPower"),
    )
