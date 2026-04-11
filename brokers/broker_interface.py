# brokers/broker_interface.py
from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd

class BrokerInterface(ABC):
    """Abstrakcyjny interfejs dla wszystkich brokerów"""

    @abstractmethod
    def connect(self) -> bool:
        """Nawiązanie połączenia z brokerem"""
        pass

    @abstractmethod
    def get_account_info(self) -> Dict:
        """Zwraca informacje o koncie"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """Zwraca listę otwartych pozycji"""
        pass

    @abstractmethod
    def get_portfolio_value(self) -> float:
        """Zwraca wartość portfela"""
        pass

    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Zwraca dane OHLCV (dla modeli LSTM)"""
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Zwraca bieżącą cenę"""
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "market", **kwargs) -> Dict:
        """Składa zlecenie"""
        pass

    @abstractmethod
    def disconnect(self):
        """Rozłączenie z brokerem"""
        pass
