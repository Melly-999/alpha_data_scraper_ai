from __future__ import annotations

import argparse
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from utils.config import *  # noqa: F403
from utils.risk_manager import RiskManager

risk = RiskManager()


def _sync_risk_from_mt5() -> None:
    """Łączy z MT5, aktualizuje saldo w RiskManager (batch_fetch zamyka sesję osobno)."""
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


from gui import render_console, run_live_gui
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import batch_fetch
from mt5_trader import MT5AutoTrader
from signal_generator import generate_signal, signal_to_dict

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY",
    "XAUUSD", "WTI", "NVDA", "GOOGL", "USTECH100",
]
DEFAULT_CONFIG = {
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
LSTM_FEATURE_COLS = [
    "close",
    "rsi",
    "stoch_k",
    "stoch_d",
    "macd_hist",
    "bb_pos",
    "volume",
]
MAX_WORKERS = 6
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"


def _load_config(path: str = "config.json") -> dict[str, Any]:
    """Load config from file with fallback to defaults; merge nested autotrade settings.
    
    Optimization: reads file only once; cached defaults.
    """
    cfg_path = Path(path)
    
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    
    # Return defaults if file missing or empty
    if not cfg_path.exists():
        return config
    
    text = cfg_path.read_text(encoding="utf-8").strip()
    if not text:
        return config
    
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in {path}: {e}. Using defaults.")
        return config
    
    # Merge top-level config
    config.update(loaded)
    
    # Merge autotrade sub-config if present
    if isinstance(loaded.get("autotrade"), dict):
        autotrade = DEFAULT_CONFIG.get("autotrade", {}).copy()
        autotrade.update(loaded["autotrade"])
        config["autotrade"] = autotrade
    
    # Backward compat: "symbol" (str) → "symbols" (list)
    if "symbol" in loaded and "symbols" not in loaded:
        config["symbols"] = [loaded["symbol"]]
    
    # Normalize symbols to list
    symbols = config.get("symbols", DEFAULT_SYMBOLS)
    if isinstance(symbols, str):
        config["symbols"] = [symbols]
    elif not symbols:
        config["symbols"] = DEFAULT_SYMBOLS
    
    return config


class AppRuntime:
    """Fetches MT5 snapshots and manages per-symbol trading state.
    
    Optimizations:
    - Caches traders dict keyed by symbol (avoid repeated lookups)
    - Thread-safe trade state tracking with last_trade_ts/signal dicts
    - Validates cooldown/duplicate signal checks before trader execution
    """

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        autotrade_cfg = cfg.get("autotrade", {})
        self.symbols: list[str] = list(cfg.get("symbols", DEFAULT_SYMBOLS))
        
        # Create traders once; reuse for all snapshots
        self.traders: dict[str, MT5AutoTrader] = self._create_traders(
            autotrade_cfg
        )
        
        self.cooldown_seconds = int(autotrade_cfg.get("cooldown_seconds", 60))
        self.allow_same_signal = bool(autotrade_cfg.get("allow_same_signal", False))
        
        # Per-symbol trade state (thread-safe dict ops in Python)
        self.last_trade_ts: dict[str, float] = {sym: 0.0 for sym in self.symbols}
        self.last_trade_signal: dict[str, str] = {sym: "" for sym in self.symbols}

    def _create_traders(self, autotrade_cfg: dict[str, Any]) -> dict[str, MT5AutoTrader]:
        """Create MT5AutoTrader instances for all symbols.
        
        Replaces lambda with explicit method for clarity and reusability.
        """
        traders = {}
        magic_base = int(autotrade_cfg.get("magic", 20260327))
        
        for idx, sym in enumerate(self.symbols):
            traders[sym] = MT5AutoTrader(
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
        return traders


    def next_snapshots(self) -> list[dict[str, Any]]:
        """Fetch all symbols (one MT5 session) then analyse in parallel."""
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
        can_trade, reason = risk.can_trade()

        if not can_trade:
            print("🚫 BLOCK:", reason)
            signal = None

        if signal not in {"BUY", "SELL"}:
            if not can_trade:
                return {"status": "risk_blocked", "reason": reason}
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

        lot = risk.calculate_lot_size(risk.current_balance, sl_pips=100)
        trader.volume = lot
        result = trader.maybe_execute(signal=signal, confidence=confidence)
        if result.get("status") in {"placed", "dry_run"}:
            profit = float(result.get("profit", 0.0))
            risk.register_trade(profit)
            self.last_trade_ts[symbol] = now_ts
            self.last_trade_signal[symbol] = signal
        return result


def _analyse_symbol(
    symbol: str,
    raw: Any,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Run indicators + LSTM + signal generation for one symbol (CPU-bound).
    
    Optimizations:
    - Use module-level LSTM_FEATURE_COLS constant (avoid recreation)
    - Extract features once instead of per-column selection
    """
    data = add_indicators(raw)
    
    # Extract feature columns once (constant defined at module level)
    features: Any = data[LSTM_FEATURE_COLS]
    
    pipeline = LSTMPipeline(
        lookback=int(cfg.get("lookback", 30)),
        epochs=int(cfg.get("epochs", 2))
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
    """Analyse all symbols in parallel using a thread pool (CPU-bound LSTM work).
    
    Optimizations:
    - Use MAX_WORKERS constant (tune once, reuse everywhere)
    - Specific exception handling instead of broad Exception catch
    - Direct iteration without redundant symbol presence check
    """
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
            except (ValueError, KeyError, RuntimeError) as exc:
                # Specific exceptions: ValueError (data errors), KeyError (missing cols),
                # RuntimeError (LSTM errors)
                logger.error(f"Analysis failed for {sym}: {exc}")
                results[sym] = {
                    "symbol": sym,
                    "error": str(exc),
                    "signal": {
                        "signal": "HOLD",
                        "confidence": 0.0,
                        "score": 0,
                        "reasons": ["Analysis error - see logs"],
                    },
                }
            except Exception as exc:
                # Catch any other unexpected errors
                logger.exception(f"Unexpected error analysing {sym}")
                results[sym] = {
                    "symbol": sym,
                    "error": f"Unexpected error: {type(exc).__name__}",
                    "signal": {
                        "signal": "HOLD",
                        "confidence": 0.0,
                        "score": 0,
                        "reasons": ["Unexpected error - see logs"],
                    },
                }
    
    # Preserve original symbol order: symbols list is source of truth
    return [results[sym] for sym in symbols]


def _clear_console() -> None:
    """Clear terminal screen (platform-aware).
    
    Optimization: Command string determined once at module load (CLEAR_COMMAND constant).
    """
    subprocess.run(
        CLEAR_COMMAND,
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
    """Main entry point: parse args, load config, run snapshots."""
    print("FTMO MODE:", FTMO_MODE)
    print("Max daily loss:", START_BALANCE * (MAX_DAILY_LOSS_PCT / 100))

    args = _parse_args()
    cfg = _load_config(args.config)
    runtime = AppRuntime(cfg)
    
    # Resolve interval: CLI override > config file > default
    interval = float(args.interval) if args.interval else cfg.get("interval", 5.0)
    interval = float(interval)
    
    # Validate interval for interactive modes
    if (args.gui or args.continuous) and interval <= 0:
        raise ValueError("--interval must be > 0 for GUI or continuous mode")
    
    try:
        if args.gui:
            run_live_gui(runtime.next_snapshots, interval_seconds=interval)
        elif args.continuous:
            _run_continuous_loop(runtime, interval)
        else:
            # One-shot mode
            snapshots = runtime.next_snapshots()
            render_console(snapshots)
            status: dict[str, Any] = risk.get_status()
            print(str(status))
    except KeyboardInterrupt:
        logger.info("Stopped by user (Ctrl+C)")


def _run_continuous_loop(runtime: AppRuntime, interval: float) -> None:
    """Run snapshot loop continuously until interrupted.
    
    Extracted to keep main() clean and reduce nesting.
    """
    logger.info(f"Starting continuous loop ({interval:.1f}s interval)")
    try:
        while True:
            snapshots = runtime.next_snapshots()
            _clear_console()
            render_console(snapshots)
            status: dict[str, Any] = risk.get_status()
            print(str(status))
            print(f"Next update in {interval:.1f}s (Ctrl+C to stop)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped continuous mode.")
        logger.info("Continuous loop stopped")


if __name__ == "__main__":
    main()


