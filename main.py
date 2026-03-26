from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gui import render_console
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import MT5Fetcher
from signal_generator import generate_signal, signal_to_dict


def _load_config(path: str = "config.json") -> dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.exists() or cfg_path.read_text(encoding="utf-8").strip() == "":
        return {
            "symbol": "EURUSD",
            "timeframe": "M5",
            "bars": 700,
            "lookback": 30,
            "epochs": 2,
        }
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "symbol": "EURUSD",
            "timeframe": "M5",
            "bars": 700,
            "lookback": 30,
            "epochs": 2,
        }


def main() -> None:
    cfg = _load_config()

    fetcher = MT5Fetcher(
        symbol=cfg.get("symbol", "EURUSD"), timeframe=cfg.get("timeframe", "M5")
    )
    raw = fetcher.get_latest_rates(bars=int(cfg.get("bars", 700)))
    data = add_indicators(raw)

    feature_cols = [
        "close",
        "rsi",
        "stoch_k",
        "stoch_d",
        "macd_hist",
        "bb_pos",
        "volume",
    ]
    features: Any = data[feature_cols]

    pipeline = LSTMPipeline(
        lookback=int(cfg.get("lookback", 30)), epochs=int(cfg.get("epochs", 2))
    )
    pipeline.fit(features)
    lstm_delta = pipeline.predict_next_delta(features, close_col_index=0)

    latest = data.iloc[-1]
    signal = generate_signal(latest, lstm_delta=lstm_delta)

    snapshot: dict[str, Any] = {
        "symbol": cfg.get("symbol", "EURUSD"),
        "timeframe": cfg.get("timeframe", "M5"),
        "last_close": round(float(latest["close"]), 6),
        "lstm_delta": round(float(lstm_delta), 6),
        "signal": signal_to_dict(signal),
        "rows": int(len(data)),
    }
    render_console(snapshot)


if __name__ == "__main__":
    main()
