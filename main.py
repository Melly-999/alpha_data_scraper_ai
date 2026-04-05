from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# ── Path bootstrap ────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Core imports ──────────────────────────────────────────────────────────────
from core import config as _cfg
from core.logger import get_logger
from gui import render_console, run_live_gui

# Feature 3: smarter scoring — use strategy versions for all indicator/signal work
from strategy.indicators import add_indicators
from strategy.signal_generator import generate_signal, signal_to_dict

from lstm_model import LSTMPipeline
from mt5_fetcher import batch_fetch
from mt5_trader import MT5AutoTrader
from trading_controller import TradingController

logger = get_logger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
FTMO_MODE = _cfg.FTMO_MODE
START_BALANCE = _cfg.START_BALANCE
MAX_DAILY_LOSS_PCT = _cfg.MAX_DAILY_LOSS_PCT
RISK_PER_TRADE_PCT = _cfg.RISK_PER_TRADE_PCT
PIP_VALUE_PER_LOT = _cfg.PIP_VALUE_PER_LOT
MAX_POSITION_SIZE_LOTS = _cfg.MAX_POSITION_SIZE_LOTS
ACCOUNT_BALANCE = _cfg.ACCOUNT_BALANCE
MAX_OPEN_POSITIONS = _cfg.MAX_OPEN_POSITIONS

DEFAULT_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY",
    "XAUUSD", "WTI", "NVDA", "GOOGL", "USTECH100",
]
DEFAULT_CONFIG: dict[str, Any] = {
    "symbols": DEFAULT_SYMBOLS,
    "timeframe": "M5",
    "bars": 700,
    "lookback": 30,
    "epochs": 2,
    "interval": 5.0,
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

# Feature columns for LSTM (unchanged — all present after strategy.add_indicators)
LSTM_FEATURE_COLS = [
    "close", "rsi", "stoch_k", "stoch_d", "macd_hist", "bb_pos", "volume",
]

MAX_WORKERS = 6
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

# Feature 5: global controller instance (shared with dashboard API)
controller = TradingController()


# ── Runtime risk manager ──────────────────────────────────────────────────────

class _RuntimeRiskManager:
    """Stateful risk gate used during the live trading loop.

    Tracks balance, open positions and daily PnL to enforce:
    - Max daily loss limit
    - Max simultaneous open positions
    - Risk-proportional lot sizing
    """

    def __init__(self) -> None:
        self.current_balance: float = float(ACCOUNT_BALANCE)
        self._start_balance: float = float(ACCOUNT_BALANCE)
        self._open_positions: int = 0
        self._daily_pnl: float = 0.0

    def update_balance(self, balance: float) -> None:
        self.current_balance = float(balance)

    def can_trade(self) -> tuple[bool, str]:
        loss_pct = (
            (self._start_balance - self.current_balance)
            / max(self._start_balance, 1e-9)
            * 100
        )
        if loss_pct >= MAX_DAILY_LOSS_PCT:
            return False, f"Daily loss limit reached ({loss_pct:.2f}%)"
        if self._open_positions >= MAX_OPEN_POSITIONS:
            return False, f"Max open positions reached ({self._open_positions})"
        return True, "OK"

    def calculate_lot_size(self, balance: float, sl_pips: float = 100) -> float:
        risk_amt = balance * (RISK_PER_TRADE_PCT / 100)
        loss_per_lot = max(sl_pips, 1) * PIP_VALUE_PER_LOT
        raw = risk_amt / max(loss_per_lot, 1e-9)
        return round(min(MAX_POSITION_SIZE_LOTS, max(0.01, raw)), 2)

    def register_trade(self, profit: float) -> None:
        self._daily_pnl += profit
        self.current_balance += profit
        if profit != 0.0:
            self._open_positions = max(0, self._open_positions - 1)

    def get_status(self) -> dict[str, Any]:
        return {
            "balance": round(self.current_balance, 2),
            "open_positions": self._open_positions,
            "daily_pnl": round(self._daily_pnl, 2),
            "start_balance": round(self._start_balance, 2),
        }


risk = _RuntimeRiskManager()


# ── MT5 helpers ───────────────────────────────────────────────────────────────

def _sync_risk_from_mt5() -> None:
    """Fetch live MT5 balance and push it to the risk manager."""
    try:
        import MetaTrader5 as mt5  # type: ignore
    except Exception:
        return
    if not mt5.initialize():
        return
    try:
        account = mt5.account_info()
        if account is not None:
            risk.update_balance(account.balance)
    finally:
        mt5.shutdown()


# ── Config loading ────────────────────────────────────────────────────────────

def _load_config(path: str = "config.json") -> dict[str, Any]:
    """Load JSON config with nested autotrade merge and backward-compat fixes."""
    cfg_path = Path(path)
    config = DEFAULT_CONFIG.copy()
    if not cfg_path.exists():
        return config
    text = cfg_path.read_text(encoding="utf-8").strip()
    if not text:
        return config
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in %s: %s — using defaults", path, exc)
        return config

    config.update(loaded)
    if isinstance(loaded.get("autotrade"), dict):
        autotrade = (DEFAULT_CONFIG.get("autotrade") or {}).copy()
        autotrade.update(loaded["autotrade"])
        config["autotrade"] = autotrade

    # Backward compat: "symbol" (str) → "symbols" (list)
    if "symbol" in loaded and "symbols" not in loaded:
        config["symbols"] = [loaded["symbol"]]

    symbols = config.get("symbols", DEFAULT_SYMBOLS)
    if isinstance(symbols, str):
        config["symbols"] = [symbols]
    elif not symbols:
        config["symbols"] = DEFAULT_SYMBOLS

    return config


# ── Grid level computation (Feature 4) ───────────────────────────────────────

def compute_grid_levels(
    latest: Any,
    n_levels: int = 3,
) -> list[dict[str, Any]]:
    """Compute key price grid levels for the visual grid chart.

    Returns a list of level dicts sorted highest → lowest price.
    Each dict: {price, label, type} where type ∈ {current, vwap, resistance, support}.

    Grid construction:
    - Current price marker
    - VWAP fair-value line (if available)
    - Bollinger Band upper/lower as first resistance/support
    - ATR-spaced grid lines above and below current price
    """
    def _f(key: str, default: float = 0.0) -> float:
        try:
            return float(latest.get(key, default))
        except (TypeError, ValueError):
            return default

    close = _f("close")
    atr = _f("atr") or close * 0.001  # fallback: 0.1% of price

    levels: list[dict[str, Any]] = [
        {"price": close, "label": "PRICE", "type": "current"},
    ]

    vwap = _f("vwap")
    if vwap > 0:
        levels.append({"price": vwap, "label": "VWAP", "type": "vwap"})

    bb_upper = _f("bb_upper")
    bb_lower = _f("bb_lower")
    if bb_upper > 0:
        levels.append({"price": bb_upper, "label": "BB↑", "type": "resistance"})
    if bb_lower > 0:
        levels.append({"price": bb_lower, "label": "BB↓", "type": "support"})

    for i in range(1, n_levels + 1):
        levels.append({"price": close + i * atr, "label": f"R{i}", "type": "resistance"})
        levels.append({"price": close - i * atr, "label": f"S{i}", "type": "support"})

    levels.sort(key=lambda x: x["price"], reverse=True)
    return levels


# ── Per-symbol analysis ───────────────────────────────────────────────────────

def _analyse_symbol(
    symbol: str,
    raw: Any,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Run strategy indicators + LSTM + smarter signal generation for one symbol.

    Feature 3: uses strategy.indicators (adds ADX/OBV/VWAP/ATR) and
    strategy.signal_generator (regime-aware, adaptive confidence).
    Feature 4: appends grid_levels to the snapshot.
    """
    # Feature 3: full indicator set including ADX, OBV, VWAP, ATR
    data = add_indicators(raw)

    features: Any = data[LSTM_FEATURE_COLS]
    pipeline = LSTMPipeline(
        lookback=int(cfg.get("lookback", 30)),
        epochs=int(cfg.get("epochs", 2)),
    )
    pipeline.fit(features)
    lstm_delta = pipeline.predict_next_delta(features, close_col_index=0)

    latest = data.iloc[-1]
    # Feature 3: strategy signal generator with regime + uncertainty-aware LSTM weight
    signal = generate_signal(latest, lstm_delta=lstm_delta, lstm_uncertainty=0.0)

    # Feature 4: grid levels for the visualiser
    grid_levels = compute_grid_levels(latest)

    return {
        "symbol": symbol,
        "timeframe": cfg.get("timeframe", "M5"),
        "last_close": round(float(latest["close"]), 6),
        "lstm_delta": round(float(lstm_delta), 6),
        "signal": signal_to_dict(signal),
        "grid_levels": grid_levels,
        "rows": int(len(data)),
    }


def _build_multi_snapshots(
    cfg: dict[str, Any],
    raw_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Analyse all symbols in parallel (CPU-bound LSTM work)."""
    symbols = list(raw_data.keys())
    results: dict[str, dict[str, Any]] = {}

    with ThreadPoolExecutor(max_workers=min(len(symbols), MAX_WORKERS)) as pool:
        futures = {
            pool.submit(_analyse_symbol, sym, raw_data[sym], cfg): sym
            for sym in symbols
        }
        for future in as_completed(futures):
            sym = futures[future]
            try:
                results[sym] = future.result()
            except Exception as exc:
                logger.error("Analysis failed for %s: %s", sym, exc)
                results[sym] = {
                    "symbol": sym,
                    "error": str(exc),
                    "signal": {
                        "signal": "HOLD",
                        "confidence": 0.0,
                        "score": 0,
                        "reasons": ["Analysis error — see logs"],
                        "regime": "RANGING",
                    },
                    "grid_levels": [],
                }

    return [results[sym] for sym in symbols]


# ── AppRuntime ────────────────────────────────────────────────────────────────

class AppRuntime:
    """Manages MT5 data fetching and per-symbol trading state."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        autotrade_cfg = cfg.get("autotrade", {})
        self.symbols: list[str] = list(cfg.get("symbols", DEFAULT_SYMBOLS))
        self.traders: dict[str, MT5AutoTrader] = self._create_traders(autotrade_cfg)
        self.cooldown_seconds = int(autotrade_cfg.get("cooldown_seconds", 60))
        self.allow_same_signal = bool(autotrade_cfg.get("allow_same_signal", False))
        self.last_trade_ts: dict[str, float] = {sym: 0.0 for sym in self.symbols}
        self.last_trade_signal: dict[str, str] = {sym: "" for sym in self.symbols}

    def _create_traders(self, autotrade_cfg: dict[str, Any]) -> dict[str, MT5AutoTrader]:
        magic_base = int(autotrade_cfg.get("magic", 20260327))
        return {
            sym: MT5AutoTrader(
                symbol=sym,
                enabled=bool(autotrade_cfg.get("enabled", False)),
                dry_run=bool(autotrade_cfg.get("dry_run", True)),
                min_confidence=float(autotrade_cfg.get("min_confidence", 70.0)),
                volume=float(autotrade_cfg.get("volume", 0.01)),
                deviation=int(autotrade_cfg.get("deviation", 20)),
                sl_points=int(autotrade_cfg.get("sl_points", 200)),
                tp_points=int(autotrade_cfg.get("tp_points", 300)),
                magic=magic_base + idx,
            )
            for idx, sym in enumerate(self.symbols)
        }

    def next_snapshots(self) -> list[dict[str, Any]]:
        """Fetch all symbols then analyse in parallel."""
        _sync_risk_from_mt5()
        raw_data = batch_fetch(
            symbols=self.symbols,
            timeframe=str(self.cfg.get("timeframe", "M5")),
            bars=int(self.cfg.get("bars", 700)),
        )
        snapshots = _build_multi_snapshots(self.cfg, raw_data)
        for snap in snapshots:
            sym = snap.get("symbol", "")
            snap["autotrade"] = self._maybe_trade(sym, snap)
        return snapshots

    def next_snapshot(self) -> dict[str, Any]:
        """Single-symbol compat wrapper."""
        snaps = self.next_snapshots()
        return snaps[0] if snaps else {}

    def _maybe_trade(self, symbol: str, snapshot: dict[str, Any]) -> dict[str, Any]:
        trader = self.traders.get(symbol)
        if trader is None:
            return {"status": "no_trader"}

        sig_data = snapshot.get("signal", {})
        signal = str(sig_data.get("signal", "HOLD")).upper()
        confidence = float(sig_data.get("confidence", 0.0))

        can, reason = risk.can_trade()
        if not can:
            logger.warning("Risk block for %s: %s", symbol, reason)
            return {"status": "risk_blocked", "reason": reason}

        if signal not in {"BUY", "SELL"}:
            return {"status": "no_trade_signal", "signal": signal}

        now_ts = time.time()
        if self.cooldown_seconds > 0 and (now_ts - self.last_trade_ts.get(symbol, 0.0)) < self.cooldown_seconds:
            return {
                "status": "cooldown",
                "seconds_left": round(self.cooldown_seconds - (now_ts - self.last_trade_ts[symbol]), 1),
            }

        if not self.allow_same_signal and signal == self.last_trade_signal.get(symbol, ""):
            return {"status": "same_signal_blocked", "signal": signal}

        lot = risk.calculate_lot_size(risk.current_balance, sl_pips=100)
        trader.volume = lot
        result = trader.maybe_execute(signal=signal, confidence=confidence)
        if result.get("status") in {"placed", "dry_run"}:
            risk.register_trade(float(result.get("profit", 0.0)))
            self.last_trade_ts[symbol] = now_ts
            self.last_trade_signal[symbol] = signal
        return result


# ── CLI helpers ───────────────────────────────────────────────────────────────

def _clear_console() -> None:
    subprocess.run(
        CLEAR_COMMAND, shell=True, check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alpha AI trading terminal")
    parser.add_argument("--config", default="config.json",
                        help="Path to config JSON (e.g. profiles/paper_safe.json)")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI")
    parser.add_argument("--continuous", action="store_true",
                        help="Run continuous loop (console output)")
    parser.add_argument("--interval", type=float, default=None,
                        help="Seconds between analysis cycles (overrides config)")
    # Feature 2: WebSocket dashboard flag
    parser.add_argument("--dashboard", action="store_true",
                        help="Start WebSocket dashboard at http://localhost:8050")
    parser.add_argument("--dashboard-port", type=int, default=8050,
                        help="Dashboard HTTP port (default: 8050)")
    return parser.parse_args()


# ── Continuous loop (Feature 1 + Feature 5) ───────────────────────────────────

def _run_continuous_loop(
    runtime: AppRuntime,
    interval: float,
    push_fn: Any = None,
) -> None:
    """Robust continuous trading loop with pause/stop support.

    Feature 1: runs indefinitely; recovers from per-cycle errors.
    Feature 5: checks controller for pause/stop between cycles.

    Args:
        runtime:  AppRuntime instance.
        interval: Seconds between analysis cycles.
        push_fn:  Optional callable(snapshots) — called after each cycle to
                  update the dashboard (Feature 2).
    """
    controller.start()
    logger.info("Continuous loop started (%.1fs interval)", interval)

    while controller.should_continue():
        # Feature 5: honour pause
        if controller.wait_if_paused():
            break  # stop was requested while paused

        # Feature 1: error-resilient iteration
        try:
            snapshots = runtime.next_snapshots()
        except Exception as exc:
            logger.error("Snapshot cycle failed: %s — retrying in %.1fs", exc, interval)
            time.sleep(min(interval, 10.0))
            continue

        _clear_console()
        render_console(snapshots)
        status: dict[str, Any] = risk.get_status()
        print(status)
        print(f"Next update in {interval:.1f}s  |  [Ctrl+C to stop]")

        # Feature 2: push snapshot to WebSocket dashboard if running
        if push_fn is not None:
            try:
                push_fn(snapshots)
            except Exception:
                pass

        # Sleep in short increments so pause/stop is responsive
        deadline = time.monotonic() + interval
        while time.monotonic() < deadline and controller.should_continue():
            time.sleep(min(0.5, deadline - time.monotonic()))

    logger.info("Continuous loop stopped")
    print("\nStopped.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print(f"FTMO MODE: {FTMO_MODE}")
    print(f"Max daily loss: {START_BALANCE * (MAX_DAILY_LOSS_PCT / 100):.2f}")

    args = _parse_args()
    cfg = _load_config(args.config)
    runtime = AppRuntime(cfg)

    interval = float(args.interval) if args.interval is not None else float(cfg.get("interval", 5.0))
    if (args.gui or args.continuous) and interval <= 0:
        raise ValueError("--interval must be > 0 for GUI or continuous mode")

    # Feature 2: start WebSocket dashboard if requested
    push_fn = None
    if args.dashboard or args.gui:
        try:
            from dashboard import start_dashboard, push_state
            start_dashboard(controller=controller, port=args.dashboard_port)
            push_fn = push_state
        except Exception as exc:
            logger.warning("Dashboard could not start: %s", exc)

    try:
        if args.gui:
            run_live_gui(runtime.next_snapshots, interval_seconds=interval)
        elif args.continuous:
            _run_continuous_loop(runtime, interval, push_fn=push_fn)
        else:
            snapshots = runtime.next_snapshots()
            render_console(snapshots)
            print(risk.get_status())
    except KeyboardInterrupt:
        logger.info("Stopped by user (Ctrl+C)")
        controller.stop()


if __name__ == "__main__":
    main()
