# brokers/__init__.py
"""Broker package.

Importing this package must never fail because of an optional broker
dependency (``ib_insync``, ``alpaca-py``, ``MetaTrader5`` ...). The
legacy :mod:`brokers.broker_factory` does ``from ib_insync import *``
through :mod:`brokers.ibkr_broker`; we re-export it lazily so the
FastAPI app and the new safe paper adapter still load on machines that
do not have those packages installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = [
    "BrokerInterface",
    "get_broker",
    "get_paper_broker_adapter",
]

# Always-safe re-exports from the new safety-first layer.
from .broker_interface import BrokerInterface
from .paper_factory import get_paper_broker_adapter

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .broker_factory import get_broker as _LegacyGetBroker  # noqa: F401


def get_broker(*args: Any, **kwargs: Any) -> Any:
    """Lazy proxy to the legacy :func:`brokers.broker_factory.get_broker`.

    Imported on first call so missing optional broker SDKs do not break
    package import. The function only raises the underlying
    ``ImportError`` if a caller actually requests it.
    """
    from .broker_factory import get_broker as _legacy_get_broker

    return _legacy_get_broker(*args, **kwargs)
