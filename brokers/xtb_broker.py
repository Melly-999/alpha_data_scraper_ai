# brokers/xtb_broker.py
import pandas as pd
import yfinance as yf
import os
from typing import Dict, List, Union
from datetime import datetime
from .broker_interface import BrokerInterface
import logging

logger = logging.getLogger(__name__)

class XTBBroker(BrokerInterface):
    """Broker XTB - tylko odczyt (XLSX + yfinance)"""

    def __init__(self, 
                 closed_positions_xlsx_paths: Union[str, list] = None, 
                 cash_operations_xlsx_paths: Union[str, list] = None,
                 default_currency: str = "PLN"):
        self.closed_positions_paths = [closed_positions_xlsx_paths] if isinstance(closed_positions_xlsx_paths, str) else (closed_positions_xlsx_paths or [])
        self.cash_operations_paths = [cash_operations_xlsx_paths] if isinstance(cash_operations_xlsx_paths, str) else (cash_operations_xlsx_paths or [])
        self.default_currency = default_currency
        self._positions_cache = None
        self._cash_cache = None

    def connect(self) -> bool:
        logger.info("✅ XTBBroker connected (XLSX + yfinance)")
        return True

    def _normalize_ticker(self, symbol: str) -> str:
        """Konwertuje tickery na format yfinance"""
        s = str(symbol).upper().strip()
        if s.endswith('.US'): return s.replace('.US', '')
        if s.endswith('.PL'): return s.replace('.PL', '.WA')
        if s.endswith('.UK'): return s.replace('.UK', '.L')
        if s.endswith('.DE'): return s.replace('.DE', '.DE')
        return s

    def _load_closed_positions(self) -> List[Dict]:
        """Wczytuje zamknięte pozycje z XLSX"""
        if self._positions_cache is not None:
            return self._positions_cache

        all_positions = []
        for path in self.closed_positions_paths:
            if not path or not os.path.exists(path):
                logger.warning(f"Plik nie istnieje: {path}")
                continue
            try:
                df = pd.read_excel(path, sheet_name="Closed Positions", skiprows=4)
                df = df.dropna(how='all').reset_index(drop=True)

                for _, row in df.iterrows():
                    ticker = str(row.get('Ticker', '')).strip()
                    if not ticker or ticker.lower() in ['nan', '']:
                        continue
                    
                    volume = float(row.get('Volume', 0) or 0)
                    if abs(volume) < 0.0001:
                        continue

                    all_positions.append({
                        "symbol": ticker,
                        "qty": volume,
                        "avg_cost": float(row.get('Open Price', 0) or 0),
                        "category": str(row.get('Category', 'UNKNOWN')),
                        "profit_loss": float(row.get('Profit/Loss', 0) or 0),
                        "close_time": str(row.get('Close Time (UTC)', '')),
                    })
                logger.info(f"✅ Wczytano {len(all_positions)} pozycji z {os.path.basename(path)}")
            except Exception as e:
                logger.error(f"Błąd parsowania {path}: {e}")

        self._positions_cache = all_positions
        return all_positions

    def _load_cash_operations(self) -> List[Dict]:
        """Wczytuje operacje gotówkowe (dywidendy, podatki, depozyty)"""
        if self._cash_cache is not None:
            return self._cash_cache

        all_cash = []
        for path in self.cash_operations_paths:
            if not path or not os.path.exists(path):
                continue
            try:
                df = pd.read_excel(path, sheet_name="Cash Operations", skiprows=4)
                df = df.dropna(how='all').reset_index(drop=True)

                for _, row in df.iterrows():
                    all_cash.append({
                        "type": str(row.get('Type', '')).strip(),
                        "ticker": str(row.get('Ticker', '')).strip(),
                        "time": str(row.get('Time', '')),
                        "amount": float(row.get('Amount', 0) or 0),
                        "comment": str(row.get('Comment', '')),
                    })
                logger.info(f"✅ Wczytano {len(all_cash)} operacji gotówkowych")
            except Exception as e:
                logger.error(f"Błąd Cash Operations {path}: {e}")

        self._cash_cache = all_cash
        return all_cash

    def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Pobiera dane przez yfinance"""
        ticker = self._normalize_ticker(symbol)
        try:
            interval_map = {"1h": "1h", "1d": "1d", "15m": "15m"}
            interval = interval_map.get(timeframe, "1h")
            
            data = yf.download(ticker, period=f"{limit + 50}d", interval=interval, progress=False, auto_adjust=True)
            if data.empty:
                logger.warning(f"Brak danych yfinance dla {ticker}")
                return pd.DataFrame()
            
            df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.index.name = 'timestamp'
            df.columns = df.columns.str.lower()
            return df.tail(limit)
        except Exception as e:
            logger.error(f"yfinance error dla {ticker}: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> float:
        """Pobiera bieżącą cenę"""
        ticker = self._normalize_ticker(symbol)
        try:
            data = yf.download(ticker, period="5d", progress=False)
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except:
            pass
        return 0.0

    def get_positions(self) -> List[Dict]:
        return self._load_closed_positions()

    def get_cash_summary(self) -> Dict:
        """Szczegółowa analiza cash flow"""
        cash = self._load_cash_operations()
        if not cash:
            return {"status": "no_data"}

        df = pd.DataFrame(cash)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        summary = {
            "total_transactions": len(df),
            "net_cash_flow": float(df['amount'].sum()),
            "total_dividends_gross": float(df[df['type'].str.contains('Dividend', case=False, na=False)]['amount'].sum()),
            "withholding_tax": float(df[df['type'].str.contains('Withholding tax|tax', case=False, na=False)]['amount'].sum()),
            "net_dividends": 0.0,
            "deposits": float(df[df['type'].str.contains('Deposit|IKE deposit|Transfer in', case=False, na=False)]['amount'].sum()),
            "withdrawals": float(df[df['type'].str.contains('Withdrawal', case=False, na=False)]['amount'].sum()),
            "top_dividend_stocks": df[df['type'].str.contains('Dividend', case=False, na=False)].groupby('ticker')['amount'].sum().nlargest(8).to_dict(),
        }
        summary["net_dividends"] = summary["total_dividends_gross"] + summary["withholding_tax"]
        return summary

    def get_dividend_analysis(self) -> Dict:
        """Analiza dywidend"""
        summary = self.get_cash_summary()
        return {
            "total_gross_dividends": summary.get("total_dividends_gross", 0),
            "withholding_tax": summary.get("withholding_tax", 0),
            "net_dividends": summary.get("net_dividends", 0),
            "top_dividend_stocks": summary.get("top_dividend_stocks", {}),
        }

    def get_portfolio_value(self) -> float:
        """Przybliżona wartość portfela"""
        positions = self.get_positions()
        total = 0.0
        for p in positions:
            price = self.get_current_price(p["symbol"])
            total += p["qty"] * (price if price > 0 else p.get("avg_cost", 0))
        return round(total, 2)

    def get_account_info(self) -> Dict:
        return {
            "broker": "XTB",
            "currency": self.default_currency,
            "equity": self.get_portfolio_value(),
            "mode": "read-only (XLSX + yfinance)"
        }

    def place_order(self, *args, **kwargs):
        logger.warning("❌ XTB broker jest read-only – nie można składać zleceń")
        return {"status": "rejected", "reason": "read-only"}

    def disconnect(self):
        pass
