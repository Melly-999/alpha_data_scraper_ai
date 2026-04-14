from dataclasses import dataclass
import os
import sys

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
        self._loaded = False
        self._callable = None
        self._load()

    def _load(self):
        if not self.alpha_repo_path:
            return
        if self.alpha_repo_path not in sys.path:
            sys.path.append(self.alpha_repo_path)
        try:
            if self.alpha_lstm_function:
                mod_name, fn_name = self.alpha_lstm_function.rsplit('.', 1)
                mod = __import__(mod_name, fromlist=[fn_name])
                self._callable = getattr(mod, fn_name)
                self._loaded = True
                return
            if self.alpha_lstm_class:
                mod_name, cls_name = self.alpha_lstm_class.rsplit('.', 1)
                mod = __import__(mod_name, fromlist=[cls_name])
                cls = getattr(mod, cls_name)
                self._callable = cls()
                self._loaded = True
        except Exception:
            self._loaded = False
            self._callable = None

    def predict(self, df):
        if not self._loaded or self._callable is None:
            return LSTMSignal(direction='HOLD', confidence=0.0, available=False, reasons=['LSTM adapter not configured'])
        try:
            raw = self._callable(df) if callable(self._callable) else self._callable.predict(df)
            if isinstance(raw, dict):
                return LSTMSignal(
                    direction=str(raw.get('direction', 'HOLD')),
                    confidence=float(raw.get('confidence', 0.0)),
                    available=True,
                    regime=str(raw.get('regime', 'UNKNOWN')),
                    lstm_uncertainty=float(raw.get('uncertainty', 0.2)),
                    reasons=list(raw.get('reasons', ['alpha_data_scraper_ai output']))
                )
            return LSTMSignal(direction='HOLD', confidence=0.0, available=False, reasons=['Unsupported LSTM output'])
        except Exception as exc:
            return LSTMSignal(direction='HOLD', confidence=0.0, available=False, reasons=[f'LSTM error: {exc}'])
