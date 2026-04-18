"""Adapter between the alpha_data_scraper_ai LSTM pipeline and the MT5 bridge.

The adapter loads the model referenced by env vars (``ALPHA_REPO_PATH`` +
``ALPHA_LSTM_CLASS`` or ``ALPHA_LSTM_FUNCTION``) at first use and converts
its output into a trading action. The ``LSTMPipeline`` shipped with the
alpha repo is stateful — it requires ``fit`` to run before
``predict_next_delta`` — so the adapter caches one instance per class and
runs ``fit`` on the first usable OHLCV batch. If anything goes wrong
(module missing, DataFrame malformed, model untrained, predict error) the
adapter falls back to ``HOLD`` with a low confidence so the backend's risk
gates simply reject the signal.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Optional

log = logging.getLogger(__name__)

Action = Literal["BUY", "SELL", "HOLD"]

REQUIRED_COLUMNS = ("close", "open", "high", "low")
OPTIONAL_COLUMNS = ("volume",)
MIN_BARS = 40
DEFAULT_THRESHOLD = 1e-4  # relative close delta that triggers BUY/SELL

_instance_cache: dict[str, Any] = {}
_cache_lock = threading.Lock()


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


def _import_attr(ref: str) -> Any:
    module_name, attr = ref.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def _resolve_instance() -> Optional[Any]:
    """Return a model instance (or function) or None if misconfigured.

    Instances are cached per class reference so the LSTM is only fit once
    per process. Functions are returned directly.
    """
    _add_repo_to_syspath()
    func_ref = os.getenv("ALPHA_LSTM_FUNCTION")
    if func_ref:
        try:
            return _import_attr(func_ref)
        except Exception as exc:
            log.warning("LSTM adapter: cannot resolve function %s (%s)", func_ref, exc)
            return None

    cls_ref = os.getenv("ALPHA_LSTM_CLASS", "lstm_model.LSTMPipeline")
    with _cache_lock:
        if cls_ref in _instance_cache:
            return _instance_cache[cls_ref]
        try:
            cls = _import_attr(cls_ref)
            instance = cls()
        except Exception as exc:
            log.warning("LSTM adapter: cannot resolve class %s (%s)", cls_ref, exc)
            return None
        _instance_cache[cls_ref] = instance
        return instance


def reset_cache() -> None:
    """Drop any cached model instances. Intended for tests."""
    with _cache_lock:
        _instance_cache.clear()


def _validate_frame(frame: Any) -> Optional[str]:
    if frame is None:
        return "no_ohlcv"
    try:
        cols = {c.lower() for c in frame.columns}
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


def _prepare_frame(frame: Any) -> Any:
    """Lower-case columns and reorder so ``close`` is first (expected by
    ``LSTMPipeline.predict_next_delta(close_col_index=0)``).

    Non-numeric columns such as MT5 timestamps are dropped because the
    bundled ``LSTMPipeline`` feeds raw ``DataFrame.values`` into a scaler.
    """
    renamed = frame.rename(columns={c: c.lower() for c in frame.columns})
    ordered = list(REQUIRED_COLUMNS)
    for extra in OPTIONAL_COLUMNS:
        if extra in renamed.columns and extra not in ordered:
            ordered.append(extra)
    return renamed[ordered]


def _invoke_model(instance: Any, frame: Any) -> float:
    """Call the best available prediction path on ``instance``.

    Order of preference:
    1. ``fit(frame) + predict_next_delta(frame)`` — stateful pipeline
       (``lstm_model.LSTMPipeline``). Fit is invoked once; subsequent
       calls only predict.
    2. ``predict_next_delta(frame)`` — stateless pipeline already trained.
    3. ``predict(frame)`` / ``instance(frame)`` — generic callable.
    """
    if (
        callable(instance)
        and not hasattr(instance, "predict_next_delta")
        and not hasattr(instance, "predict")
    ):
        return float(instance(frame))

    if hasattr(instance, "predict_next_delta"):
        needs_fit = (
            hasattr(instance, "fit") and getattr(instance, "model", None) is None
        )
        if needs_fit:
            instance.fit(frame)
        return float(instance.predict_next_delta(frame))

    if hasattr(instance, "predict"):
        result = instance.predict(frame)
        try:
            return float(result)
        except TypeError:
            # Numpy array or similar — take last scalar.
            return float(result[-1])

    if callable(instance):
        return float(instance(frame))

    raise TypeError(f"Unsupported model type: {type(instance)!r}")


def predict_signal(
    ohlcv: Any,
    threshold: float = DEFAULT_THRESHOLD,
    predict_fn: Optional[Callable[..., Any]] = None,
) -> AdapterSignal:
    """Run the configured LSTM and return a structured :class:`AdapterSignal`."""
    err = _validate_frame(ohlcv)
    if err is not None:
        return AdapterSignal("HOLD", 33.0, 0.0, reason=f"fallback:{err}")

    frame = _prepare_frame(ohlcv)

    if predict_fn is not None:
        try:
            delta = float(predict_fn(frame))
        except Exception as exc:
            return AdapterSignal(
                "HOLD", 33.0, 0.0, reason=f"fallback:predict_error:{exc}"
            )
    else:
        instance = _resolve_instance()
        if instance is None:
            return AdapterSignal("HOLD", 33.0, 0.0, reason="fallback:no_model")
        try:
            delta = _invoke_model(instance, frame)
        except Exception as exc:
            return AdapterSignal(
                "HOLD", 33.0, 0.0, reason=f"fallback:predict_error:{exc}"
            )

    close = float(frame["close"].iloc[-1])
    action = _delta_to_action(delta, close, threshold)
    rel = abs(delta) / close if close else 0.0
    confidence = max(33.0, min(85.0, 50.0 + rel * 10000))
    return AdapterSignal(action=action, confidence=confidence, predicted_delta=delta)
