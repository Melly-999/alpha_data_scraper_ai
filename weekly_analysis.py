# weekly_analysis.py
from ai_engine import AlphaAIEngine
from brokers.broker_factory import get_broker
from notifications import AlphaNotifier
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_weekly_analysis():
    logger.info("🚀 Weekly Analysis started")
    engine = AlphaAIEngine()
    broker = get_broker()
    notifier = AlphaNotifier()

    result = engine.analyze_and_decide()

    # Get cash data
    try:
        cash = broker.get_cash_summary()
        dividend_info = broker.get_dividend_analysis()
    except:
        cash = {"net_cash_flow": 0}
        dividend_info = {}

    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = f"reports/weekly_{ts}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Alpha AI Weekly Report – {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"**Portfolio Value:** {result.get('portfolio_value', 0):.2f} PLN\n")
        f.write(f"**Net Cash Flow:** {cash.get('net_cash_flow', 0):.2f} PLN\n\n")

        if dividend_info:
            f.write("## Dywidendy (ostatni miesiąc)\n")
            f.write(
                f"- Brutto: {dividend_info.get('total_gross_dividends', 0):.2f} PLN\n"
            )
            f.write(f"- Podatek: {dividend_info.get('withholding_tax', 0):.2f} PLN\n")
            f.write(f"- Netto: {dividend_info.get('net_dividends', 0):.2f} PLN\n\n")

        f.write("## Bridgewater Risk Assessment\n")
        f.write(result.get("risk_report_summary", "Report ready"))

    logger.info(f"✅ Report saved: {path}")
    notifier.send_report_notification(
        "Weekly Report", f"Cash flow: {cash.get('net_cash_flow', 0):.2f} PLN"
    )
    engine.shutdown()


if __name__ == "__main__":
    run_weekly_analysis()
