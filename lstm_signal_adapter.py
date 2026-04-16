"""
lstm_signal_adapter.py
─────────────────────────────────────────────────────────────────────
Adapter layer: loads alpha_data_scraper_ai LSTMPipeline + signal_generator
and exposes a clean interface for mt5_bridge.py to consume.

Key design decisions:
  - FIX #4: Train/predict split — fit() excludes the final LOOKBACK bars
    so inference runs on data the model did not fit on.
  - FIX #2: Fit cooldown — prevents refit-storm on repeated failure;
    failed retrain reverts to last-good pipeline.
  - Compatibility: keeps the legacy ensemble_size constructor argument, but
    uses the local LSTMPipeline API: fit() + predict_next_delta().
  - One instance per symbol — each has its own fitted model.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# ─── Resolve alpha_data_scraper_ai path ──────────────────────────────
ALPHA_PATH = Path(os.getenv("ALPHA_REPO_PATH", Path(__file__).resolve().parent))
if str(ALPHA_PATH) not in sys.path:
    sys.path.insert(0, str(ALPHA_PATH))

try:
    from indicators import (
        compute_atr,
        compute_atr_pct,
        compute_adx,
        compute_obv_zscore,
        compute_vwap_deviation,
    )
    from lstm_model import LSTMPipeline
    from signal_generator import (
        generate_signal,
        detect_market_regime,
        SignalResult,
    )

    ALPHA_AVAILABLE = True
except ImportError as exc:
    logging.warning(f"[LSTMAdapter] alpha_data_scraper_ai not found: {exc}")
    ALPHA_AVAILABLE = False

log = logging.getLogger("LSTMAdapter")

# ─── 13-column feature schema (matches main.py) ─────────────────────
LSTM_FEATURE_COLS: tuple[str, ...] = (
    "close",
    "rsi",
    "stoch_k",
    "stoch_d",
    "macd_hist",
    "bb_pos",
    "volume",
    "atr",
    "adx",
    "obv_zscore",
    "vwap_dev",
    "plus_di",
    "minus_di",
)


@dataclass
class LSTMSignal:
    """Result from LSTM inference pipeline."""

    direction: str  # BUY | SELL | HOLD
    confidence: float  # 0–100
    lstm_delta: float  # predicted price delta
    lstm_uncertainty: float  # conservative uncertainty until pipeline exposes it
    regime: str  # TRENDING | RANGING | VOLATILE
    score: int  # raw signal score
    reasons: list[str] = field(default_factory=list)
    available: bool = True


_FALLBACK = LSTMSignal(
    direction="HOLD",
    confidence=0.0,
    lstm_delta=0.0,
    lstm_uncertainty=1.0,
    regime="UNKNOWN",
    score=0,
    reasons=[],
    available=False,
)


class LSTMSignalAdapter:
    """
    Wraps alpha_data_scraper_ai LSTMPipeline + signal_generator.
    One instance per symbol — each symbol owns its own fitted model.
    """

    MIN_BARS_TO_FIT = 60
    LOOKBACK = 30
    RETRAIN_BARS = 100
    FIT_COOLDOWN_S = 300  # seconds between fit attempts after failure

    def __init__(self, symbol: str, ensemble_size: int = 2) -> None:
        self.symbol = symbol
        self.ensemble_size = ensemble_size
        self._pipeline: LSTMPipeline | None = None
        self._last_good_pipeline: LSTMPipeline | None = None
        self._bars_since_train = 0
        self._fitted = False
        self._last_fit_attempt = 0.0

    # ─── Feature engineering ─────────────────────────────────────────

    def _build_features(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """Compute all 13 LSTM feature columns from raw OHLCV + pre-computed indicators."""
        if not ALPHA_AVAILABLE:
            return None
        try:
            feat = df[["close", "volume"]].copy()

            # Pre-computed by mt5_bridge; fall back to neutral defaults
            for col, default in (
                ("rsi", 50.0),
                ("stoch_k", 50.0),
                ("stoch_d", 50.0),
                ("macd_hist", 0.0),
                ("bb_pos", 0.5),
            ):
                feat[col] = df.get(col, pd.Series(default, index=df.index))

            # alpha_data_scraper_ai indicators
            feat["atr"] = compute_atr(df["high"], df["low"], df["close"])
            feat["adx"], feat["plus_di"], feat["minus_di"] = compute_adx(
                df["high"], df["low"], df["close"]
            )
            feat["obv_zscore"] = compute_obv_zscore(df["close"], df["volume"])
            feat["vwap_dev"] = compute_vwap_deviation(
                df["high"], df["low"], df["close"], df["volume"]
            )

            return feat[list(LSTM_FEATURE_COLS)].dropna()

        except Exception as exc:
            log.error(f"[{self.symbol}] Feature build failed: {exc}")
            return None

    # ─── Training ────────────────────────────────────────────────────

    def _fit(self, features: pd.DataFrame) -> None:
        """
        FIX #4: Train on features[:-LOOKBACK] so the prediction window
        is never in the training set.
        """
        train_end = len(features) - self.LOOKBACK
        if train_end < self.MIN_BARS_TO_FIT:
            log.warning(
                f"[{self.symbol}] Not enough bars for train/predict split "
                f"({train_end} < {self.MIN_BARS_TO_FIT})"
            )
            return

        train_features = features.iloc[:train_end]

        try:
            pipeline = LSTMPipeline(
                lookback=self.LOOKBACK,
                epochs=5,
                batch_size=16,
            )
            pipeline.fit(train_features, target_col="close")

            self._pipeline = pipeline
            self._last_good_pipeline = pipeline
            self._fitted = True
            self._bars_since_train = 0
            log.info(
                f"[{self.symbol}] LSTM fitted | train_bars={len(train_features)} "
                f"| held_out={self.LOOKBACK}"
            )

        except Exception as exc:
            log.error(f"[{self.symbol}] LSTM fit failed: {exc}")
            # Revert to last working model if available
            if self._last_good_pipeline is not None:
                self._pipeline = self._last_good_pipeline
                self._fitted = True
                log.warning(f"[{self.symbol}] Reverted to previous pipeline")
            else:
                self._fitted = False

    # ─── Inference ───────────────────────────────────────────────────

    def predict(self, df: pd.DataFrame) -> LSTMSignal:
        """Main entry point. Returns LSTMSignal; falls back gracefully."""
        if not ALPHA_AVAILABLE:
            return self._fallback("alpha_data_scraper_ai not installed")

        features = self._build_features(df)
        if features is None or len(features) < self.MIN_BARS_TO_FIT + self.LOOKBACK:
            bar_count = 0 if features is None else len(features)
            return self._fallback(f"Insufficient bars ({bar_count})")

        # ── Gated fit with cooldown ───────────────────────────────────
        self._bars_since_train += 1
        needs_fit = (not self._fitted) or (self._bars_since_train >= self.RETRAIN_BARS)
        if needs_fit:
            now = time.monotonic()
            if (now - self._last_fit_attempt) >= self.FIT_COOLDOWN_S:
                self._last_fit_attempt = now
                self._fit(features)
            else:
                remaining = self.FIT_COOLDOWN_S - (now - self._last_fit_attempt)
                log.debug(f"[{self.symbol}] Fit cooldown: {remaining:.0f}s")

        if not self._fitted or self._pipeline is None:
            return self._fallback("LSTM not fitted")

        try:
            lstm_delta = float(
                self._pipeline.predict_next_delta(features, close_col_index=0)
            )
            uncertainty = 1.0

            latest_row = features.iloc[-1]
            regime = detect_market_regime(
                adx=float(latest_row.get("adx", 20)),
                atr_pct=float(
                    compute_atr_pct(df["high"], df["low"], df["close"]).iloc[-1]
                ),
                plus_di=float(latest_row.get("plus_di", 0)),
                minus_di=float(latest_row.get("minus_di", 0)),
            )

            result: SignalResult = generate_signal(
                latest=latest_row,
                lstm_delta=lstm_delta,
                lstm_uncertainty=uncertainty,
            )

            log.info(
                f"[{self.symbol}] LSTM → {result.signal} "
                f"conf={result.confidence:.1f}% delta={lstm_delta:+.5f} "
                f"unc={uncertainty:.3f} regime={regime.value}"
            )

            return LSTMSignal(
                direction=result.signal,
                confidence=result.confidence,
                lstm_delta=lstm_delta,
                lstm_uncertainty=uncertainty,
                regime=self._combiner_regime(regime),
                score=result.score,
                reasons=result.reasons,
            )

        except Exception as exc:
            log.error(f"[{self.symbol}] Predict error: {exc}")
            return self._fallback(str(exc))

    @staticmethod
    def _combiner_regime(regime: object) -> str:
        value = getattr(regime, "value", str(regime))
        if value in {"TRENDING_UP", "TRENDING_DOWN"}:
            return "TRENDING"
        if value == "RANGING":
            return "RANGING"
        return "UNKNOWN"

    @staticmethod
    def _fallback(reason: str) -> LSTMSignal:
        return LSTMSignal(
            direction="HOLD",
            confidence=0.0,
            lstm_delta=0.0,
            lstm_uncertainty=1.0,
            regime="UNKNOWN",
            score=0,
            reasons=[f"LSTM unavailable: {reason}"],
            available=False,
        )
