"""Diagnostic script: verifies MellyTrade v3 setup (LSTM + adapter).

Usage
-----
    python -m mellytrade_v3.mt5.check_setup
    # or (with PYTHONPATH set by the session-start hook):
    python mellytrade_v3/mt5/check_setup.py

Exit codes
----------
0 — everything the script could test worked (LSTM resolved, adapter
    returned BUY/SELL/HOLD on synthetic OHLCV).
1 — something failed; message is printed to stderr.

Intentionally does NOT touch the live API or network.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running as a plain script without PYTHONPATH.
HERE = Path(__file__).resolve().parent
for parent in (HERE.parent, HERE.parent.parent):
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))

from mt5 import lstm_signal_adapter  # noqa: E402  (path fix above)


def _synthetic_ohlcv(n: int = 120, drift: float = 0.0) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    base = 1.10 + np.cumsum(rng.normal(drift, 0.0003, n))
    return pd.DataFrame(
        {
            "open": base + rng.normal(0, 0.0002, n),
            "high": base + np.abs(rng.normal(0, 0.0005, n)),
            "low": base - np.abs(rng.normal(0, 0.0005, n)),
            "close": base,
            "volume": rng.integers(100, 1000, n),
        }
    )


def main() -> int:
    print("MellyTrade v3 setup check")
    print("-" * 40)
    print(f"ALPHA_REPO_PATH    = {os.getenv('ALPHA_REPO_PATH') or '(unset)'}")
    print(f"ALPHA_LSTM_CLASS   = {os.getenv('ALPHA_LSTM_CLASS') or '(default)'}")
    print(f"ALPHA_LSTM_FUNCTION= {os.getenv('ALPHA_LSTM_FUNCTION') or '(unset)'}")

    # 1) Fallback path — no OHLCV should always HOLD + is_fallback
    none_sig = lstm_signal_adapter.predict_signal(None)
    print(f"[fallback/None]    action={none_sig.action} reason={none_sig.reason}")
    if not none_sig.is_fallback or none_sig.action != "HOLD":
        print("‼ fallback path broken", file=sys.stderr)
        return 1

    # 2) Real OHLCV path — LSTMPipeline should resolve and produce a
    # clamped confidence within [33, 85]. Action can be BUY/SELL/HOLD
    # depending on the predicted delta.
    lstm_signal_adapter.reset_cache()
    frame = _synthetic_ohlcv(n=120)
    sig = lstm_signal_adapter.predict_signal(frame)
    available = not sig.reason.startswith("fallback:")
    print(
        f"[lstm/real OHLCV]  available={available} action={sig.action} "
        f"confidence={sig.confidence:.1f} delta={sig.predicted_delta:+.6f}"
    )
    if not available:
        print(f"‼ LSTM unavailable: {sig.reason}", file=sys.stderr)
        return 1
    if sig.action not in ("BUY", "SELL", "HOLD"):
        print(f"‼ unexpected action {sig.action!r}", file=sys.stderr)
        return 1
    if not 33.0 <= sig.confidence <= 85.0:
        print(f"‼ confidence out of clamp: {sig.confidence}", file=sys.stderr)
        return 1

    print("-" * 40)
    print("OK")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
