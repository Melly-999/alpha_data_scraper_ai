"""Trading system entry point."""

from core.config import DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME
from core.logger import get_logger, setup_logging
from data.fetch import fetch_ohlc
from risk.risk_manager import RiskManager
from strategy.signals import generate_signal


def main() -> None:
    setup_logging()
    log = get_logger("main")
    print("Trading system started")

    symbol = DEFAULT_SYMBOLS[0]
    df = fetch_ohlc(symbol, DEFAULT_TIMEFRAME)
    log.info("Loaded %s rows for %s %s", len(df), symbol, DEFAULT_TIMEFRAME)

    result = generate_signal(df)
    risk_manager = RiskManager()
    risk = risk_manager.evaluate(result["signal"], int(result["confidence"]))

    if not risk["allowed"]:
        print("TRADE BLOCKED")

    lot_size = float(risk["lot_size"]) if risk["allowed"] else 0.0

    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Lot size: {lot_size}")
    print(f"Risk status: {risk['status']}")


if __name__ == "__main__":
    main()
