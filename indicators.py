import pandas as pd


class IndicatorCalculator:
    """Computes technical indicators from OHLC data."""

    def __init__(self, config):
        self.config = config

    def calculate_all(self, df):
        """Return dict with all indicators."""
        close = df["close"]
        high = df["high"]
        low = df["low"]

        rsi_val = self._rsi(close, self.config["rsi_period"])
        _, _, hist = self._macd(
            close,
            self.config["macd_fast"],
            self.config["macd_slow"],
            self.config["macd_signal"],
        )
        bb_pos = self._bb_position(close, self.config["bb_period"], self.config["bb_std"])
        stoch_k, stoch_d = self._stochastic(
            close,
            high,
            low,
            self.config["stoch_period"],
            self.config["stoch_k_smooth"],
        )

        return {
            "rsi": rsi_val,
            "macd_hist": hist,
            "bb_position": bb_pos,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
        }

    def calculate_rsi_series(self, close):
        """Return full RSI series (used for LSTM input)."""
        period = self.config["rsi_period"]
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    @staticmethod
    def _rsi(close, period):
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0

    @staticmethod
    def _macd(close, fast, slow, signal):
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - signal_line
        return macd.iloc[-1], signal_line.iloc[-1], hist.iloc[-1]

    @staticmethod
    def _bb_position(close, period, std_mult):
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        bb_up = sma + std_mult * std
        bb_low = sma - std_mult * std
        denominator = bb_up - bb_low
        if denominator.iloc[-1] != 0:
            pos = (close.iloc[-1] - sma.iloc[-1]) / denominator.iloc[-1] * 100
        else:
            pos = 0.0
        return pos

    @staticmethod
    def _stochastic(close, high, low, period, k_smooth):
        low_min = low.rolling(period).min()
        high_max = high.rolling(period).max()
        k = 100 * (close - low_min) / (high_max - low_min + 1e-10)
        d = k.rolling(k_smooth).mean()
        return k.iloc[-1], d.iloc[-1]
