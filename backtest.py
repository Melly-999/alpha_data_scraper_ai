"""Backtesting engine with performance metrics (Sharpe, drawdown, win rate)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Callable, Tuple
import logging

try:
    import MetaTrader5 as mt5  # type: ignore
except ImportError:  # pragma: no cover - MT5 is optional (Linux/CI)
    mt5 = None  # type: ignore[assignment]
import numpy as np
import pandas as pd

logger = logging.getLogger("Backtest")


@dataclass
class Trade:
    """Single trade record."""

    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    signal: str = "BUY"  # "BUY" or "SELL"
    pnl: float = 0.0  # Profit/Loss
    pnl_pct: float = 0.0  # PnL %
    status: str = "OPEN"  # "OPEN", "CLOSED", "CANCELLED"


@dataclass
class BacktestMetrics:
    """Comprehensive backtest performance metrics."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # 0-1
    total_return: float  # %
    annual_return: float  # %
    sharpe_ratio: float
    max_drawdown: float  # %
    drawdown_duration: timedelta
    avg_win: float  # %
    avg_loss: float  # %
    profit_factor: float  # gross_profit / gross_loss
    consecutive_wins: int
    consecutive_losses: int
    start_date: datetime
    end_date: datetime
    period_days: int
    trades: List[Trade] = field(default_factory=list)

    def summary_str(self) -> str:
        """Return formatted summary."""
        return f"""
╔══════════════════════════════════════════════════════╗
║           BACKTEST PERFORMANCE REPORT                ║
╠══════════════════════════════════════════════════════╣
║ Period: {self.start_date.strftime('%Y-%m-%d')} ~ {self.end_date.strftime('%Y-%m-%d')} ({self.period_days}d)
║ Total Trades: {self.total_trades} | Wins: {self.winning_trades} | Losses: {self.losing_trades}
║ Win Rate: {self.win_rate*100:.2f}% | Total Return: {self.total_return:+.2f}%
║ Annual Return: {self.annual_return:+.2f}% | Sharpe: {self.sharpe_ratio:.2f}
║ Max Drawdown: {self.max_drawdown:.2f}% (Duration: {self.drawdown_duration.days}d)
║ Avg Win: {self.avg_win:.2f}% | Avg Loss: {self.avg_loss:.2f}%
║ Profit Factor: {self.profit_factor:.2f}x
║ Consecutive: {self.consecutive_wins}W / {self.consecutive_losses}L
╚══════════════════════════════════════════════════════╝
"""


class BacktestEngine:
    """Run backtest on historical data."""

    def __init__(
        self,
        symbol: str,
        initial_balance: float = 10000.0,
        risk_per_trade: float = 0.01,
    ):
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_balance]
        self.equity_timestamps: List[datetime] = []

    def backtest(
        self,
        signal_func: Callable[[pd.DataFrame], Tuple[str, float]],
        start_date: datetime,
        end_date: datetime,
        lookback_bars: int = 100,
    ) -> Optional[BacktestMetrics]:
        """
        Run backtest using signal function over historical data.

        Args:
            signal_func: Function that takes OHLC DataFrame and returns (signal, confidence).
            start_date: Backtest start date (UTC).
            end_date: Backtest end date (UTC).
            lookback_bars: Number of bars for indicators.

        Returns:
            BacktestMetrics object or None on error.
        """
        # Fetch historical data
        try:
            logger.info(
                f"Fetching {self.symbol} data from {start_date} to {end_date}..."
            )
            df = self._fetch_historical_data(start_date, end_date, lookback_bars)
            if df is None or len(df) == 0:
                logger.error("No data fetched")
                return None
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return None

        logger.info(f"Running backtest on {len(df)} bars...")

        self.balance = self.initial_balance
        self.trades = []
        self.equity_curve = [self.initial_balance]
        self.equity_timestamps = [df.iloc[0]["time"]]

        open_position: Optional[Trade] = None

        for i in range(lookback_bars, len(df)):
            # Compute signal from historical window
            window = df.iloc[i - lookback_bars : i + 1]
            try:
                signal, confidence = signal_func(window)
            except Exception as e:
                logger.debug(f"Signal error at {i}: {e}")
                continue

            current_time = df.iloc[i]["time"]
            current_close = float(df.iloc[i]["close"])

            # Position management
            if open_position is None:
                # Open new trade if signal is strong
                if signal in ["BUY", "SELL"] and confidence >= 60:
                    lot_size = self._calculate_lot_size(current_close)
                    open_position = Trade(
                        entry_time=current_time,
                        entry_price=current_close,
                        signal=signal,
                    )
                    logger.debug(
                        f"OPEN {signal} @ {current_close:.5f} ({lot_size:.2f} lots)"
                    )
            else:
                # Close position after N bars or on opposite signal
                bars_held = i - list(df.iloc[lookback_bars : i + 1]["time"]).index(
                    open_position.entry_time
                )
                # Simple: hold for max 50 bars or close on opposite signal
                should_close = (
                    bars_held > 50
                    or (open_position.signal == "BUY" and signal == "SELL")
                    or (open_position.signal == "SELL" and signal == "BUY")
                )

                if should_close:
                    open_position.exit_time = current_time
                    open_position.exit_price = current_close
                    open_position.status = "CLOSED"

                    # Calculate PnL
                    if open_position.signal == "BUY":
                        pnl_pct = (
                            (current_close - open_position.entry_price)
                            / open_position.entry_price
                            * 100
                        )
                    else:
                        pnl_pct = (
                            (open_position.entry_price - current_close)
                            / open_position.entry_price
                            * 100
                        )

                    open_position.pnl_pct = pnl_pct
                    open_position.pnl = self.balance * (pnl_pct / 100)
                    self.balance += open_position.pnl

                    self.trades.append(open_position)
                    logger.debug(
                        f"CLOSE {open_position.signal} @ {current_close:.5f} "
                        f"(PnL: {pnl_pct:+.2f}%)"
                    )

                    open_position = None

            # Update equity curve
            if open_position:
                # Unrealized PnL
                if open_position.signal == "BUY":
                    unrealized_pnl_pct = (
                        (current_close - open_position.entry_price)
                        / open_position.entry_price
                        * 100
                    )
                else:
                    unrealized_pnl_pct = (
                        (open_position.entry_price - current_close)
                        / open_position.entry_price
                        * 100
                    )
                equity = self.balance + (self.balance * unrealized_pnl_pct / 100)
            else:
                equity = self.balance

            self.equity_curve.append(equity)
            self.equity_timestamps.append(current_time)

        # Close any open position
        if open_position:
            last_close = float(df.iloc[-1]["close"])
            open_position.exit_time = df.iloc[-1]["time"]
            open_position.exit_price = last_close
            open_position.status = "CLOSED"

            if open_position.signal == "BUY":
                pnl_pct = (
                    (last_close - open_position.entry_price)
                    / open_position.entry_price
                    * 100
                )
            else:
                pnl_pct = (
                    (open_position.entry_price - last_close)
                    / open_position.entry_price
                    * 100
                )

            open_position.pnl_pct = pnl_pct
            open_position.pnl = self.balance * (pnl_pct / 100)
            self.balance += open_position.pnl
            self.trades.append(open_position)

        logger.info(f"Backtest complete: {len(self.trades)} trades")

        # Compute metrics
        metrics = self._compute_metrics(df.iloc[0]["time"], df.iloc[-1]["time"])
        return metrics

    def _fetch_historical_data(
        self,
        start_date: datetime,
        end_date: datetime,
        lookback_bars: int,
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLC data from MT5."""
        if mt5 is None:
            logger.warning(
                "MetaTrader5 not available — _fetch_historical_data returning "
                "None. Tests should patch this method."
            )
            return None

        # Extend start_date for lookback
        extended_start = start_date - timedelta(
            days=max(int(lookback_bars * 1.5 / 1440), 7)
        )

        from_ts = int(extended_start.timestamp())
        to_ts = int(end_date.timestamp())

        rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M1, from_ts, to_ts)
        if rates is None or len(rates) == 0:
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        # Filter to requested range
        df = df[(df["time"] >= start_date) & (df["time"] <= end_date)]
        return df.reset_index(drop=True)

    def _calculate_lot_size(self, current_price: float) -> float:
        """Calculate lot size based on risk per trade."""
        risk_amount = self.balance * self.risk_per_trade
        # Assume 100 pips stop loss
        sl_price_diff = 0.0100 if self.symbol.startswith(("EUR", "GBP")) else 100
        lot_size = risk_amount / sl_price_diff
        return max(0.01, min(lot_size, 1.0))  # Cap at 1 lot

    def _compute_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> BacktestMetrics:
        """Compute performance metrics from trades."""
        period_days = (end_date - start_date).days + 1

        if not self.trades:
            return BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_return=0.0,
                annual_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                drawdown_duration=timedelta(0),
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                consecutive_wins=0,
                consecutive_losses=0,
                start_date=start_date,
                end_date=end_date,
                period_days=period_days,
                trades=[],
            )

        # Basic stats
        closed_trades = [t for t in self.trades if t.status == "CLOSED"]
        pnl_pcts = [t.pnl_pct for t in closed_trades if t.pnl_pct is not None]
        winning = [p for p in pnl_pcts if p > 0]
        losing = [p for p in pnl_pcts if p < 0]

        total_return = (
            (self.balance - self.initial_balance) / self.initial_balance
        ) * 100
        annual_return = total_return * (365 / period_days)

        win_rate = len(winning) / len(pnl_pcts) if pnl_pcts else 0.0
        avg_win = np.mean(winning) if winning else 0.0
        avg_loss = np.mean(losing) if losing else 0.0

        # Sharpe ratio
        if len(pnl_pcts) > 1:
            returns = np.array(pnl_pcts) / 100
            sharpe = (
                np.mean(returns) / np.std(returns) * np.sqrt(252)
                if np.std(returns) > 0
                else 0.0
            )
        else:
            sharpe = 0.0

        # Max drawdown
        max_dd, dd_duration = self._calculate_max_drawdown()

        # Consecutive wins/losses
        max_consec_w, max_consec_l = self._calculate_consecutive(pnl_pcts)

        # Profit factor
        gross_profit = sum(winning) if winning else 0
        gross_loss = abs(sum(losing)) if losing else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        return BacktestMetrics(
            total_trades=len(closed_trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=win_rate,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            drawdown_duration=dd_duration,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            consecutive_wins=max_consec_w,
            consecutive_losses=max_consec_l,
            start_date=start_date,
            end_date=end_date,
            period_days=period_days,
            trades=closed_trades,
        )

    def _calculate_max_drawdown(self) -> Tuple[float, timedelta]:
        """Calculate maximum drawdown from equity curve."""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return 0.0, timedelta(0)

        equity = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100

        max_dd_idx = np.argmin(drawdown)
        max_dd = abs(drawdown[max_dd_idx])

        # Duration: from peak to recovery
        peak_idx = np.argmax(equity[: max_dd_idx + 1]) if max_dd_idx > 0 else 0
        recovery_idx = max_dd_idx
        for i in range(max_dd_idx + 1, len(equity)):
            if equity[i] >= equity[peak_idx]:
                recovery_idx = i
                break

        dd_duration = timedelta(minutes=int(recovery_idx - peak_idx))
        return max_dd, dd_duration

    @staticmethod
    def _calculate_consecutive(pnl_pcts: List[float]) -> Tuple[int, int]:
        """Calculate max consecutive wins and losses."""
        max_w, max_l = 0, 0
        curr_w, curr_l = 0, 0

        for pnl in pnl_pcts:
            if pnl > 0:
                curr_w += 1
                max_w = max(max_w, curr_w)
                curr_l = 0
            elif pnl < 0:
                curr_l += 1
                max_l = max(max_l, curr_l)
                curr_w = 0

        return max_w, max_l
