"""MT5 → MellyTrade API bridge.

Fetches OHLCV bars from MT5 (or a synthetic fallback on non-Windows
machines), asks the LSTM adapter for a direction, and POSTs the result
to the MellyTrade API. Designed so every call feeds a real OHLCV
DataFrame to the adapter — without it the adapter always returns HOLD.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx

from .lstm_signal_adapter import AdapterSignal, predict_signal

log = logging.getLogger(__name__)

REQUIRED_COLUMNS = ("open", "high", "low", "close")


@dataclass(frozen=True)
class BridgeConfig:
    api_url: str = os.getenv("MELLYTRADE_API_URL", "http://127.0.0.1:8000")
    api_key: str = os.getenv("FASTAPI_KEY", "change-me-api-key")
    symbol: str = os.getenv("MT5_SYMBOL", "EURUSD")
    timeframe: str = os.getenv("MT5_TIMEFRAME", "M5")
    bars: int = int(os.getenv("MT5_BARS", "300"))
    sl_pips: float = float(os.getenv("MT5_SL_PIPS", "20"))
    tp_pips: float = float(os.getenv("MT5_TP_PIPS", "40"))
    risk_percent: float = float(os.getenv("MT5_RISK_PERCENT", "0.5"))


def _pip_size(symbol: str) -> float:
    return 0.01 if "JPY" in symbol.upper() else 0.0001


def fetch_ohlcv(
    symbol: str,
    timeframe: str,
    bars: int,
    fetcher: Optional[Any] = None,
) -> Optional[Any]:
    """Return a DataFrame with at least the REQUIRED_COLUMNS, or None.

    When a custom `fetcher` is injected (used by tests) it is called
    instead of the alpha_data_scraper_ai `MT5Fetcher`. This keeps the
    bridge testable on Linux without MT5 installed.
    """
    if fetcher is not None:
        frame = fetcher(symbol=symbol, timeframe=timeframe, bars=bars)
        return _normalize(frame)

    try:
        from mt5_fetcher import MT5Fetcher  # type: ignore

        f = MT5Fetcher()
        frame = f.fetch(symbol=symbol, timeframe=timeframe, bars=bars)
        return _normalize(frame)
    except Exception as exc:
        log.warning("MT5 fetch failed: %s", exc)
        return None


def _normalize(frame: Any) -> Optional[Any]:
    if frame is None:
        return None
    try:
        frame = frame.rename(columns={c: c.lower() for c in frame.columns})
    except Exception:
        return None
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        log.warning("OHLCV missing columns: %s", missing)
        return None
    return frame


def build_signal_payload(
    symbol: str,
    adapter: AdapterSignal,
    last_close: float,
    config: BridgeConfig,
) -> dict:
    pip = _pip_size(symbol)
    if adapter.action == "BUY":
        sl = last_close - config.sl_pips * pip
        tp = last_close + config.tp_pips * pip
    elif adapter.action == "SELL":
        sl = last_close + config.sl_pips * pip
        tp = last_close - config.tp_pips * pip
    else:
        # HOLD keeps SL/TP valid/distinct but will be gated out by confidence.
        sl = last_close - config.sl_pips * pip
        tp = last_close + config.tp_pips * pip
    return {
        "symbol": symbol,
        "action": adapter.action,
        "confidence": round(adapter.confidence, 2),
        "risk_percent": config.risk_percent,
        "entry_price": round(last_close, 5),
        "stop_loss": round(sl, 5),
        "take_profit": round(tp, 5),
        "source": "mt5_bridge",
    }


def run_once(
    config: Optional[BridgeConfig] = None,
    fetcher: Optional[Any] = None,
    http_client: Optional[httpx.Client] = None,
) -> dict:
    """Fetch OHLCV, predict, and POST to the API. Returns a status dict."""
    cfg = config or BridgeConfig()
    frame = fetch_ohlcv(cfg.symbol, cfg.timeframe, cfg.bars, fetcher=fetcher)
    if frame is None:
        return {"status": "skipped", "reason": "no_ohlcv"}

    adapter = predict_signal(frame)
    last_close = float(frame["close"].iloc[-1])
    payload = build_signal_payload(cfg.symbol, adapter, last_close, cfg)

    if adapter.action == "HOLD":
        # Do not hit the API for HOLD; the risk gates would reject anyway.
        return {"status": "hold", "payload": payload, "reason": adapter.reason}

    client = http_client or httpx.Client(timeout=10.0)
    try:
        resp = client.post(
            f"{cfg.api_url.rstrip('/')}/signal",
            json=payload,
            headers={"X-API-Key": cfg.api_key, "Content-Type": "application/json"},
        )
        body: Any
        try:
            body = resp.json()
        except Exception:
            body = {"text": resp.text}
        return {"status": "sent", "http": resp.status_code, "body": body}
    finally:
        if http_client is None:
            client.close()


def _cli() -> int:  # pragma: no cover - thin entry point
    import json

    logging.basicConfig(
        level=os.getenv("MT5_BRIDGE_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    result = run_once()
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("status") in ("sent", "hold", "skipped") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli())
