# brokers/alpaca_broker.py
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class AlpacaBroker:
    """Alpaca Broker - commission-free US stocks"""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.paper = paper

    def connect(self) -> bool:
        try:
            self.trading_client.get_account()
            logger.info(f"✅ Alpaca {'PAPER' if self.paper else 'LIVE'} connected")
            return True
        except Exception as e:
            logger.error(f"Alpaca connection error: {e}")
            return False

    def get_historical_data(
        self, symbol: str, timeframe: str = "1h", limit: int = 500
    ) -> pd.DataFrame:
        try:
            tf_map = {
                "1h": TimeFrame.Hour,
                "1d": TimeFrame.Day,
                "15m": TimeFrame.FifteenMinute,
            }
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf_map.get(timeframe, TimeFrame.Hour),
                limit=limit,
            )
            bars = self.data_client.get_stock_bars(request)
            df = bars.df
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(symbol, level=0)
            return df[["open", "high", "low", "close", "volume"]]
        except Exception as e:
            logger.error(f"Alpaca historical data error: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> float:
        try:
            latest = self.data_client.get_stock_latest_trade(symbol)
            return float(latest[symbol].price) if latest else 0.0
        except Exception:
            return 0.0

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        **kwargs,
    ):
        try:
            order_data = MarketOrderRequest(
                symbol=symbol, qty=quantity, side=side.lower(), time_in_force="day"
            )
            order = self.trading_client.submit_order(order_data=order_data)
            logger.info(f"✅ Alpaca Order: {side} {quantity} {symbol}")
            return {"status": order.status, "orderId": order.id}
        except Exception as e:
            logger.error(f"Alpaca order error: {e}")
            return {"status": "error"}

    def get_positions(self):
        positions = self.trading_client.get_all_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_cost": float(p.avg_entry_price),
            }
            for p in positions
        ]

    def get_portfolio_value(self) -> float:
        account = self.trading_client.get_account()
        return float(account.equity)

    def get_account_info(self) -> dict:
        return {"broker": "Alpaca", "connected": True}

    def disconnect(self):
        pass
