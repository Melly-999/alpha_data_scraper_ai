from __future__ import annotations

from dataclasses import dataclass
import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class LSTMSignal:
    direction: str
    confidence: float
    available: bool = False
    regime: str = 'UNKNOWN'
    lstm_uncertainty: float = 1.0
    reasons: list[str] | None = None

class LSTMSignalAdapter:
    def __init__(self, symbol: str, ensemble_size: int = 1):
        self.symbol = symbol
        self.ensemble_size = ensemble_size
        self.alpha_repo_path = os.getenv('ALPHA_REPO_PATH', '').strip()
        self.alpha_lstm_class = os.getenv('ALPHA_LSTM_CLASS', '').strip()
        self.alpha_lstm_function = os.getenv('ALPHA_LSTM_FUNCTION', '').strip()
        self.alpha_lstm_checkpoint = os.getenv('ALPHA_LSTM_CHECKPOINT', '').strip()
        self._loaded = False
        self._callable: Any = None
        self._load_reason = 'LSTM adapter not configured'
        self._load()

    def _load(self):
        if self.alpha_lstm_class and self.alpha_lstm_function:
            self._load_reason = (
                'Both ALPHA_LSTM_CLASS and ALPHA_LSTM_FUNCTION are set; set only one'
            )
            logger.warning(self._load_reason)
            return
        if not self.alpha_repo_path:
            self._load_reason = 'ALPHA_REPO_PATH is missing'
            logger.warning(self._load_reason)
            return

        repo_path = Path(self.alpha_repo_path)
        if not repo_path.exists():
            self._load_reason = f'ALPHA_REPO_PATH does not exist: {repo_path}'
            logger.warning(self._load_reason)
            return

        if str(repo_path) not in sys.path:
            sys.path.append(self.alpha_repo_path)

        try:
            if self.alpha_lstm_function:
                mod_name, fn_name = self._split_dotted_path(self.alpha_lstm_function)
                mod = importlib.import_module(mod_name)
                if not hasattr(mod, fn_name):
                    self._load_reason = (
                        f'ALPHA_LSTM_FUNCTION attribute not found: {self.alpha_lstm_function}'
                    )
                    logger.warning(self._load_reason)
                    return
                self._callable = getattr(mod, fn_name)
                self._loaded = True
                self._load_reason = f'Loaded ALPHA_LSTM_FUNCTION={self.alpha_lstm_function}'
                logger.info(self._load_reason)
                return
            if self.alpha_lstm_class:
                mod_name, cls_name = self._split_dotted_path(self.alpha_lstm_class)
                mod = importlib.import_module(mod_name)
                if not hasattr(mod, cls_name):
                    self._load_reason = (
                        f'ALPHA_LSTM_CLASS attribute not found: {self.alpha_lstm_class}'
                    )
                    logger.warning(self._load_reason)
                    return
                cls = getattr(mod, cls_name)
                self._callable = cls()
                self._load_checkpoint_if_supported()
                self._loaded = True
                self._load_reason = f'Loaded ALPHA_LSTM_CLASS={self.alpha_lstm_class}'
                logger.info(self._load_reason)
                return

            self._load_reason = 'Neither ALPHA_LSTM_CLASS nor ALPHA_LSTM_FUNCTION is set'
            logger.warning(self._load_reason)
        except ImportError as exc:
            self._loaded = False
            self._callable = None
            self._load_reason = f'LSTM import failure: {exc}'
            logger.exception(self._load_reason)
        except Exception as exc:
            self._loaded = False
            self._callable = None
            self._load_reason = f'LSTM runtime model load error: {type(exc).__name__}: {exc}'
            logger.exception(self._load_reason)

    @staticmethod
    def _split_dotted_path(path: str) -> tuple[str, str]:
        if '.' not in path:
            raise ValueError(f'Invalid dotted import path: {path}')
        return path.rsplit('.', 1)

    def _load_checkpoint_if_supported(self) -> None:
        if not hasattr(self._callable, 'load_checkpoint'):
            return
        if not self.alpha_lstm_checkpoint:
            logger.warning(
                'ALPHA_LSTM_CHECKPOINT is missing for model with load_checkpoint support'
            )
            return

        checkpoint = Path(self.alpha_lstm_checkpoint)
        if not checkpoint.exists():
            logger.warning('LSTM checkpoint missing: %s', checkpoint)
            return

        try:
            self._callable.load_checkpoint(str(checkpoint))
        except Exception as exc:
            self._load_reason = f'LSTM checkpoint load error: {type(exc).__name__}: {exc}'
            logger.exception(self._load_reason)
            raise

    def predict(self, df):
        if not self._loaded or self._callable is None:
            return self._fallback(self._load_reason)
        try:
            raw = self._predict_raw(df)
            return self._to_signal(raw)
        except Exception as exc:
            reason = f'LSTM runtime prediction error: {type(exc).__name__}: {exc}'
            logger.exception(reason)
            return self._fallback(reason)

    def _predict_raw(self, df):
        if callable(self._callable) and self.alpha_lstm_function:
            return self._callable(df)

        if hasattr(self._callable, 'predict') and not hasattr(
            self._callable, 'predict_next_delta'
        ):
            return self._callable.predict(df)

        if hasattr(self._callable, 'fit') and hasattr(self._callable, 'predict_next_delta'):
            if df is None:
                raise ValueError(
                    'Input OHLCV/features dataframe is required for LSTMPipeline inference'
                )
            features = self._feature_frame(df)
            self._callable.fit(features, target_col='close')
            delta = float(self._callable.predict_next_delta(features, close_col_index=0))
            uncertainty = 0.0
            if hasattr(self._callable, 'prediction_uncertainty'):
                uncertainty = float(
                    self._callable.prediction_uncertainty(features, close_col_index=0)
                )
            return {
                'direction': self._direction_from_delta(delta),
                'confidence': self._confidence_from_delta(delta, features),
                'regime': 'UNKNOWN',
                'uncertainty': uncertainty,
                'delta': delta,
                'reasons': [
                    f'{self.alpha_lstm_class or self.alpha_lstm_function} delta={delta:.8f}'
                ],
            }

        raise TypeError(
            'Loaded LSTM object must be callable, expose predict(df), or expose '
            'fit(df) plus predict_next_delta(df)'
        )

    @staticmethod
    def _feature_frame(df):
        required = ['close', 'open', 'high', 'low']
        missing = [column for column in required if column not in df.columns]
        if missing:
            raise ValueError(f'LSTM input missing required columns: {missing}')
        columns = [
            column
            for column in ['close', 'open', 'high', 'low', 'volume']
            if column in df.columns
        ]
        return df[columns].copy()

    @staticmethod
    def _direction_from_delta(delta: float) -> str:
        if delta > 0:
            return 'BUY'
        if delta < 0:
            return 'SELL'
        return 'HOLD'

    @staticmethod
    def _confidence_from_delta(delta: float, features) -> float:
        close = float(features['close'].iloc[-1])
        if close == 0:
            return 70.0
        move_bps = abs(delta / close) * 10000
        return round(max(33.0, min(85.0, 70.0 + move_bps)), 1)

    @staticmethod
    def _to_signal(raw) -> LSTMSignal:
        if isinstance(raw, dict):
            return LSTMSignal(
                direction=str(raw.get('direction', 'HOLD')),
                confidence=float(raw.get('confidence', 0.0)),
                available=True,
                regime=str(raw.get('regime', 'UNKNOWN')),
                lstm_uncertainty=float(raw.get('uncertainty', 0.2)),
                reasons=list(raw.get('reasons', ['alpha_data_scraper_ai output'])),
            )
        if isinstance(raw, (int, float)):
            delta = float(raw)
            return LSTMSignal(
                direction=LSTMSignalAdapter._direction_from_delta(delta),
                confidence=70.0,
                available=True,
                reasons=[f'Numeric LSTM delta={delta:.8f}'],
            )
        return LSTMSignalAdapter._fallback(
            f'Unsupported LSTM output type: {type(raw).__name__}'
        )

    @staticmethod
    def _fallback(reason: str) -> LSTMSignal:
        logger.warning('LSTM fallback to HOLD: %s', reason)
        return LSTMSignal(
            direction='HOLD',
            confidence=0.0,
            available=False,
            reasons=[reason],
        )
