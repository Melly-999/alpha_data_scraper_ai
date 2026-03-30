class SignalGenerator:
    """Combines indicators and LSTM to generate trading signals."""

    def __init__(self, config):
        self.config = config

    def generate_signal(self, price_slope, rsi, stoch_k, bb_pos, lstm_dir):
        """
        Returns (signal, hold_mode) where signal is 'BUY', 'SELL', or None.
        """
        slope_abs = abs(price_slope)
        if (
            slope_abs > self.config["slope_threshold"]
            and rsi < self.config["rsi_buy_max"]
            and stoch_k < self.config["stoch_buy_max"]
            and bb_pos < self.config["bb_buy_max"]
            and lstm_dir >= 0
        ):
            signal = "BUY"
        elif (
            slope_abs > self.config["slope_threshold"]
            and rsi > self.config["rsi_sell_min"]
            and stoch_k > self.config["stoch_sell_min"]
            and bb_pos > self.config["bb_sell_min"]
            and lstm_dir <= 0
        ):
            signal = "SELL"
        else:
            signal = None

        if signal:
            if slope_abs > self.config["trend_slope_threshold"]:
                hold_mode = "TREND (minuty)"
            else:
                hold_mode = "SCALPING (sekundy)"
        else:
            hold_mode = "NEUTRAL"

        return signal, hold_mode

    def compute_confidence(self, price_slope, rsi, stoch_k, lstm_dir, bb_pos):
        """Return confidence score (0-100)."""
        slope_abs = abs(price_slope)
        weights = self.config["weights"]

        slope_score = 40 + slope_abs * 20
        rsi_score = 72 if rsi < 35 else 28 if rsi > 65 else 50
        stoch_score = 76 if stoch_k < 20 else 24 if stoch_k > 80 else 50
        lstm_score = 72 if lstm_dir == 1 else 28 if lstm_dir == -1 else 50
        bb_score = 70 if abs(bb_pos) > 40 else 50

        confidence = (
            weights["slope"] * slope_score
            + weights["rsi"] * rsi_score
            + weights["stochastic"] * stoch_score
            + weights["lstm"] * lstm_score
            + weights["bb"] * bb_score
        )
        confidence = max(33, min(85, confidence))
        return int(confidence)
