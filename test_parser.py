# test_parser.py
from brokers.broker_factory import get_broker
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_parser():
    logger.info("🧪 Test parsera XTB")
    broker = get_broker()

    print("\n" + "=" * 60)
    print("TEST PARSERA XTB – CLOSED POSITIONS + CASH OPERATIONS")
    print("=" * 60)

    # Pozycje
    positions = broker.get_positions()
    print(f"\n✅ Wczytano {len(positions)} pozycji:")
    for p in positions[:12]:
        print(
            f"   {p['symbol']:12} | {p['qty']:8.4f} szt. | avg {p.get('avg_cost', 0):8.2f}"
        )

    # Cash Flow
    try:
        cash = broker.get_cash_summary()
        print("\n✅ Cash Operations:")
        print(f"   Transakcji: {cash.get('total_transactions', 0)}")
        print(f"   Net cash flow: {cash.get('net_cash_flow', 0):.2f} PLN")
        print(f"   Dywidendy brutto: {cash.get('total_dividends_gross', 0):.2f} PLN")
        print(f"   Podatek: {cash.get('withholding_tax', 0):.2f} PLN")
        print(f"   Dywidendy netto: {cash.get('net_dividends', 0):.2f} PLN")
    except Exception as e:
        print(f"❌ Cash operations error: {e}")

    # Dywidendy
    try:
        dividends = broker.get_dividend_analysis()
        print("\n✅ Top dywidendy:")
        for ticker, amount in list(dividends.get("top_dividend_stocks", {}).items())[
            :5
        ]:
            print(f"   {ticker:12}: {amount:8.2f} PLN")
    except Exception:
        pass

    # Wartość
    value = broker.get_portfolio_value()
    print(f"\n✅ Wartość portfela (yfinance): {value:.2f} PLN")

    print(f"\n✅ Test completed – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    test_parser()
