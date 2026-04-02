import os
import json
import time
import logging
import traceback
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from datetime import datetime
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter

# ====================== LOGGING SETUP ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("grok_alpha.log"), logging.StreamHandler()]
)
logger = logging.getLogger("GrokAlpha")

# ====================== CONFIGURATION ======================
def load_config(config_path="config.json"):
    with open(config_path, 'r') as f:
        return json.load(f)

class MT5DataFetcher:
    """Handles MT5 connection and data fetching with incremental updates."""
    def __init__(self, symbol):
        self.symbol = symbol
        self.initialized = False
        self.last_bar_time = None

    def initialize(self):
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        if not mt5.symbol_select(self.symbol, True):
            logger.warning(f"Symbol {self.symbol} not available")
            # Still allow, maybe later it becomes available
        self.initialized = True
        return True

    def shutdown(self):
        if self.initialized:
            mt5.shutdown()

    def get_tick(self):
        """Return current bid/ask as tuple (bid, ask)."""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return tick.bid, tick.ask

    def get_new_bars(self, max_bars=350):
        """
        Fetch new bars since last known bar.
        Returns (new_rates, full_df) or (None, None) if no new bars.
        """
        # First call: fetch all bars
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, max_bars)
        if rates is None or len(rates) == 0:
            logger.warning("No rates fetched")
            return None, None

        current_bar_time = datetime.fromtimestamp(rates[-1][0])
        if self.last_bar_time == current_bar_time:
            # No new bar
            return None, None

        # New bar(s) detected
        self.last_bar_time = current_bar_time
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return rates, df

    def get_account_info(self):
        return mt5.account_info()

class IndicatorCalculator:
    """Computes technical indicators from OHLC data."""
    def __init__(self, config):
        self.config = config

    def calculate_all(self, df):
        """Return dict with all indicators."""
        close = df['close']
        high = df['high']
        low = df['low']

        rsi_val = self._rsi(close, self.config['rsi_period'])
        macd_val, signal, hist = self._macd(close,
                                            self.config['macd_fast'],
                                            self.config['macd_slow'],
                                            self.config['macd_signal'])
        bb_pos = self._bb_position(close, self.config['bb_period'], self.config['bb_std'])
        stoch_k, stoch_d = self._stochastic(close, high, low,
                                            self.config['stoch_period'],
                                            self.config['stoch_k_smooth'])

        return {
            'rsi': rsi_val,
            'macd_hist': hist,
            'bb_position': bb_pos,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d
        }

    def calculate_rsi_series(self, close):
        """Return full RSI series (used for LSTM input)."""
        period = self.config['rsi_period']
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-10)  # avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    # Static methods for individual indicators
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

class LSTMModel:
    """LSTM model for price direction prediction."""
    def __init__(self, input_size=2, hidden_size=64, num_layers=3, dropout=0.15):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiFeatureLSTM(input_size, hidden_size, num_layers, dropout).to(self.device)
        self.model.eval()
        self.trained = False

    def load_checkpoint(self, path):
        if os.path.exists(path):
            try:
                checkpoint = torch.load(path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.trained = True
                logger.info(f"LSTM checkpoint loaded from {path}")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        else:
            logger.warning("No LSTM checkpoint found. Model will use random weights.")

    def predict(self, price_seq, rsi_seq):
        """
        price_seq: numpy array of last N prices
        rsi_seq: numpy array of last N RSI values
        Returns predicted price (float).
        """
        if not self.trained or len(price_seq) != len(rsi_seq):
            return None
        seq = np.column_stack((price_seq, rsi_seq))
        # Normalize
        seq = (seq - seq.mean(axis=0)) / (seq.std(axis=0) + 1e-8)
        seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            pred = self.model(seq_tensor).item()
        return pred

class MultiFeatureLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, 🙂)

class SignalGenerator:
    """Combines indicators and LSTM to generate trading signals."""
    def __init__(self, config):
        self.config = config

    def generate_signal(self, price_slope, rsi, stoch_k, bb_pos, lstm_dir):
        """
        Returns (signal, hold_mode) where signal is 'BUY', 'SELL', or None.
        """
        slope_abs = abs(price_slope)
        # Basic conditions
        if (slope_abs > self.config['slope_threshold'] and
            rsi < self.config['rsi_buy_max'] and
            stoch_k < self.config['stoch_buy_max'] and
            bb_pos < self.config['bb_buy_max'] and
            lstm_dir >= 0):
            signal = "BUY"
        elif (slope_abs > self.config['slope_threshold'] and
              rsi > self.config['rsi_sell_min'] and
              stoch_k > self.config['stoch_sell_min'] and
              bb_pos > self.config['bb_sell_min'] and
              lstm_dir <= 0):
            signal = "SELL"
        else:
            signal = None

        # Hold mode based on slope strength
        if signal:
            if slope_abs > self.config['trend_slope_threshold']:
                hold_mode = "TREND (minuty)"
            else:
                hold_mode = "SCALPING (sekundy)"
        else:
            hold_mode = "NEUTRAL"

        return signal, hold_mode

    def compute_confidence(self, price_slope, rsi, stoch_k, lstm_dir, bb_pos):
        """Return confidence score (0-100)."""
        slope_abs = abs(price_slope)
        weights = self.config['weights']

        # Component scores
        slope_score = 40 + slope_abs * 20
        rsi_score = 72 if rsi < 35 else 28 if rsi > 65 else 50
        stoch_score = 76 if stoch_k < 20 else 24 if stoch_k > 80 else 50
        lstm_score = 72 if lstm_dir == 1 else 28 if lstm_dir == -1 else 50
        bb_score = 70 if bb_pos < -40 else 70 if bb_pos > 40 else 50

        confidence = (weights['slope'] * slope_score +
                      weights['rsi'] * rsi_score +
                      weights['stochastic'] * stoch_score +
                      weights['lstm'] * lstm_score +
                      weights['bb'] * bb_score)
        confidence = max(33, min(85, confidence))
        return int(confidence)

class GrokAlphaGUI:
    def __init__(self, config):
        self.config = config
        self.symbol = config['symbol']
        self.version = config['version']
        self.update_ms = config['update_ms']
        self.conf_threshold = config['conf_threshold']
        self.seq_length = config['seq_length']

        # Initialize components
        self.mt5_fetcher = MT5DataFetcher(self.symbol)
        if not self.mt5_fetcher.initialize():
            messagebox.showerror("Błąd", "Nie można zainicjować MT5")
            raise SystemExit

        self.indicator_calc = IndicatorCalculator(config['indicators'])
        self.lstm = LSTMModel()
        self.lstm.load_checkpoint(config['lstm_checkpoint'])
        self.signal_gen = SignalGenerator(config)

        # Data storage
        self.prices = []        # list of latest tick prices (for slope and chart)
        self.times = []         # corresponding timestamps
        self.df = None          # full OHLC dataframe (updated on new bar)
        self.cached_indicators = {
            'rsi': 50.0,
            'macd_hist': 0.0,
            'bb_position': 0.0,
            'stoch_k': 50.0,
            'stoch_d': 50.0
        }
        self.lstm_dir = 0       # 1: bullish, -1: bearish, 0: neutral/unknown
        self.current_price = None
        self.last_bar_time = None
        self.logs = []
        self.session_start = self._get_initial_equity()

        # UI setup
        self.root = tk.Tk()
        self.root.title(f"Grok Alpha AI Terminal GUI {self.version}")
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("1460x860")
        self.create_ui()

        # Start periodic update
        self.update_data()

    def _get_initial_equity(self):
        account = self.mt5_fetcher.get_account_info()
        return account.equity if account else 706.88

    def create_ui(self):
        left_frame = tk.Frame(self.root, bg="#0a0a0a", width=740)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(left_frame, text=f"AI TRADING Terminal Grok Alpha AI [{self.version}]",
                 font=("Consolas", 14, "bold"), fg="#00ff00", bg="#0a0a0a").pack(anchor="w")
        tk.Label(left_frame, text=f"Symbol: {self.symbol} | 3-Layer LSTM + RSI Fusion + Stochastic",
                 font=("Consolas", 10), fg="#00ccff", bg="#0a0a0a").pack(anchor="w")

        self.stats_text = tk.Text(left_frame, height=17, bg="#111111", fg="#00ff00", font=("Consolas", 10))
        self.stats_text.pack(fill=tk.X, pady=8)

        self.conf_label = tk.Label(left_frame, text="AI CONFIDENCE: [####################] 33.0%",
                                   font=("Consolas", 13, "bold"), fg="#ffff00", bg="#0a0a0a")
        self.conf_label.pack(anchor="w", pady=6)

        tk.Label(left_frame, text="[RECENT LOGS] – 3-Layer LSTM + RSI Signals",
                 font=("Consolas", 10, "bold"), fg="#00ffff", bg="#0a0a0a").pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(left_frame, height=13, bg="#111111", fg="#00ffaa", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

        self.status_label = tk.Label(left_frame, text="🔴 Czekam na sygnał | Dynamic Holding Time: NEUTRAL",
                                     font=("Consolas", 11, "bold"), fg="#ff8800", bg="#0a0a0a")
        self.status_label.pack(anchor="w", pady=8)

        right_frame = tk.Frame(self.root, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.4), facecolor="#0a0a0a")
        self.ax.set_facecolor("#111111")
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        tk.Button(btn_frame, text="STOP & ZAMKNIJ", command=self.shutdown,
                  bg="#ff4444", fg="white", font=("Consolas", 11, "bold")).pack(side=tk.RIGHT, padx=25)
        tk.Button(btn_frame, text="Wyczyść logi", command=self.clear_logs,
                  bg="#333333", fg="white").pack(side=tk.RIGHT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def update_data(self):
        """Main loop: fetch tick, update bar data if new, compute signals, update UI."""
        try:
            # 1. Fetch current tick
            tick = self.mt5_fetcher.get_tick()
            if tick is None:
                logger.warning("No tick data")
                self.root.after(self.update_ms, self.update_data)
                return
            bid, ask = tick
            price = (bid + ask) / 2
            self.current_price = price
            self.prices.append(price)
            self.times.append(datetime.now())
            if len(self.prices) > 200:
                self.prices.pop(0)
                self.times.pop(0)

            # 2. Check for new bar
            new_rates, new_df = self.mt5_fetcher.get_new_bars()
            if new_df is not None:
                self.df = new_df
                # Update indicators from full OHLC
                self._update_indicators_from_df()
                # Update LSTM prediction
                self._update_lstm_prediction()

            # 3. Compute current slope
            slope = 0.0
            if len(self.prices) > 15:
                slope = np.polyfit(np.arange(len(self.prices)), self.prices, 1)[0] * 25

            # 4. Get current indicator values
            rsi = self.cached_indicators['rsi']
            stoch_k = self.cached_indicators['stoch_k']
            bb_pos = self.cached_indicators['bb_position']
            lstm_dir = self.lstm_dir

            # 5. Generate signal and confidence
            signal, hold_mode = self.signal_gen.generate_signal(slope, rsi, stoch_k, bb_pos, lstm_dir)
            confidence = self.signal_gen.compute_confidence(slope, rsi, stoch_k, lstm_dir, bb_pos)

            # 6. Log if signal and confidence >= threshold
            if signal and confidence >= self.conf_threshold:
                log_msg = (f"[{datetime.now().strftime('%H:%M:%S')}] [AI] {signal} | "
                           f"Conf:{confidence}% | LSTM+RSI:{lstm_dir} | StochK:{stoch_k:.1f} | {hold_mode}")
                self.logs.append(log_msg)
                if len(self.logs) > 15:
                    self.logs.pop(0)

            # 7. Update UI
            account = self.mt5_fetcher.get_account_info()
            self.update_terminal(price, bid, ask, slope, confidence, hold_mode,
                                 rsi, self.cached_indicators['macd_hist'], bb_pos,
                                 stoch_k, self.cached_indicators['stoch_d'], lstm_dir, account, signal)
            self.update_chart()

        except Exception as e:
            logger.error(f"Error in update loop: {traceback.format_exc()}")

        self.root.after(self.update_ms, self.update_data)

    def _update_indicators_from_df(self):
        """Recalculate all indicators from the full OHLC dataframe."""
        if self.df is None or len(self.df) == 0:
            return
        indicators = self.indicator_calc.calculate_all(self.df)
        self.cached_indicators.update(indicators)

    def _update_lstm_prediction(self):
        """Run LSTM prediction using the latest bar data."""
        if self.df is None or len(self.df) < self.seq_length:
            self.lstm_dir = 0
            return
        # Get last N close prices and RSI series
        close_series = self.df['close']
        rsi_series = self.indicator_calc.calculate_rsi_series(close_series)

        # Take last SEQ_LENGTH values
        price_seq = close_series.iloc[-self.seq_length:].values
        rsi_seq = rsi_series.iloc[-self.seq_length:].values

        # Predict
        pred_price = self.lstm.predict(price_seq, rsi_seq)
        if pred_price is not None:
            # Compare to the last bar's close (not current tick)
            last_close = close_series.iloc[-1]
            self.lstm_dir = 1 if pred_price > last_close else -1 if pred_price < last_close else 0
        else:
            self.lstm_dir = 0

    def update_terminal(self, price, bid, ask, slope, confidence, hold_mode,
                        rsi, hist, bb_pos, stoch_k, stoch_d, lstm_dir, account, signal):
        equity = account.equity if account else 706.88
        profit = equity - self.session_start
        stats = f"""EQUITY     : ${equity:.2f}
P/L        : ${profit:.2f}
SLOPE      : {slope:.4f}
Bid/Ask    : {bid:.3f} / {ask:.3f}

RSI 14     : {rsi:.1f}
MACD Hist  : {hist:+.4f}
BB Pos     : {bb_pos:+.1f}%
Stochastic : %K {stoch_k:.1f}  %D {stoch_d:.1f}

LSTM+RSI   : {'↑ BULLISH' if lstm_dir > 0 else '↓ BEARISH' if lstm_dir < 0 else 'NEUTRAL'} (3 layers)
AI CONF    : {confidence}%   REQ: {self.conf_threshold}%
TODAY PROFIT: +{profit:.2f} USD (Goal 15.00)
        """
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)

        bar = "#" * (confidence // 4) + " " * (20 - confidence // 4)
        self.conf_label.config(text=f"AI CONFIDENCE : [{bar}] {confidence}%")

        self.log_area.delete(1.0, tk.END)
        for log in self.logs[-13:]:
            self.log_area.insert(tk.END, log + "\n")

        self.status_label.config(
            text=f"{'🟢' if confidence >= self.conf_threshold else '🔴'} Sygnał: {signal or 'BRAK'} | Dynamic Holding Time: {hold_mode}",
            fg="#00ff00" if confidence >= self.conf_threshold else "#ff8800"
        )

    def update_chart(self):
        self.ax.clear()
        if len(self.prices) < 5:
            self.canvas.draw()
            return
        df_plot = pd.DataFrame({'time': self.times, 'close': self.prices})
        self.ax.plot(df_plot['time'], df_plot['close'], color="#00ffaa", linewidth=2.3)
        self.ax.set_title(f"{self.symbol} Live – 3-Layer LSTM + RSI Fusion (Refactored)", color="white", fontsize=13)
        self.ax.grid(True, alpha=0.3)
        self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        self.ax.tick_params(colors="#aaaaaa")
        for spine in self.ax.spines.values():
            spine.set_color("#555555")
        self.fig.tight_layout()
        self.canvas.draw()

    def clear_logs(self):
        self.logs.clear()
        self.log_area.delete(1.0, tk.END)

    def shutdown(self):
        self.mt5_fetcher.shutdown()
        self.root.destroy()

# ====================== ENTRY POINT ======================
if _name_ == "_main_":
    config = load_config()
    logger.info(f"Starting Grok Alpha AI {config['version']}")
    app = GrokAlphaGUI(config)
    app.root.mainloop()
    