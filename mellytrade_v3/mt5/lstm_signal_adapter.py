"""Adapter between the alpha_data_scraper_ai LSTM pipeline and the MT5 bridge.

The adapter loads the LSTM class/function referenced by env vars
(ALPHA_REPO_PATH + ALPHA_LSTM_CLASS or ALPHA_LSTM_FUNCTION) at first use
and converts its output into a trading action. If anything goes wrong
(module missing, DataFrame malformed, model untrained) it falls back to
`HOLD` with a low confidence so downstream risk gates simply reject.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Optional

log = logging.getLogger(__name__)

Action = Literal["BUY", "SELL", "HOLD"]

REQUIRED_COLUMNS = ("open", "high", "low", "close")
MIN_BARS = 40
DEFAULT_THRESHOLD = 1e-4  # relative close delta that triggers BUY/SELL


@dataclass(frozen=True)
class AdapterSignal:
    action: Action
    confidence: float
    predicted_delta: float
    reason: str = ""

    @property
    def is_fallback(self) -> bool:
        return self.action == "HOLD" and self.reason != ""


def _add_repo_to_syspath() -> None:
    repo = os.getenv("ALPHA_REPO_PATH")
    if not repo:
        return
    path = Path(repo).expanduser()
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _resolve_callable() -> Optional[Callable[..., Any]]:
    """Return the predict callable or None if misconfigured."""
    _add_repo_to_syspath()

    func_ref = os.getenv("ALPHA_LSTM_FUNCTION")
    cls_ref = os.getenv("ALPHA_LSTM_CLASS", "lstm_model.LSTMPipeline")

    try:
        if func_ref:
            module_name, attr = func_ref.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, attr)

        module_name, attr = cls_ref.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, attr)
        instance = cls()

        # Pick the first supported predict method.
        for method in ("predict_next_delta", "predict", "__call__"):
            fn = getattr(instance, method, None)
            if callable(fn):
                return fn
    except Exception as exc:
        log.warning("LSTM adapter: cannot resolve model (%s)", exc)
        return None
    return None


def _validate_frame(frame: Any) -> Optional[str]:
    if frame is None:
        return "no_ohlcv"
    try:
        cols = [c.lower() for c in frame.columns]
    except Exception:
        return "bad_frame_type"
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing:
        return f"missing_columns:{','.join(missing)}"
    if len(frame) < MIN_BARS:
        return f"not_enough_bars:{len(frame)}<{MIN_BARS}"
    return None


def _delta_to_action(delta: float, close: float, threshold: float) -> Action:
    if close <= 0:
        return "HOLD"
    rel = delta / close
    if rel > threshold:
        return "BUY"
    if rel < -threshold:
        return "SELL"
    return "HOLD"


def predict_signal(
    ohlcv: Any,
    threshold: float = DEFAULT_THRESHOLD,
    predict_fn: Optional[Callable[..., Any]] = None,
) -> AdapterSignal:
    """Run the configured LSTM and return a structured `AdapterSignal`."""
    err = _validate_frame(ohlcv)
    if err is not None:
        return AdapterSignal("HOLD", 33.0, 0.0, reason=f"fallback:{err}")

    fn = predict_fn if predict_fn is not None else _resolve_callable()
    if fn is None:
        return AdapterSignal("HOLD", 33.0, 0.0, reason="fallback:no_model")

    frame = ohlcv.rename(columns={c: c.lower() for c in ohlcv.columns})
    try:
        result = fn(frame)
    except TypeError:
        try:
            result = fn()
        except Exception as exc:
            return AdapterSignal(
                "HOLD", 33.0, 0.0, reason=f"fallback:predict_error:{exc}"
            )
    except Exception as exc:
        return AdapterSignal(
            "HOLD", 33.0, 0.0, reason=f"fallback:predict_error:{exc}"
        )

    try:
        delta = float(result)
    except Exception:
        return AdapterSignal(
            "HOLD", 33.0, 0.0, reason="fallback:non_numeric_prediction"
        )

    close = float(frame["close"].iloc[-1])
    action = _delta_to_action(delta, close, threshold)
    rel = abs(delta) / close if close else 0.0
    confidence = max(33.0, min(85.0, 50.0 + rel * 10000))
    return AdapterSignal(action=action, confidence=confidence, predicted_delta=delta)
