from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any

from gui import render_console, run_live_gui
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import MT5Fetcher
from mt5_trader import MT5AutoTrader
from signal_generator import generate_signal, signal_to_dict


def _default_config() -> dict[str, Any]:
    return {
        "symbol": "EURUSD",
        "timeframe": "M5",
        "bars": 700,
        "lookback": 30,
        "epochs": 2,
        "autotrade": {
            "enabled": False,
            "dry_run": True,
            "min_confidence": 70.0,
            "volume": 0.01,
            "deviation": 20,
            "sl_points": 200,
            "tp_points": 300,
            "magic": 20260327,
            "cooldown_seconds": 60,
            "allow_same_signal": False,
        },
    }


def _load_config(path: str = "config.json") -> dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.exists() or cfg_path.read_text(encoding="utf-8").strip() == "":
        return _default_config()
    try:
        loaded = json.loads(cfg_path.read_text(encoding="utf-8"))
        merged = _default_config()
        merged.update(loaded)
        if isinstance(loaded.get("autotrade"), dict):
            merged_autotrade = dict(merged.get("autotrade", {}))
            merged_autotrade.update(loaded["autotrade"])
            merged["autotrade"] = merged_autotrade
        return merged
    except Exception:
        return _default_config()


class AppRuntime:
    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        autotrade_cfg = cfg.get("autotrade", {})
        self.trader = MT5AutoTrader(
            symbol=str(cfg.get("symbol", "EURUSD")),
            enabled=bool(autotrade_cfg.get("enabled", False)),
            dry_run=bool(autotrade_cfg.get("dry_run", True)),
            min_confidence=float(autotrade_cfg.get("min_confidence", 70.0)),
            volume=float(autotrade_cfg.get("volume", 0.01)),
            deviation=int(autotrade_cfg.get("deviation", 20)),
            sl_points=int(autotrade_cfg.get("sl_points", 200)),
            tp_points=int(autotrade_cfg.get("tp_points", 300)),
            magic=int(autotrade_cfg.get("magic", 20260327)),
        )
        self.cooldown_seconds = int(autotrade_cfg.get("cooldown_seconds", 60))
        self.allow_same_signal = bool(autotrade_cfg.get("allow_same_signal", False))
        self.last_trade_ts: float = 0.0
        self.last_trade_signal: str = ""

    def next_snapshot(self) -> dict[str, Any]:
        snapshot = _build_snapshot(self.cfg)
        snapshot["autotrade"] = self._maybe_trade(snapshot)
        return snapshot

    def _maybe_trade(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        signal_data = snapshot.get("signal", {})
        signal = str(signal_data.get("signal", "HOLD")).upper()
        confidence = float(signal_data.get("confidence", 0.0))

        if signal not in {"BUY", "SELL"}:
            return {"status": "no_trade_signal", "signal": signal}

        now_ts = time.time()
        if self.cooldown_seconds > 0 and (now_ts - self.last_trade_ts) < self.cooldown_seconds:
            return {
                "status": "cooldown",
                "seconds_left": round(self.cooldown_seconds - (now_ts - self.last_trade_ts), 1),
            }

        if not self.allow_same_signal and signal == self.last_trade_signal:
            return {"status": "same_signal_blocked", "signal": signal}

        result = self.trader.maybe_execute(signal=signal, confidence=confidence)
        if result.get("status") in {"placed", "dry_run"}:
            self.last_trade_ts = now_ts
            self.last_trade_signal = signal
        return result


def _build_snapshot(cfg: dict[str, Any]) -> dict[str, Any]:
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

    return {
        "symbol": cfg.get("symbol", "EURUSD"),
        "timeframe": cfg.get("timeframe", "M5"),
        "last_close": round(float(latest["close"]), 6),
        "lstm_delta": round(float(lstm_delta), 6),
        "signal": signal_to_dict(signal),
        "rows": int(len(data)),
    }


def _clear_console() -> None:
    subprocess.run(
        "cls" if os.name == "nt" else "clear",
        shell=True,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Alpha AI snapshot renderer")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to config JSON file (e.g. profiles/paper_safe.json)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run in live window GUI mode",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run in continuous loop mode",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Seconds between snapshots in continuous mode (overrides config interval)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = _load_config(args.config)
    runtime = AppRuntime(cfg)
    interval = float(args.interval if args.interval is not None else cfg.get("interval", 5.0))

    if args.gui:
        if interval <= 0:
            raise ValueError("--interval must be greater than 0")
        run_live_gui(runtime.next_snapshot, interval_seconds=interval)
        return

    if not args.continuous:
        snapshot = runtime.next_snapshot()
        render_console(snapshot)
        return

    if interval <= 0:
        raise ValueError("--interval must be greater than 0")

    try:
        while True:
            snapshot = runtime.next_snapshot()
            _clear_console()
            render_console(snapshot)
            print(f"\nNext update in {interval:.1f}s (Ctrl+C to stop)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped continuous mode.")


if __name__ == "__main__":
    main()
