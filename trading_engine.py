from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np

from indicators import IndicatorCalculator
from lstm_model import LSTMModel
from mt5_fetcher import MT5DataFetcher
from risk_manager import PropRiskConfig, PropRiskManager
from signal_generator import SignalGenerator

logger = logging.getLogger("GrokAlpha")


@dataclass(frozen=True)
class EngineSnapshot:
    ts: datetime
    bid: float
    ask: float
    price: float
    slope: float
    rsi: float
    macd_hist: float
    bb_pos: float
    stoch_k: float
    stoch_d: float
    lstm_dir: int
    signal: Optional[str]
    hold_mode: str
    confidence: int
    equity: Optional[float]
    risk_ok: bool
    risk_reason: str


class TradingEngine:
    """
    Background engine:
    - fetch tick + bars from MT5
    - compute indicators + LSTM direction
    - compute signal + confidence
    - apply prop-like risk guard (no order placement here)
    - publish snapshots to a queue (GUI thread consumes)
    """

    def __init__(self, config: dict, out_queue: "queue.Queue[EngineSnapshot]"):
        self.config = config
        self.out_queue = out_queue

        self.symbol = config["symbol"]
        self.update_ms = int(config["update_ms"])
        self.seq_length = int(config["seq_length"])

        self.mt5 = MT5DataFetcher(self.symbol)
        self.indicators = IndicatorCalculator(config["indicators"])
        self.lstm = LSTMModel()
        self.lstm.load_checkpoint(config["lstm_checkpoint"])
        self.signal_gen = SignalGenerator(config)

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._prices: list[float] = []
        self._last_df = None
        self._cached = {
            "rsi": 50.0,
            "macd_hist": 0.0,
            "bb_position": 0.0,
            "stoch_k": 50.0,
            "stoch_d": 50.0,
        }
        self._lstm_dir = 0

        self._risk: Optional[PropRiskManager] = None

    def start(self) -> None:
        if not self.mt5.initialize():
            raise RuntimeError("Cannot initialize MT5")

        acc = self.mt5.get_account_info()
        initial_equity = acc.equity if acc else 706.88
        risk_cfg = PropRiskConfig(
            max_daily_loss=float(self.config.get("max_daily_loss", 0.05)),
            max_drawdown=float(self.config.get("max_drawdown", 0.10)),
            daily_profit_target=float(self.config.get("daily_profit_target", 0.03)),
            max_daily_trades=int(self.config.get("max_daily_trades", 5)),
            confidence_threshold=int(self.config.get("conf_threshold", 56)),
        )
        self._risk = PropRiskManager(risk_cfg, initial_equity=float(initial_equity))

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        try:
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
        finally:
            self.mt5.shutdown()

    def _publish(self, snap: EngineSnapshot) -> None:
        try:
            self.out_queue.put_nowait(snap)
        except queue.Full:
            try:
                _ = self.out_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.out_queue.put_nowait(snap)
            except queue.Full:
                pass

    def _update_from_df(self, df) -> None:
        self._cached.update(self.indicators.calculate_all(df))

        if len(df) < self.seq_length:
            self._lstm_dir = 0
            return

        close_series = df["close"]
        rsi_series = self.indicators.calculate_rsi_series(close_series)
        price_seq = close_series.iloc[-self.seq_length :].values
        rsi_seq = rsi_series.iloc[-self.seq_length :].values
        pred_price = self.lstm.predict(price_seq, rsi_seq)
        if pred_price is None:
            self._lstm_dir = 0
            return

        last_close = close_series.iloc[-1]
        if pred_price > last_close:
            self._lstm_dir = 1
        elif pred_price < last_close:
            self._lstm_dir = -1
        else:
            self._lstm_dir = 0

    def _compute_slope(self) -> float:
        if len(self._prices) <= 15:
            return 0.0
        slope_factor = float(self.config.get("slope_factor", 25))
        slope = np.polyfit(np.arange(len(self._prices)), self._prices, 1)[0] * slope_factor
        return float(slope)

    def _run(self) -> None:
        sleep_s = max(0.25, self.update_ms / 1000.0)
        while not self._stop.is_set():
            try:
                tick = self.mt5.get_tick()
                if tick is None:
                    time.sleep(sleep_s)
                    continue

                bid, ask = tick
                price = (bid + ask) / 2.0

                self._prices.append(price)
                if len(self._prices) > 200:
                    self._prices.pop(0)

                _, new_df = self.mt5.get_new_bars()
                if new_df is not None:
                    self._last_df = new_df
                    self._update_from_df(new_df)

                slope = self._compute_slope()

                rsi = float(self._cached["rsi"])
                stoch_k = float(self._cached["stoch_k"])
                bb_pos = float(self._cached["bb_position"])
                signal, hold_mode = self.signal_gen.generate_signal(
                    slope, rsi, stoch_k, bb_pos, self._lstm_dir
                )
                confidence = int(
                    self.signal_gen.compute_confidence(
                        slope, rsi, stoch_k, self._lstm_dir, bb_pos
                    )
                )

                acc = self.mt5.get_account_info()
                equity = acc.equity if acc else None

                risk_ok = True
                risk_reason = "OK"
                if self._risk and equity is not None:
                    risk_ok, risk_reason = self._risk.can_trade(equity, confidence)

                self._publish(
                    EngineSnapshot(
                        ts=datetime.now(),
                        bid=float(bid),
                        ask=float(ask),
                        price=float(price),
                        slope=float(slope),
                        rsi=float(self._cached["rsi"]),
                        macd_hist=float(self._cached["macd_hist"]),
                        bb_pos=float(self._cached["bb_position"]),
                        stoch_k=float(self._cached["stoch_k"]),
                        stoch_d=float(self._cached["stoch_d"]),
                        lstm_dir=int(self._lstm_dir),
                        signal=signal,
                        hold_mode=str(hold_mode),
                        confidence=int(confidence),
                        equity=float(equity) if equity is not None else None,
                        risk_ok=bool(risk_ok),
                        risk_reason=str(risk_reason),
                    )
                )
            except Exception:
                logger.exception("Engine loop error")

            time.sleep(sleep_s)

