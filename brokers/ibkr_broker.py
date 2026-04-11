# brokers/ibkr_broker.py
from ib_insync import *
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class IBKRBroker:
    """Interactive Brokers - pełne API do tradingu"""

    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1, paper: bool = True):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.paper = paper
        self.ib = IB()
        self.connected = False

    def connect(self) -> bool:
        try:
            if not self.ib.isConnected():
                self.ib.connect(self.host, self.port, clientId=self.client_id)
                self.connected = True
                logger.info(f"✅ IBKR {'PAPER' if self.paper else 'LIVE'} connected")
            return True
        except Exception as e:
            logger.error(f"IBKR connect error: {e}")
            return False

    def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=f"{limit * 2} D",
                barSizeSetting=timeframe,
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            df = util.df(bars)[['date', 'open', 'high', 'low', 'close', 'volume']]
            df.columns = df.columns.str.lower()
            df.set_index('date', inplace=True)
            return df.tail(limit)
        except Exception as e:
            logger.error(f"IBKR historical data error: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> float:
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            ticker = self.ib.reqMktData(contract, snapshot=True)
            self.ib.sleep(1)
            return ticker.marketPrice() or 0.0
        except:
            return 0.0

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "market", **kwargs):
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            order = MarketOrder(side, quantity) if order_type == "market" else LimitOrder(side, quantity, kwargs.get("limit_price", 0))
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(0.5)
            logger.info(f"✅ IBKR Order: {side} {quantity} {symbol}")
            return {"status": trade.orderStatus.status, "orderId": trade.order.orderId}
        except Exception as e:
            logger.error(f"Order error: {e}")
            return {"status": "error"}

    def get_positions(self):
        return [{"symbol": p.contract.symbol, "qty": p.position, "avg_cost": p.averageCost} 
                for p in self.ib.positions()]

    def get_portfolio_value(self) -> float:
        summary = self.ib.accountSummary()
        for item in summary:
            if item.tag == "NetLiquidation":
                return float(item.value)
        return 0.0

    def get_account_info(self) -> dict:
        return {"broker": "IBKR", "connected": self.connected}

    def disconnect(self):
        if self.connected:
            self.ib.disconnect()
            self.connected = False
