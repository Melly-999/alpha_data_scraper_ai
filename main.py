# Copyright 2025-2026 Mati (Melly-999)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, cast

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from gui import render_console, run_live_gui
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import batch_fetch
from mt5_trader import MT5AutoTrader
from signal_generator import generate_signal, signal_to_dict
from utils.risk_manager import RiskManager


DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "XAUUSD"]


def _sync_risk_from_mt5(risk: RiskManager) -> None:
    try:
        import MetaTrader5 as mt5  # type: ignore
    except Exception:
        return

    if not mt5.initialize():
        return

    try:
        account = mt5.account_info()
        if account is None:
            return
        risk.update_balance(account.balance)
    finally:
        mt5.shutdown()


def _default_config() -> dict[str, Any]:
    return {
        "symbols": DEFAULT_SYMBOLS,
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
        # Backward compat: "symbol" (str) → "symbols" (list)
        if "symbols" not in merged and "symbol" in merged:
            merged["symbols"] = [merged["symbol"]]
        elif "symbols" not in merged:
            merged["symbols"] = DEFAULT_SYMBOLS
        if isinstance(merged.get("symbols"), str):
            merged["symbols"] = [merged["symbols"]]
        return merged
    except Exception:
        return _default_config()


class AppRuntime:
    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.autotrade_cfg = cfg.get("autotrade", {})
        self.symbols: list[str] = list(cfg.get("symbols", DEFAULT_SYMBOLS))
        self.risk = RiskManager()
        self.auto_trading_enabled = bool(self.autotrade_cfg.get("enabled", False))

        # One MT5AutoTrader per symbol, all sharing the same autotrade params
        self.traders: dict[str, MT5AutoTrader] = {
            sym: self._create_trader(sym, idx)
            for idx, sym in enumerate(self.symbols)
        }

        self.cooldown_seconds = int(self.autotrade_cfg.get("cooldown_seconds", 60))
        self.allow_same_signal = bool(self.autotrade_cfg.get("allow_same_signal", False))
        # Per-symbol trade state
        self.last_trade_ts: dict[str, float] = {sym: 0.0 for sym in self.symbols}
        self.last_trade_signal: dict[str, str] = {sym: "" for sym in self.symbols}

    def _create_trader(self, symbol: str, magic_offset: int) -> MT5AutoTrader:
        return MT5AutoTrader(
            symbol=symbol,
            enabled=self.auto_trading_enabled,
            dry_run=bool(self.autotrade_cfg.get("dry_run", True)),
            min_confidence=float(self.autotrade_cfg.get("min_confidence", 70.0)),
            volume=float(self.autotrade_cfg.get("volume", 0.01)),
            deviation=int(self.autotrade_cfg.get("deviation", 20)),
            sl_points=int(self.autotrade_cfg.get("sl_points", 200)),
            tp_points=int(self.autotrade_cfg.get("tp_points", 300)),
            magic=int(self.autotrade_cfg.get("magic", 20260327)) + magic_offset,
        )

    def _set_traders_enabled(self, enabled: bool) -> None:
        for trader in self.traders.values():
            trader.enabled = enabled

    def set_auto_trading(self, enabled: bool) -> tuple[bool, str]:
        can_trade, reason = self.risk.can_trade()
        if enabled and not can_trade:
            self.auto_trading_enabled = False
            self._set_traders_enabled(False)
            return False, reason

        self.auto_trading_enabled = enabled
        self._set_traders_enabled(enabled)
        return True, "ON" if enabled else "OFF"

    def _risk_status_view(self) -> dict[str, Any]:
        can_trade, reason = self.risk.can_trade()
        status = cast(dict[str, Any], self.risk.get_status())
        status["can_trade"] = can_trade
        status["reason"] = reason
        return status

    def next_snapshots(self) -> list[dict[str, Any]]:
        """Fetch all symbols (one MT5 session) then analyse in parallel."""
        _sync_risk_from_mt5(self.risk)
        raw_data = batch_fetch(
            symbols=self.symbols,
            timeframe=str(self.cfg.get("timeframe", "M5")),
            bars=int(self.cfg.get("bars", 700)),
        )
        snapshots = _build_multi_snapshots(self.cfg, raw_data)
        for snap in snapshots:
            sym = snap.get("symbol", "")
            snap["autotrade"] = self._maybe_trade(sym, snap)
            snap["risk_status"] = self._risk_status_view()
            snap["auto_trading_enabled"] = self.auto_trading_enabled
        return snapshots

    # Keep backward-compat single-snapshot method
    def next_snapshot(self) -> dict[str, Any]:
        snaps = self.next_snapshots()
        return snaps[0] if snaps else {}

    def _maybe_trade(self, symbol: str, snapshot: dict[str, Any]) -> dict[str, Any]:
        trader = self.traders.get(symbol)
        if trader is None:
            return {"status": "no_trader"}

        signal_data = snapshot.get("signal", {})
        signal = str(signal_data.get("signal", "HOLD")).upper()
        confidence = float(signal_data.get("confidence", 0.0))

        can_trade, reason = self.risk.can_trade()
        if not can_trade:
            if isinstance(signal_data, dict):
                signal_data["signal"] = None
                signal_data["confidence"] = 0.0
            signal = None
            confidence = 0.0
            self.auto_trading_enabled = False
            self._set_traders_enabled(False)
            return {"status": "risk_blocked", "reason": reason}

        if not self.auto_trading_enabled:
            return {"status": "auto_trading_off"}

        if signal not in {"BUY", "SELL"}:
            return {"status": "no_trade_signal", "signal": signal}

        now_ts = time.time()
        last_ts = self.last_trade_ts.get(symbol, 0.0)
        if self.cooldown_seconds > 0 and (now_ts - last_ts) < self.cooldown_seconds:
            return {
                "status": "cooldown",
                "seconds_left": round(self.cooldown_seconds - (now_ts - last_ts), 1),
            }

        if not self.allow_same_signal and signal == self.last_trade_signal.get(symbol, ""):
            return {"status": "same_signal_blocked", "signal": signal}

        balance = float(self.risk.current_balance)
        lot = self.risk.calculate_lot_size(balance, sl_pips=trader.sl_points)
        trader.volume = lot
        result = trader.maybe_execute(signal=signal, confidence=confidence)
        result["lot"] = lot
        result["sl"] = trader.sl_points
        result["tp"] = trader.tp_points
        if result.get("status") in {"placed", "dry_run"}:
            profit = float(result.get("profit", 0.0))
            self.risk.register_trade(profit)
            self.last_trade_ts[symbol] = now_ts
            self.last_trade_signal[symbol] = signal
        return result


def _analyse_symbol(
    symbol: str,
    raw: Any,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Run indicators + LSTM + signal generation for one symbol (CPU-bound)."""
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
        "symbol": symbol,
        "timeframe": cfg.get("timeframe", "M5"),
        "last_close": round(float(latest["close"]), 6),
        "lstm_delta": round(float(lstm_delta), 6),
        "signal": signal_to_dict(signal),
        "rows": int(len(data)),
    }


def _build_multi_snapshots(
    cfg: dict[str, Any],
    raw_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Analyse all symbols in parallel using a thread pool (CPU-bound LSTM work)."""
    symbols = list(raw_data.keys())
    results: dict[str, dict[str, Any]] = {}

    with ThreadPoolExecutor(max_workers=min(len(symbols), 6)) as pool:
        futures = {
            pool.submit(_analyse_symbol, sym, raw_data[sym], cfg): sym
            for sym in symbols
        }
        for future in as_completed(futures):
            sym = futures[future]
            try:
                results[sym] = future.result()
            except Exception as exc:
                results[sym] = {
                    "symbol": sym,
                    "error": str(exc),
                    "signal": {"signal": "HOLD", "confidence": 0.0, "score": 0, "reasons": []},
                }

    # Preserve original symbol order
    return [results[sym] for sym in symbols if sym in results]


def _build_snapshot(cfg: dict[str, Any]) -> dict[str, Any]:
    """Single-symbol snapshot (legacy compatibility)."""
    symbols: list[str] = list(cfg.get("symbols", DEFAULT_SYMBOLS))
    raw_data = batch_fetch(
        symbols=[symbols[0]],
        timeframe=str(cfg.get("timeframe", "M5")),
        bars=int(cfg.get("bars", 700)),
    )
    snaps = _build_multi_snapshots(cfg, raw_data)
    return snaps[0] if snaps else {}


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
        run_live_gui(runtime.next_snapshots, interval_seconds=interval)
        return

    if not args.continuous:
        snapshots = runtime.next_snapshots()
        render_console(snapshots)
        return

    if interval <= 0:
        raise ValueError("--interval must be greater than 0")

    try:
        while True:
            snapshots = runtime.next_snapshots()
            _clear_console()
            render_console(snapshots)
            print(f"Next update in {interval:.1f}s (Ctrl+C to stop)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped continuous mode.")


if __name__ == "__main__":
    main()
