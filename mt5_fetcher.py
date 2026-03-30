import logging
from datetime import datetime

import pandas as pd
try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

logger = logging.getLogger("GrokAlpha")


class MT5DataFetcher:
    """Handles MT5 connection and data fetching with incremental updates."""

    def __init__(self, symbol):
        self.symbol = symbol
        self.initialized = False
        self.last_bar_time = None

    def initialize(self):
        if mt5 is None:
            logger.error("MetaTrader5 package is not installed")
            return False
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        if not mt5.symbol_select(self.symbol, True):
            logger.warning("Symbol %s not available", self.symbol)
        self.initialized = True
        return True

    def shutdown(self):
        if self.initialized:
            mt5.shutdown()
            self.initialized = False

    def get_tick(self):
        """Return current bid/ask as tuple (bid, ask)."""
        if not self.initialized:
            return None
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return tick.bid, tick.ask

    def get_new_bars(self, max_bars=350):
        """
        Fetch new bars since last known bar.
        Returns (new_rates, full_df) or (None, None) if no new bars.
        """
        if not self.initialized:
            return None, None

        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, max_bars)
        if rates is None or len(rates) == 0:
            logger.warning("No rates fetched")
            return None, None

        current_bar_time = datetime.fromtimestamp(rates[-1][0])
        if self.last_bar_time == current_bar_time:
            return None, None

        self.last_bar_time = current_bar_time
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return rates, df

    def get_account_info(self):
        if not self.initialized:
            return None
        return mt5.account_info()
