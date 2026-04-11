# brokers/broker_factory.py
import yaml
import os
from .xtb_broker import XTBBroker
from .ibkr_broker import IBKRBroker
from .alpaca_broker import AlpacaBroker
import logging

logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Wczytuje config/brokers.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), "../config/brokers.yaml")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    logger.warning("brokers.yaml nie znaleziony!")
    return {"active_broker": "xtb"}

def get_broker():
    """Zwraca aktywnego brokera na podstawie config"""
    config = load_config()
    active = config.get("active_broker", "xtb").lower()

    if active == "xtb":
        cfg = config.get("xtb", {})
        return XTBBroker(
            closed_positions_xlsx_paths=cfg.get("closed_positions_xlsx_paths"),
            cash_operations_xlsx_paths=cfg.get("cash_operations_xlsx_paths"),
            default_currency=cfg.get("default_currency", "PLN")
        )

    elif active == "ibkr":
        cfg = config.get("ibkr", {})
        return IBKRBroker(
            host=cfg.get("host", "127.0.0.1"),
            port=cfg.get("port", 7497),
            client_id=cfg.get("client_id", 1),
            paper=cfg.get("paper", True)
        )

    elif active == "alpaca":
        cfg = config.get("alpaca", {})
        return AlpacaBroker(
            api_key=cfg.get("api_key", ""),
            secret_key=cfg.get("secret_key", ""),
            paper=cfg.get("paper", True)
        )

    else:
        logger.error(f"Nieznany broker: {active}")
        raise ValueError(f"Broker '{active}' nie istnieje")
