import json
import logging
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import matplotlib.pyplot as plt
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
import tkinter as tk
from tkinter import scrolledtext

# ====================== LOGGING ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("grok_alpha.log"), logging.StreamHandler()],
)
logger = logging.getLogger("GrokAlpha")


# ====================== CONFIGURATION (validated) ======================
@dataclass
class IndicatorConfig:
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std: int = 2
    stoch_period: int = 14
    stoch_k_smooth: int = 3


@dataclass
class WeightConfig:
    slope: float = 0.28
    rsi: float = 0.22
    stochastic: float = 0.18
    lstm: float = 0.18
    bb: float = 0.14


@dataclass
class RiskConfig:
    max_position_size: float = 0.01
    max_risk_per_trade: float = 0.02
    stop_loss_points: int = 50
    take_profit_points: int = 100
    max_daily_loss: float = 0.05


@dataclass
class Config:
    symbol: str = "XAUUSD"
    version: str = "v2.5 – Production Ready"
    update_ms: int = 2000
    conf_threshold: int = 20
    seq_length: int = 60
    indicators: IndicatorConfig = field(default_factory=IndicatorConfig)
    weights: WeightConfig = field(default_factory=WeightConfig)
    slope_threshold: float = 0.7
    trend_slope_threshold: float = 1.3
    rsi_buy_max: int = 67
    rsi_sell_min: int = 33
    stoch_buy_max: int = 72
    stoch_sell_min: int = 28
    bb_buy_max: int = 38
    bb_sell_min: int = -38
    lstm_checkpoint: str = "model_checkpoint.pth"
    account_number: str = "168221144"
    broker: str = "XM Global Limited"
    server: str = "XMGLOBAL-MT5"
    risk: RiskConfig = field(default_factory=RiskConfig)

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load config from JSON file with basic validation."""
        with open(path, "r") as f:
            data = json.load(f)

        # Validate critical numeric fields (example)
        for key in ["update_ms", "conf_threshold", "seq_length"]:
            if key in data and not isinstance(data[key], int):
                raise ValueError(f"{key} must be an integer")
        if "seq_length" in data and data["seq_length"] < 10:
            raise ValueError("seq_length must be at least 10")

        data["indicators"] = IndicatorConfig(**data.get("indicators", {}))
        data["weights"] = WeightConfig(**data.get("weights", {}))
        data["risk"] = RiskConfig(**data.get("risk", {}))
        return cls(**data)


# ====================== MT5 CONNECTION (separate responsibility) ======================
class MT5Connection:
    """Handles MT5 initialisation, shutdown and basic info retrieval."""

    def __init__(self):
        self._connected = False

    def connect(self) -> bool:
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        self._connected = True
        return True

    def disconnect(self):
        if self._connected:
            mt5.shutdown()
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def select_symbol(self, symbol: str) -> bool:
        return mt5.symbol_select(symbol, True)

    def get_account_info(self):
        return mt5.account_info()

    def get_symbol_info(self, symbol: str):
        return mt5.symbol_info(symbol)

    def get_tick(self, symbol: str):
        tick = mt5.symbol_info_tick(symbol)
        return (tick.bid, tick.ask) if tick else None


# ====================== BAR STORAGE (incremental fetching) ======================
class BarStorage:
    """Manages OHLC bars with incremental updates."""

    def __init__(self, symbol: str, mt5_conn: MT5Connection):
        self.symbol = symbol
        self.mt5 = mt5_conn
        self.df: Optional[pd.DataFrame] = None
        self._last_bar_time: Optional[datetime] = None

    def fetch_initial_bars(self, max_bars: int = 350) -> bool:
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, max_bars)
        if rates is None or len(rates) == 0:
            logger.error("No initial bar data received")
            return False
        self.df = pd.DataFrame(rates)
        self.df["time"] = pd.to_datetime(self.df["time"], unit="s")
        self._last_bar_time = self.df["time"].iloc[-1]
        return True

    def fetch_new_bars(self) -> Optional[pd.DataFrame]:
        """Fetch only new bars since last known bar."""
        if self._last_bar_time is None:
            return None if not self.fetch_initial_bars() else self.df

        from_time = self._last_bar_time + timedelta(minutes=1)
        to_time = datetime.now()
        from_ts = int(from_time.timestamp())
        to_ts = int(to_time.timestamp())
        rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M1, from_ts, to_ts)
        if rates is None or len(rates) == 0:
            return None

        new_df = pd.DataFrame(rates)
        new_df["time"] = pd.to_datetime(new_df["time"], unit="s")
        self.df = (
            pd.concat([self.df, new_df], ignore_index=True)
            .drop_duplicates(subset=["time"])
            .sort_values("time")
        )
        # Keep only last 500 bars to prevent memory bloat
        if len(self.df) > 500:
            self.df = self.df.iloc[-500:]
        self._last_bar_time = self.df["time"].iloc[-1]
        return self.df


# ====================== INDICATOR CALCULATOR (with caching) ======================
class IndicatorCalculator:
    def __init__(self, config: IndicatorConfig):
        self.config = config
        self._cached_rsi_series: Optional[pd.Series] = None

    def compute_all(self, df: pd.DataFrame) -> Dict[str, float]:
        """Return latest indicator values and also cache the RSI series."""
        close = df["close"]
        high = df["high"]
        low = df["low"]

        # Compute RSI series once and cache
        self._cached_rsi_series = self._rsi_series(close)
        rsi_val = (
            self._cached_rsi_series.iloc[-1]
            if not self._cached_rsi_series.empty
            else 50.0
        )

        return {
            "rsi": rsi_val,
            "macd_hist": self._macd_hist(
                close,
                self.config.macd_fast,
                self.config.macd_slow,
                self.config.macd_signal,
            ),
            "bb_position": self._bb_position(
                close, self.config.bb_period, self.config.bb_std
            ),
            "stoch_k": self._stochastic_k(
                close, high, low, self.config.stoch_period, self.config.stoch_k_smooth
            ),
            "stoch_d": self._stochastic_d(
                close, high, low, self.config.stoch_period, self.config.stoch_k_smooth
            ),
        }

    def get_rsi_series(self) -> Optional[pd.Series]:
        """Return the last computed RSI series (used by LSTM)."""
        return self._cached_rsi_series

    def _rsi_series(self, close: pd.Series) -> pd.Series:
        period = self.config.rsi_period
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        return 100 - (100 / (1 + rs)).fillna(50)

    @staticmethod
    def _macd_hist(close: pd.Series, fast: int, slow: int, signal: int) -> float:
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return (macd - signal_line).iloc[-1]

    @staticmethod
    def _bb_position(close: pd.Series, period: int, std_mult: int) -> float:
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        bb_up = sma + std_mult * std
        bb_low = sma - std_mult * std
        denominator = bb_up - bb_low
        if denominator.iloc[-1] != 0:
            return (close.iloc[-1] - sma.iloc[-1]) / denominator.iloc[-1] * 100
        return 0.0

    @staticmethod
    def _stochastic_k(
        close: pd.Series, high: pd.Series, low: pd.Series, period: int, k_smooth: int
    ) -> float:
        low_min = low.rolling(period).min()
        high_max = high.rolling(period).max()
        k = 100 * (close - low_min) / (high_max - low_min + 1e-10)
        return k.iloc[-1] if not pd.isna(k.iloc[-1]) else 50.0

    @staticmethod
    def _stochastic_d(
        close: pd.Series, high: pd.Series, low: pd.Series, period: int, k_smooth: int
    ) -> float:
        low_min = low.rolling(period).min()
        high_max = high.rolling(period).max()
        k = 100 * (close - low_min) / (high_max - low_min + 1e-10)
        d = k.rolling(k_smooth).mean()
        return d.iloc[-1] if not pd.isna(d.iloc[-1]) else 50.0


# ====================== LSTM MODEL (thread-safe) ======================
class MultiFeatureLSTM(nn.Module):
    def __init__(
        self,
        input_size: int = 2,
        hidden_size: int = 64,
        num_layers: int = 3,
        dropout: float = 0.15,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=dropout
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


class LSTMModel:
    def __init__(
        self,
        input_size: int = 2,
        hidden_size: int = 64,
        num_layers: int = 3,
        dropout: float = 0.15,
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiFeatureLSTM(input_size, hidden_size, num_layers, dropout).to(
            self.device
        )
        self.model.eval()
        self.trained = False
        self._lock = threading.Lock()  # protect model state

    def load_checkpoint(self, path: str):
        p = Path(path)
        if p.exists():
            try:
                checkpoint = torch.load(p, map_location=self.device, weights_only=True)
                with self._lock:
                    self.model.load_state_dict(checkpoint["model_state_dict"])
                    self.trained = True
                logger.info(f"LSTM checkpoint loaded from {path}")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        else:
            logger.warning("No LSTM checkpoint found. Using random weights.")

    def predict(self, price_seq: np.ndarray, rsi_seq: np.ndarray) -> Optional[float]:
        if not self.trained or len(price_seq) != len(rsi_seq):
            return None
        seq = np.column_stack((price_seq, rsi_seq))
        seq = (seq - seq.mean(axis=0)) / (seq.std(axis=0) + 1e-8)
        seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            with self._lock:
                return self.model(seq_tensor).item()

    def train_mode(self, mode: bool = True):
        with self._lock:
            if mode:
                self.model.train()
            else:
                self.model.eval()


# ====================== LSTM TRAINER (background thread) ======================
class LSTMTrainer:
    def __init__(
        self,
        model: LSTMModel,
        bar_storage: BarStorage,
        indicator_calc: IndicatorCalculator,
        seq_length: int = 60,
        batch_size: int = 32,
        epochs: int = 10,
        interval: int = 300,
    ):
        self.model = model
        self.bar_storage = bar_storage
        self.indicator_calc = indicator_calc
        self.seq_length = seq_length
        self.batch_size = batch_size
        self.epochs = epochs
        self.interval = interval
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._training_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _training_loop(self):
        while not self._stop.wait(self.interval):
            self._train_once()

    def _train_once(self):
        df = self.bar_storage.df
        if df is None or len(df) < self.seq_length * 2:
            logger.debug("Not enough data for LSTM training")
            return
        logger.info("Starting LSTM training...")
        try:
            close = df["close"].values
            rsi = self.indicator_calc.get_rsi_series()
            if rsi is None or len(rsi) != len(close):
                # fallback: compute RSI series
                rsi = self.indicator_calc._rsi_series(df["close"]).values
            else:
                rsi = rsi.values

            # Use vectorized sliding windows for performance
            from numpy.lib.stride_tricks import sliding_window_view

            price_windows = sliding_window_view(close, window_shape=self.seq_length)
            rsi_windows = sliding_window_view(rsi, window_shape=self.seq_length)
            # Target: next close price after the window
            targets = close[self.seq_length :]

            X = np.stack(
                [price_windows, rsi_windows], axis=-1
            )  # shape (n_windows, seq_len, 2)
            y = targets

            # Normalize X
            mean = X.mean(axis=(0, 1), keepdims=True)
            std = X.std(axis=(0, 1), keepdims=True) + 1e-8
            X = (X - mean) / std

            X_tensor = torch.tensor(X, dtype=torch.float32)
            y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)

            optimizer = torch.optim.Adam(self.model.model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            self.model.train_mode(True)
            for epoch in range(self.epochs):
                for i in range(0, len(X_tensor), self.batch_size):
                    X_batch = X_tensor[i : i + self.batch_size]
                    y_batch = y_tensor[i : i + self.batch_size]
                    optimizer.zero_grad()
                    output = self.model.model(X_batch)
                    loss = criterion(output, y_batch)
                    loss.backward()
                    optimizer.step()
                logger.debug(f"Epoch {epoch+1}/{self.epochs} loss={loss.item():.6f}")
            self.model.train_mode(False)
            self.model.trained = True
            logger.info("LSTM training completed")
        except Exception as e:
            logger.error(f"Training failed: {e}")


# ====================== SIGNAL GENERATOR ======================
class SignalGenerator:
    def __init__(self, config: Config):
        self.config = config

    def generate(
        self, slope: float, rsi: float, stoch_k: float, bb_pos: float, lstm_dir: int
    ) -> Tuple[Optional[str], str]:
        slope_abs = abs(slope)
        if (
            slope_abs > self.config.slope_threshold
            and rsi < self.config.rsi_buy_max
            and stoch_k < self.config.stoch_buy_max
            and bb_pos < self.config.bb_buy_max
            and lstm_dir >= 0
        ):
            signal = "BUY"
        elif (
            slope_abs > self.config.slope_threshold
            and rsi > self.config.rsi_sell_min
            and stoch_k > self.config.stoch_sell_min
            and bb_pos > self.config.bb_sell_min
            and lstm_dir <= 0
        ):
            signal = "SELL"
        else:
            signal = None

        hold_mode = "NEUTRAL"
        if signal:
            hold_mode = (
                "TREND (minuty)"
                if slope_abs > self.config.trend_slope_threshold
                else "SCALPING (sekundy)"
            )
        return signal, hold_mode

    def confidence(
        self, slope: float, rsi: float, stoch_k: float, lstm_dir: int, bb_pos: float
    ) -> int:
        slope_abs = abs(slope)
        w = self.config.weights

        slope_score = 40 + slope_abs * 20
        rsi_score = 72 if rsi < 35 else 28 if rsi > 65 else 50
        stoch_score = 76 if stoch_k < 20 else 24 if stoch_k > 80 else 50
        lstm_score = 72 if lstm_dir == 1 else 28 if lstm_dir == -1 else 50
        bb_score = 70 if bb_pos < -40 else 70 if bb_pos > 40 else 50

        confidence = (
            w.slope * slope_score
            + w.rsi * rsi_score
            + w.stochastic * stoch_score
            + w.lstm * lstm_score
            + w.bb * bb_score
        )
        return int(max(33, min(85, confidence)))


# ====================== RISK MANAGER (with symbol info) ======================
class RiskManager:
    def __init__(self, config: RiskConfig, symbol_info: Any):
        self.config = config
        self.symbol_info = symbol_info

    def check_trade_allowed(
        self, signal: str, equity: float, open_positions: int, daily_pnl: float
    ) -> Tuple[bool, str]:
        if daily_pnl <= -self.config.max_daily_loss * equity:
            return False, "Daily loss limit reached"
        if open_positions >= 1:
            return False, "Already have an open position"
        return True, "OK"

    def calculate_lot_size(
        self, equity: float, price: float, stop_loss_points: int
    ) -> float:
        risk_amount = equity * self.config.max_risk_per_trade
        # Retrieve point value from symbol info (e.g., 0.001 for XAUUSD)
        point = self.symbol_info.point if self.symbol_info else 0.0001
        stop_loss_price_diff = stop_loss_points * point
        # Retrieve contract size (e.g., 100 for XAUUSD)
        contract_size = (
            self.symbol_info.trade_contract_size if self.symbol_info else 100000
        )
        lot_size = risk_amount / (stop_loss_price_diff * contract_size)
        lot_size = min(lot_size, self.config.max_position_size)
        # Also respect symbol's min/max volume
        if self.symbol_info:
            lot_size = max(lot_size, self.symbol_info.volume_min)
            lot_size = min(lot_size, self.symbol_info.volume_max)
        lot_size = round(lot_size, 2)
        return max(lot_size, 0.01)


# ====================== TRADE EXECUTOR (with validation) ======================
class TradeExecutor:
    def __init__(self, symbol: str, demo_mode: bool = True):
        self.symbol = symbol
        self.demo_mode = demo_mode
        self.open_positions: List[Dict] = []

    def place_order(
        self,
        signal: str,
        lot_size: float,
        stop_loss: float,
        take_profit: float,
        comment: str = "AI Signal",
    ) -> bool:
        if signal not in ("BUY", "SELL"):
            return False

        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            logger.error(f"Symbol {self.symbol} info not available")
            return False

        # Validate lot size
        if lot_size < symbol_info.volume_min or lot_size > symbol_info.volume_max:
            logger.error(
                f"Lot size {lot_size} out of allowed range "
                f"({symbol_info.volume_min}–{symbol_info.volume_max})"
            )
            return False

        order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            logger.error("No tick data for order")
            return False
        price = tick.ask if signal == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": 123456,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        if self.demo_mode:
            logger.info(
                f"[DEMO] {signal} {lot_size} lots at {price} (SL: {stop_loss}, TP: {take_profit})"
            )
            return True

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment} (retcode {result.retcode})")
            return False
        logger.info(f"Order placed: {signal} {lot_size} lots, ticket {result.order}")
        self.open_positions.append(
            {
                "ticket": result.order,
                "type": signal,
                "volume": lot_size,
                "open_price": price,
                "sl": stop_loss,
                "tp": take_profit,
            }
        )
        return True

    def close_all_positions(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return
        for pos in positions:
            if self.demo_mode:
                logger.info(f"[DEMO] Closing position {pos.ticket}")
                continue
            order_type = mt5.ORDER_TYPE_BUY if pos.type == 1 else mt5.ORDER_TYPE_SELL
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                continue
            price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "comment": "Close by AI",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to close position {pos.ticket}: {result.comment}")
        self.open_positions.clear()


# ====================== MAIN GUI (with dependency injection) ======================
class GrokAlphaGUI:
    def __init__(
        self,
        config: Config,
        mt5_conn: MT5Connection,
        bar_storage: BarStorage,
        indicator_calc: IndicatorCalculator,
        lstm_model: LSTMModel,
        signal_gen: SignalGenerator,
        risk_mgr: RiskManager,
        trade_exec: TradeExecutor,
    ):
        self.config = config
        self.mt5 = mt5_conn
        self.bar_storage = bar_storage
        self.indicator_calc = indicator_calc
        self.lstm = lstm_model
        self.signal_gen = signal_gen
        self.risk_mgr = risk_mgr
        self.trade_exec = trade_exec

        # Data buffers
        self.prices: List[float] = []
        self.times: List[datetime] = []
        self.cached_indicators: Dict[str, float] = {
            "rsi": 50.0,
            "macd_hist": 0.0,
            "bb_position": 0.0,
            "stoch_k": 50.0,
            "stoch_d": 50.0,
        }
        self.lstm_dir: int = 0
        self.current_price: Optional[float] = None
        self.logs: List[str] = []
        self.trade_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        self.ticks_processed: int = 0
        self.last_tick_time: float = time.time()
        self.ticks_per_second: float = 0.0
        self.session_start = self._get_initial_equity()

        # Background training
        self.trainer = LSTMTrainer(
            self.lstm,
            self.bar_storage,
            self.indicator_calc,
            seq_length=config.seq_length,
            interval=300,
        )
        self.trainer.start()

        # UI setup
        self.root = tk.Tk()
        self.root.title(
            f"CJ Smart Alpha AI [{config.version}] - Modern Quantitative Trading"
        )
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("1460x860")
        self._create_ui()

        # Start main loop
        self._update_data()

    def _get_initial_equity(self) -> float:
        acc = self.mt5.get_account_info()
        return acc.equity if acc else 706.88

    def _create_ui(self):
        """Build the dashboard UI (same as before, but now fully implemented)."""
        left_frame = tk.Frame(self.root, bg="#0a0a0a", width=740)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Title and path
        tk.Label(
            left_frame,
            text=f"CJ Smart Alpha AI [{self.config.version}] - (Modern Quantitative Trading)",
            font=("Consolas", 12, "bold"),
            fg="#00ff00",
            bg="#0a0a0a",
        ).pack(anchor="w")
        tk.Label(
            left_frame,
            text=f"[PATH]: {Path.cwd() / 'config.json'}",
            font=("Consolas", 9),
            fg="#888888",
            bg="#0a0a0a",
        ).pack(anchor="w")

        # Speed row
        speed_frame = tk.Frame(left_frame, bg="#0a0a0a")
        speed_frame.pack(anchor="w", pady=(10, 0))
        tk.Label(
            speed_frame,
            text="[SPEED]",
            font=("Consolas", 10, "bold"),
            fg="#ffaa00",
            bg="#0a0a0a",
        ).pack(side=tk.LEFT)
        self.speed_label = tk.Label(
            speed_frame,
            text="0.0000 ms",
            font=("Consolas", 10),
            fg="#ffaa00",
            bg="#0a0a0a",
        )
        self.speed_label.pack(side=tk.LEFT, padx=(5, 0))

        # Broker / Account info
        account_frame = tk.Frame(left_frame, bg="#0a0a0a")
        account_frame.pack(anchor="w", pady=5)
        tk.Label(
            account_frame,
            text=f"BROKER: {self.config.broker} | SERVER: {self.config.server}",
            font=("Consolas", 9),
            fg="#cccccc",
            bg="#0a0a0a",
        ).pack(anchor="w")
        tk.Label(
            account_frame,
            text=f"ACC: {self.config.account_number}",
            font=("Consolas", 9),
            fg="#cccccc",
            bg="#0a0a0a",
        ).pack(anchor="w")

        # Main stats grid
        stats_grid = tk.Frame(left_frame, bg="#0a0a0a")
        stats_grid.pack(anchor="w", pady=5)
        self.equity_label = tk.Label(
            stats_grid,
            text="EQUITY: $706.88",
            font=("Consolas", 11, "bold"),
            fg="#00ff00",
            bg="#0a0a0a",
        )
        self.equity_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        self.pl_label = tk.Label(
            stats_grid,
            text="P/L: +$0.00 ▲",
            font=("Consolas", 11, "bold"),
            fg="#00ff00",
            bg="#0a0a0a",
        )
        self.pl_label.grid(row=0, column=1, sticky="w")
        self.margin_label = tk.Label(
            stats_grid,
            text="MARGIN: $0.00",
            font=("Consolas", 10),
            fg="#cccccc",
            bg="#0a0a0a",
        )
        self.margin_label.grid(row=1, column=0, sticky="w")
        self.free_label = tk.Label(
            stats_grid,
            text="FREE: $706.88",
            font=("Consolas", 10),
            fg="#cccccc",
            bg="#0a0a0a",
        )
        self.free_label.grid(row=1, column=1, sticky="w")
        self.level_label = tk.Label(
            stats_grid,
            text="LEVEL: 0.00%",
            font=("Consolas", 10),
            fg="#cccccc",
            bg="#0a0a0a",
        )
        self.level_label.grid(row=2, column=0, sticky="w")

        # Positions
        self.positions_label = tk.Label(
            left_frame,
            text="POSITIONS: 0",
            font=("Consolas", 10),
            fg="#ffff00",
            bg="#0a0a0a",
        )
        self.positions_label.pack(anchor="w", pady=5)

        # DB / Speed counters
        db_frame = tk.Frame(left_frame, bg="#0a0a0a")
        db_frame.pack(anchor="w", pady=5)
        self.db_label = tk.Label(
            db_frame,
            text="DB: 0 / 0 (0.0%) | SPD: 0.0 p/s",
            font=("Consolas", 9),
            fg="#00ccff",
            bg="#0a0a0a",
        )
        self.db_label.pack(side=tk.LEFT)

        # BUY/SELL/HOLD counters
        trade_counts_frame = tk.Frame(left_frame, bg="#0a0a0a")
        trade_counts_frame.pack(anchor="w", pady=2)
        self.buy_count_label = tk.Label(
            trade_counts_frame,
            text="BUY: 0 (0.0%)",
            font=("Consolas", 9),
            fg="#00ffaa",
            bg="#0a0a0a",
        )
        self.buy_count_label.pack(side=tk.LEFT, padx=(0, 10))
        self.sell_count_label = tk.Label(
            trade_counts_frame,
            text="SELL: 0 (0.0%)",
            font=("Consolas", 9),
            fg="#ff6666",
            bg="#0a0a0a",
        )
        self.sell_count_label.pack(side=tk.LEFT, padx=(0, 10))
        self.hold_count_label = tk.Label(
            trade_counts_frame,
            text="HOLD: 0",
            font=("Consolas", 9),
            fg="#ffff00",
            bg="#0a0a0a",
        )
        self.hold_count_label.pack(side=tk.LEFT)

        # AI Confidence section
        conf_frame = tk.Frame(left_frame, bg="#0a0a0a")
        conf_frame.pack(anchor="w", pady=8)
        self.conf_text = tk.Label(
            conf_frame,
            text="AI CONFIDENCE: 33.0%",
            font=("Consolas", 12, "bold"),
            fg="#ffff00",
            bg="#0a0a0a",
        )
        self.conf_text.pack(anchor="w")
        self.signal_ready = tk.Label(
            conf_frame,
            text="AC SIGNAL READY: 0.00%",
            font=("Consolas", 10),
            fg="#ffaa00",
            bg="#0a0a0a",
        )
        self.signal_ready.pack(anchor="w")

        # Additional metrics
        self.extra_frame = tk.Frame(left_frame, bg="#0a0a0a")
        self.extra_frame.pack(anchor="w", pady=5)
        self.slope_label = tk.Label(
            self.extra_frame,
            text="SLOPE: 0.00000 | Bid: 0.000 | SPREAD: 0.0",
            font=("Consolas", 9),
            fg="#cccccc",
            bg="#0a0a0a",
        )
        self.slope_label.pack(anchor="w")
        self.diff_label = tk.Label(
            self.extra_frame,
            text="DIFF: 0.00000 | CONF: 0% | REQ: 0%",
            font=("Consolas", 9),
            fg="#cccccc",
            bg="#0a0a0a",
        )
        self.diff_label.pack(anchor="w")

        # Log area
        tk.Label(
            left_frame,
            text="RECENT LOGS",
            font=("Consolas", 10, "bold"),
            fg="#00ffff",
            bg="#0a0a0a",
        ).pack(anchor="w", pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(
            left_frame, height=13, bg="#111111", fg="#00ffaa", font=("Consolas", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # Right frame (chart)
        right_frame = tk.Frame(self.root, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.4), facecolor="#0a0a0a")
        self.ax.set_facecolor("#111111")
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom buttons
        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        tk.Button(
            btn_frame,
            text="STOP & ZAMKNIJ",
            command=self.shutdown,
            bg="#ff4444",
            fg="white",
            font=("Consolas", 11, "bold"),
        ).pack(side=tk.RIGHT, padx=25)
        tk.Button(
            btn_frame,
            text="Wyczyść logi",
            command=self.clear_logs,
            bg="#333333",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def _update_data(self):
        start = time.perf_counter()
        try:
            # 1. Get tick
            tick = self.mt5.get_tick(self.config.symbol)
            if not tick:
                self.root.after(self.config.update_ms, self._update_data)
                return
            bid, ask = tick
            price = (bid + ask) / 2
            self.current_price = price
            self.prices.append(price)
            self.times.append(datetime.now())
            if len(self.prices) > 200:
                self.prices.pop(0)
                self.times.pop(0)

            # 2. Check for new bars
            new_df = self.bar_storage.fetch_new_bars()
            if new_df is not None:
                # Update indicators from full OHLC
                ind = self.indicator_calc.compute_all(self.bar_storage.df)
                self.cached_indicators.update(ind)
                # Update LSTM prediction
                self._update_lstm_prediction()

            # 3. Compute slope
            slope = 0.0
            if len(self.prices) > 15:
                slope = np.polyfit(np.arange(len(self.prices)), self.prices, 1)[0] * 25

            # 4. Current indicators
            rsi = self.cached_indicators["rsi"]
            stoch_k = self.cached_indicators["stoch_k"]
            bb_pos = self.cached_indicators["bb_position"]
            lstm_dir = self.lstm_dir

            # 5. Signal and confidence
            signal, hold_mode = self.signal_gen.generate(
                slope, rsi, stoch_k, bb_pos, lstm_dir
            )
            confidence = self.signal_gen.confidence(
                slope, rsi, stoch_k, lstm_dir, bb_pos
            )

            # 6. Risk & execution
            if signal and confidence >= self.config.conf_threshold:
                acc = self.mt5.get_account_info()
                equity = acc.equity if acc else 0.0
                daily_pnl = equity - self.session_start
                allowed, reason = self.risk_mgr.check_trade_allowed(
                    signal, equity, len(self.trade_exec.open_positions), daily_pnl
                )
                if allowed:
                    symbol_info = self.mt5.get_symbol_info(self.config.symbol)
                    point = symbol_info.point if symbol_info else 0.0001
                    stop_loss = (
                        price - self.config.risk.stop_loss_points * point
                        if signal == "BUY"
                        else price + self.config.risk.stop_loss_points * point
                    )
                    take_profit = (
                        price + self.config.risk.take_profit_points * point
                        if signal == "BUY"
                        else price - self.config.risk.take_profit_points * point
                    )
                    lot_size = self.risk_mgr.calculate_lot_size(
                        equity, price, self.config.risk.stop_loss_points
                    )
                    success = self.trade_exec.place_order(
                        signal, lot_size, stop_loss, take_profit
                    )
                    if success:
                        self.logs.append(
                            f"{datetime.now().strftime('%H:%M:%S')} [EXEC] {signal} {lot_size} lots @ {price}"
                        )
                        self.trade_counts[signal] += 1
                    else:
                        self.logs.append(
                            f"{datetime.now().strftime('%H:%M:%S')} [EXEC] {signal} failed"
                        )
                else:
                    self.logs.append(
                        f"{datetime.now().strftime('%H:%M:%S')} [MM] {signal} Blocked: {reason}"
                    )
                if len(self.logs) > 15:
                    self.logs.pop(0)

            # 7. Update UI (with cached account info)
            account = self.mt5.get_account_info()
            self._update_ui(
                price,
                bid,
                ask,
                slope,
                confidence,
                hold_mode,
                rsi,
                self.cached_indicators["macd_hist"],
                bb_pos,
                stoch_k,
                self.cached_indicators["stoch_d"],
                lstm_dir,
                signal,
                account,
            )

            # 8. Tick rate
            self.ticks_processed += 1
            now = time.time()
            if now - self.last_tick_time >= 1.0:
                self.ticks_per_second = self.ticks_processed / (
                    now - self.last_tick_time
                )
                self.ticks_processed = 0
                self.last_tick_time = now

            # 9. Chart
            self._update_chart()

        except Exception:
            logger.error(traceback.format_exc())

        elapsed_ms = (time.perf_counter() - start) * 1000
        self.speed_label.config(text=f"{elapsed_ms:.4f} ms")
        self.root.after(self.config.update_ms, self._update_data)

    def _update_lstm_prediction(self):
        """Update LSTM direction using cached RSI series."""
        df = self.bar_storage.df
        if df is None or len(df) < self.config.seq_length:
            self.lstm_dir = 0
            return
        close = df["close"]
        rsi_series = self.indicator_calc.get_rsi_series()
        if rsi_series is None:
            self.lstm_dir = 0
            return
        price_seq = close.iloc[-self.config.seq_length :].values
        rsi_seq = rsi_series.iloc[-self.config.seq_length :].values
        pred = self.lstm.predict(price_seq, rsi_seq)
        if pred is not None:
            last_close = close.iloc[-1]
            self.lstm_dir = 1 if pred > last_close else -1 if pred < last_close else 0
        else:
            self.lstm_dir = 0

    def _update_ui(
        self,
        price,
        bid,
        ask,
        slope,
        confidence,
        hold_mode,
        rsi,
        hist,
        bb_pos,
        stoch_k,
        stoch_d,
        lstm_dir,
        signal,
        account,
    ):
        equity = account.equity if account else 706.88
        profit = equity - self.session_start
        margin = account.margin if account else 0.0
        free_margin = account.margin_free if account else 0.0
        level = account.margin_level if account else 0.0
        positions = account.positions_total if account else 0

        self.equity_label.config(text=f"EQUITY: ${equity:.2f}")
        self.pl_label.config(text=f"P/L: {'+' if profit >= 0 else ''}{profit:.2f} ▲")
        self.margin_label.config(text=f"MARGIN: ${margin:.2f}")
        self.free_label.config(text=f"FREE: ${free_margin:.2f}")
        self.level_label.config(text=f"LEVEL: {level:.2f}%")
        self.positions_label.config(text=f"POSITIONS: {positions}")

        db_count = len(self.bar_storage.df) if self.bar_storage.df is not None else 0
        self.db_label.config(
            text=f"DB: {db_count} / 0 (0.0%) | SPD: {self.ticks_per_second:.1f} p/s"
        )

        total_trades = sum(self.trade_counts.values())
        buy_pct = (self.trade_counts["BUY"] / total_trades * 100) if total_trades else 0
        sell_pct = (
            (self.trade_counts["SELL"] / total_trades * 100) if total_trades else 0
        )
        self.buy_count_label.config(
            text=f"BUY: {self.trade_counts['BUY']} ({buy_pct:.1f}%)"
        )
        self.sell_count_label.config(
            text=f"SELL: {self.trade_counts['SELL']} ({sell_pct:.1f}%)"
        )
        self.hold_count_label.config(text=f"HOLD: {self.trade_counts['HOLD']}")

        self.conf_text.config(text=f"AI CONFIDENCE: {confidence}.0%")
        self.signal_ready.config(
            text=f"AC SIGNAL READY: {confidence/self.config.conf_threshold*100:.2f}%"
        )

        spread = (
            (ask - bid) * 10000 if self.mt5.get_symbol_info(self.config.symbol) else 0
        )
        diff = 0.0
        if self.bar_storage.df is not None and len(self.bar_storage.df) > 0:
            diff = price - self.bar_storage.df["close"].iloc[-1]

        self.slope_label.config(
            text=f"SLOPE: {slope:.5f} | Bid: {bid:.3f} | SPREAD: {spread:.1f}"
        )
        self.diff_label.config(
            text=f"DIFF: {diff:.5f} | CONF: {confidence}% | REQ: {self.config.conf_threshold}%"
        )

        self.log_area.delete(1.0, tk.END)
        for log in self.logs[-13:]:
            self.log_area.insert(tk.END, log + "\n")

    def _update_chart(self):
        self.ax.clear()
        if len(self.prices) < 5:
            self.canvas.draw()
            return
        df_plot = pd.DataFrame({"time": self.times, "close": self.prices})
        self.ax.plot(df_plot["time"], df_plot["close"], color="#00ffaa", linewidth=2.3)
        self.ax.set_title(
            f"{self.config.symbol} Live – 3-Layer LSTM + RSI Fusion (Quant Dashboard)",
            color="white",
            fontsize=13,
        )
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
        self.trainer.stop()
        self.trade_exec.close_all_positions()
        self.mt5.disconnect()
        self.root.destroy()


# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    cfg = Config.from_file("config.json")

    # Create dependencies
    mt5_conn = MT5Connection()
    if not mt5_conn.connect():
        logger.error("MT5 connection failed")
        exit(1)
    if not mt5_conn.select_symbol(cfg.symbol):
        logger.warning(f"Symbol {cfg.symbol} not available, but continuing")

    bar_storage = BarStorage(cfg.symbol, mt5_conn)
    indicator_calc = IndicatorCalculator(cfg.indicators)
    lstm_model = LSTMModel()
    lstm_model.load_checkpoint(cfg.lstm_checkpoint)
    signal_gen = SignalGenerator(cfg)

    # Get symbol info for risk manager
    symbol_info = mt5_conn.get_symbol_info(cfg.symbol)
    risk_mgr = RiskManager(cfg.risk, symbol_info)
    trade_exec = TradeExecutor(cfg.symbol, demo_mode=True)  # Set False for live

    # Pass all dependencies to GUI
    app = GrokAlphaGUI(
        cfg,
        mt5_conn,
        bar_storage,
        indicator_calc,
        lstm_model,
        signal_gen,
        risk_mgr,
        trade_exec,
    )
    app.root.mainloop()
