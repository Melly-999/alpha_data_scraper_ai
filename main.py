from __future__ import annotations

import argparse
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, List

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from core.config import *  # noqa: F403,E402
from risk.risk_manager import RiskConfig, RiskManager  # noqa: E402

# ---------------------------------------------------------------------------
# Dataclass-based configuration
#
# Converting the loosely-typed config dictionary into concrete dataclasses
# makes it easier to reason about available settings, provides better type
# checking, and improves discoverability when navigating the codebase. By
# defining defaults here, we reduce repetition in `_load_config` and make
# merging user-provided values more obvious. These classes are lightweight
# containers and impose zero runtime overhead.


@dataclass
class AutotradeConfig:
    """Settings controlling autotrade behaviour.

    Attributes mirror the keys in DEFAULT_CONFIG["autotrade"]. See
    DEFAULT_CONFIG for initial values.
    """

    enabled: bool = False
    dry_run: bool = True
    min_confidence: float = 70.0
    volume: float = 0.01
    deviation: int = 20
    sl_points: int = 200
    tp_points: int = 300
    magic: int = 20260327
    cooldown_seconds: int = 60
    allow_same_signal: bool = False


@dataclass
class AppConfig:
    """Top-level application configuration.

    Parameters correspond to those in DEFAULT_CONFIG. `autotrade` is a
    nested dataclass for clarity.
    """

    symbols: List[str] = field(default_factory=lambda: DEFAULT_SYMBOLS.copy())
    timeframe: str = "M5"
    bars: int = 700
    lookback: int = 30
    epochs: int = 2
    interval: float = 5.0
    indicator_buffer_size: int = 260
    http_timeout: float = 10.0
    enable_ensemble: bool = False
    risk: RiskConfig = field(default_factory=RiskConfig)
    autotrade: AutotradeConfig = field(default_factory=AutotradeConfig)


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


from gui import render_console, run_live_gui  # noqa: E402
from indicators import RollingIndicatorBuffer, add_indicators  # noqa: E402
from lstm_model import LSTMPipeline  # noqa: E402
from mt5_fetcher import batch_fetch  # noqa: E402
from mt5_trader import MT5AutoTrader  # noqa: E402
from signal_generator import generate_signal, signal_to_dict  # noqa: E402

# Optional ensemble combiner — graceful fallback to simple signal generator
try:
    from ensemble_combiner import EnsembleCombiner, TechnicalSignal  # noqa: E402
    from lstm_signal_adapter import LSTMSignalAdapter  # noqa: E402

    ENSEMBLE_AVAILABLE = True
except Exception:
    ENSEMBLE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "EURJPY",
    "XAUUSD",
    "WTI",
    "NVDA",
    "GOOGL",
    "USTECH100",
]
DEFAULT_CONFIG = {
    "symbols": DEFAULT_SYMBOLS,
    "timeframe": "M5",
    "bars": 700,
    "lookback": 30,
    "epochs": 2,
    "interval": 5.0,
    "indicator_buffer_size": 260,
    "http_timeout": 10.0,
    "enable_ensemble": False,
    "risk": {
        "max_risk_per_trade_pct": 1.0,
        "min_confidence": 50.0,
        "min_rr": 1.2,
        "max_open_positions": 5,
        "max_daily_loss_pct": 2.0,
        "max_position_size_lots": 1.0,
        "stop_loss_pips": 20.0,
        "pip_value_per_lot": 10.0,
    },
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


def _load_config(path: str = "config.json") -> AppConfig:
    """Load configuration from a JSON file into an `AppConfig` instance.

    This helper performs a deep merge of user-defined settings onto the
    `DEFAULT_CONFIG` and then populates the strongly-typed dataclasses
    `AutotradeConfig` and `AppConfig`. By returning concrete dataclasses
    instead of bare dictionaries we gain static type checking and better
    autocomplete support. Missing or invalid fields fall back to defaults.

    Args:
        path: Path to the JSON configuration file. If the file is absent
            or contains invalid JSON, defaults are used instead.

    Returns:
        An `AppConfig` populated with values from the provided file and
        sensible defaults.
    """
    cfg_path = Path(path)

    # Start with defaults as a deep copy (shallow is fine for primitives)
    config: dict[str, Any] = DEFAULT_CONFIG.copy()

    # If the file doesn't exist, return defaults immediately
    if not cfg_path.exists():
        return AppConfig()  # dataclasses already contain defaults

    text = cfg_path.read_text(encoding="utf-8").strip()
    if not text:
        return AppConfig()

    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in {path}: {e}. Using defaults.")
        return AppConfig()

    # Merge top-level fields onto defaults
    config.update({k: v for k, v in loaded.items() if k != "autotrade"})

    # Merge nested autotrade config
    if isinstance(loaded.get("autotrade"), dict):
        autotrade = DEFAULT_CONFIG.get("autotrade", {}).copy()
        autotrade.update(loaded["autotrade"])
        config["autotrade"] = autotrade
    if isinstance(loaded.get("risk"), dict):
        risk_defaults = DEFAULT_CONFIG.get("risk", {}).copy()
        risk_defaults.update(loaded["risk"])
        config["risk"] = risk_defaults

    # Backward compatibility: allow "symbol" instead of "symbols"
    if "symbol" in loaded and "symbols" not in loaded:
        config["symbols"] = [loaded["symbol"]]

    # Normalize symbols to list
    symbols_cfg = config.get("symbols", DEFAULT_SYMBOLS)
    if isinstance(symbols_cfg, str):
        symbols_cfg = [symbols_cfg]
    elif not symbols_cfg:
        symbols_cfg = DEFAULT_SYMBOLS

    # Build nested AutotradeConfig
    at_cfg_dict: dict[str, Any] = config.get("autotrade", {})
    at_cfg = AutotradeConfig(
        enabled=bool(at_cfg_dict.get("enabled", False)),
        dry_run=bool(at_cfg_dict.get("dry_run", True)),
        min_confidence=float(at_cfg_dict.get("min_confidence", 70.0)),
        volume=float(at_cfg_dict.get("volume", 0.01)),
        deviation=int(at_cfg_dict.get("deviation", 20)),
        sl_points=int(at_cfg_dict.get("sl_points", 200)),
        tp_points=int(at_cfg_dict.get("tp_points", 300)),
        magic=int(at_cfg_dict.get("magic", 20260327)),
        cooldown_seconds=int(at_cfg_dict.get("cooldown_seconds", 60)),
        allow_same_signal=bool(at_cfg_dict.get("allow_same_signal", False)),
    )

    risk_cfg_dict: dict[str, Any] = config.get("risk", {})
    risk_cfg = RiskConfig(
        max_risk_per_trade_pct=float(risk_cfg_dict.get("max_risk_per_trade_pct", 1.0)),
        min_confidence=float(risk_cfg_dict.get("min_confidence", 50.0)),
        min_rr=float(risk_cfg_dict.get("min_rr", 1.2)),
        max_open_positions=int(risk_cfg_dict.get("max_open_positions", 5)),
        max_daily_loss_pct=float(risk_cfg_dict.get("max_daily_loss_pct", 2.0)),
        max_position_size_lots=float(risk_cfg_dict.get("max_position_size_lots", 1.0)),
        stop_loss_pips=float(risk_cfg_dict.get("stop_loss_pips", 20.0)),
        pip_value_per_lot=float(risk_cfg_dict.get("pip_value_per_lot", 10.0)),
    )

    # Instantiate and return the top-level AppConfig
    return AppConfig(
        symbols=list(symbols_cfg),
        timeframe=str(config.get("timeframe", "M5")),
        bars=int(config.get("bars", 700)),
        lookback=int(config.get("lookback", 30)),
        epochs=int(config.get("epochs", 2)),
        interval=float(config.get("interval", 5.0)),
        indicator_buffer_size=int(config.get("indicator_buffer_size", 260)),
        http_timeout=float(config.get("http_timeout", 10.0)),
        enable_ensemble=bool(config.get("enable_ensemble", False)),
        risk=risk_cfg,
        autotrade=at_cfg,
    )


class AppRuntime:
    """Fetches MT5 snapshots and manages per-symbol trading state.

    Optimizations:
    - Caches traders dict keyed by symbol (avoid repeated lookups)
    - Thread-safe trade state tracking with last_trade_ts/signal dicts
    - Validates cooldown/duplicate signal checks before trader execution
    """

    def __init__(self, cfg: AppConfig) -> None:
        """Initialize runtime with a typed configuration.

        Args:
            cfg: The application configuration produced by `_load_config`. A
                copy is stored on the instance for later access. Symbols and
                autotrade settings are read directly from this object.
        """
        self.cfg: AppConfig = cfg
        risk.config = cfg.risk
        self.symbols: list[str] = list(cfg.symbols)

        # Create one LSTM pipeline per symbol. Reusing pipelines avoids
        # constructing new Keras models on each snapshot but still retrains
        # on fresh data as needed.
        self._lstm_pipelines: dict[str, LSTMPipeline] = {
            sym: LSTMPipeline(lookback=cfg.lookback, epochs=cfg.epochs)
            for sym in self.symbols
        }

        # Rolling indicator buffers for incremental updates. When running in
        # continuous mode, only the newest candles are pushed through the
        # indicator pipeline instead of recomputing on the full history.
        self._indicator_buffers: dict[str, RollingIndicatorBuffer] = {
            sym: RollingIndicatorBuffer(maxlen=cfg.indicator_buffer_size)
            for sym in self.symbols
        }

        # Ensemble combiner (optional) — fuses technical + LSTM signals
        self._ensemble_available = ENSEMBLE_AVAILABLE and cfg.enable_ensemble
        self._combiner = EnsembleCombiner() if self._ensemble_available else None
        self._lstm_adapters: dict[str, Any] = {}
        if self._ensemble_available:
            self._lstm_adapters = {
                sym: LSTMSignalAdapter(sym, ensemble_size=2) for sym in self.symbols
            }

        # Create traders once; reuse for all snapshots
        self.traders: dict[str, MT5AutoTrader] = self._create_traders(cfg.autotrade)

        # Cooldown/duplicate-signal settings
        self.cooldown_seconds = cfg.autotrade.cooldown_seconds
        self.allow_same_signal = cfg.autotrade.allow_same_signal

        # Per-symbol trade state (thread-safe dict ops in Python)
        self.last_trade_ts: dict[str, float] = {sym: 0.0 for sym in self.symbols}
        self.last_trade_signal: dict[str, str] = {sym: "" for sym in self.symbols}

    def _create_traders(
        self, autotrade_cfg: AutotradeConfig
    ) -> dict[str, MT5AutoTrader]:
        """Create MT5AutoTrader instances for all symbols.

        Using the strongly-typed `AutotradeConfig` avoids repetitive lookups
        and clearly communicates the expected fields. The magic number is
        incremented per symbol to ensure unique order identifiers.
        """
        traders: dict[str, MT5AutoTrader] = {}
        magic_base: int = autotrade_cfg.magic
        for idx, sym in enumerate(self.symbols):
            traders[sym] = MT5AutoTrader(
                symbol=sym,
                enabled=autotrade_cfg.enabled,
                dry_run=autotrade_cfg.dry_run,
                min_confidence=autotrade_cfg.min_confidence,
                volume=autotrade_cfg.volume,
                deviation=autotrade_cfg.deviation,
                sl_points=autotrade_cfg.sl_points,
                tp_points=autotrade_cfg.tp_points,
                magic=magic_base + idx,
                risk_manager=risk,
            )
        return traders

    def next_snapshots(self) -> list[dict[str, Any]]:
        """Fetch all symbols (one MT5 session) then analyse in parallel."""
        _sync_risk_from_mt5()
        raw_data = batch_fetch(
            symbols=self.symbols,
            timeframe=str(self.cfg.timeframe),
            bars=int(self.cfg.bars),
        )
        snapshots = _build_multi_snapshots(
            self.cfg,
            raw_data,
            self._lstm_pipelines,
            self._indicator_buffers,
            self._combiner,
            self._lstm_adapters if self._ensemble_available else None,
        )
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
        if signal not in {"BUY", "SELL"}:
            return {"status": "no_trade_signal", "signal": signal}

        now_ts = time.time()
        last_ts = self.last_trade_ts.get(symbol, 0.0)
        if self.cooldown_seconds > 0 and (now_ts - last_ts) < self.cooldown_seconds:
            return {
                "status": "cooldown",
                "seconds_left": round(self.cooldown_seconds - (now_ts - last_ts), 1),
            }

        if not self.allow_same_signal and signal == self.last_trade_signal.get(
            symbol, ""
        ):
            return {"status": "same_signal_blocked", "signal": signal}

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
    cfg: AppConfig,
    pipeline: LSTMPipeline | None = None,
    indicator_buffer: RollingIndicatorBuffer | None = None,
    ensemble_combiner: Any | None = None,
    lstm_adapter: Any | None = None,
) -> dict[str, Any]:
    """Run indicators + LSTM + signal generation for one symbol (CPU-bound).

    Optimizations:
    - Use module-level LSTM_FEATURE_COLS constant (avoid recreation)
    - Extract features once instead of per-column selection
    - When an indicator_buffer is supplied, new candles are pushed
      incrementally instead of recomputing the full history each cycle.
    - When ensemble_combiner + lstm_adapter are supplied, uses the
      EnsembleCombiner for weighted signal fusion (technical + LSTM).
    """
    if indicator_buffer is not None:
        data = indicator_buffer.extend(raw)
        if data.empty:
            source = indicator_buffer.frame if not indicator_buffer.frame.empty else raw
            data = add_indicators(source)
    else:
        data = add_indicators(raw)

    min_feature_rows = int(getattr(cfg, "lookback", 30)) + 1
    if indicator_buffer is not None and len(data) < min_feature_rows:
        source = indicator_buffer.frame if not indicator_buffer.frame.empty else raw
        full_window = add_indicators(source)
        if len(full_window) >= min_feature_rows:
            data = full_window

    # Extract feature columns once (constant defined at module level)
    features: Any = data[LSTM_FEATURE_COLS]

    if pipeline is None:
        pipeline = LSTMPipeline(
            lookback=int(getattr(cfg, "lookback", 30)),
            epochs=int(getattr(cfg, "epochs", 2)),
        )
    pipeline.fit(features)
    lstm_delta = pipeline.predict_next_delta(features, close_col_index=0)

    latest = data.iloc[-1]
    signal = generate_signal(latest, lstm_delta=lstm_delta)

    result: dict[str, Any] = {
        "symbol": symbol,
        "timeframe": getattr(cfg, "timeframe", "M5"),
        "last_close": round(float(latest["close"]), 6),
        "lstm_delta": round(float(lstm_delta), 6),
        "signal": signal_to_dict(signal),
        "rows": int(len(data)),
    }

    # Ensemble fusion (optional) — blends technical signal with LSTM adapter
    if ensemble_combiner is not None and lstm_adapter is not None:
        try:
            lstm_sig = lstm_adapter.predict(data)
            tech_sig = TechnicalSignal(
                direction=signal.signal,
                confidence=signal.confidence,
                sl=0.0,  # SL/TP computed by risk manager downstream
                tp=0.0,
            )
            combined = ensemble_combiner.combine(tech_sig, lstm_sig)
            result["ensemble"] = {
                "direction": combined.direction,
                "confidence": round(combined.confidence, 2),
                "lstm_weight": round(combined.lstm_weight, 2),
                "technical_weight": round(combined.technical_weight, 2),
                "regime": combined.regime,
                "blocked": combined.blocked,
                "block_reason": combined.block_reason,
                "reasons": combined.reasons[:5],
            }
            # Override signal with ensemble result when not blocked
            if not combined.blocked:
                result["signal"] = {
                    "signal": combined.direction,
                    "confidence": round(combined.confidence, 2),
                    "score": signal.score,
                    "reasons": combined.reasons[:5],
                }
        except Exception as exc:
            logger.warning(f"Ensemble fusion failed for {symbol}: {exc}")

    return result


def _build_multi_snapshots(
    cfg: AppConfig,
    raw_data: dict[str, Any],
    pipelines: dict[str, LSTMPipeline] | None = None,
    indicator_buffers: dict[str, RollingIndicatorBuffer] | None = None,
    ensemble_combiner: Any | None = None,
    lstm_adapters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Analyse all symbols in parallel using a thread pool (CPU-bound LSTM work).

    Optimizations:
    - Use MAX_WORKERS constant (tune once, reuse everywhere)
    - Specific exception handling instead of broad Exception catch
    - Direct iteration without redundant symbol presence check
    - Passes per-symbol RollingIndicatorBuffer for incremental updates
    - Passes EnsembleCombiner + LSTMSignalAdapter for ensemble fusion
    """
    symbols = list(raw_data.keys())
    results: dict[str, dict[str, Any]] = {}

    with ThreadPoolExecutor(max_workers=min(len(symbols), MAX_WORKERS)) as pool:
        futures = {
            pool.submit(
                _analyse_symbol,
                sym,
                raw_data[sym],
                cfg,
                pipelines.get(sym) if pipelines else None,
                indicator_buffers.get(sym) if indicator_buffers else None,
                ensemble_combiner,
                lstm_adapters.get(sym) if lstm_adapters else None,
            ): sym
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
    subprocess.run(  # noqa: S603
        [CLEAR_COMMAND],
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
    print("FTMO MODE:", FTMO_MODE)  # noqa: F405
    print("Max daily loss:", START_BALANCE * (MAX_DAILY_LOSS_PCT / 100))  # noqa: F405

    args = _parse_args()
    cfg = _load_config(args.config)
    runtime = AppRuntime(cfg)

    # Resolve interval: CLI override > config file > default
    # Determine update interval: CLI override > config > default
    interval = float(args.interval) if args.interval else cfg.interval
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
