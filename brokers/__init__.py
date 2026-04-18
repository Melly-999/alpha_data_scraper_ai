# brokers/__init__.py
# ``get_broker`` is resolved lazily so importing ``brokers`` does not drag
# in yfinance / ib_insync / alpaca-py (any of which may be missing on CI).
from .broker_interface import BrokerInterface

__all__ = ["get_broker", "BrokerInterface"]


def get_broker(*args, **kwargs):
    from .broker_factory import get_broker as _impl

    return _impl(*args, **kwargs)
