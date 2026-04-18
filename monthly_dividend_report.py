# monthly_dividend_report.py
from ai_engine import AlphaAIEngine
from brokers.broker_factory import get_broker
from notifications import AlphaNotifier
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_monthly_dividend_report():
    logger.info("🚀 Monthly Dividend Report started")
    engine = AlphaAIEngine()
    broker = get_broker()
    notifier = AlphaNotifier()

    dividend_info = broker.get_dividend_analysis()
    cash = broker.get_cash_summary()
    positions = broker.get_positions()

    # Claude Harvard Dividend Strategy
    harvard_report = engine.claude.get_full_analysis(
        "harvard_dividend",
        dividend_details=f"""
        Dywidendy netto: {dividend_info.get('net_dividends', 0):.2f} PLN
        Top stocks: {list(dividend_info.get('top_dividend_stocks', {}).keys())[:5]}
        Portfel: {broker.get_portfolio_value():.2f} PLN
        """,
    )

    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d")
    path = f"reports/monthly_dividend_{ts}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Monthly Dividend Report – Harvard Strategy\n")
        f.write(f"**Data:** {ts}\n\n")

        f.write("## Dywidendy (ostatni miesiąc)\n")
        f.write(f"- Brutto: {dividend_info.get('total_gross_dividends', 0):.2f} PLN\n")
        f.write(f"- Podatek: {dividend_info.get('withholding_tax', 0):.2f} PLN\n")
        f.write(f"- **Netto: {dividend_info.get('net_dividends', 0):.2f} PLN**\n\n")

        f.write("## Top Dywidendy\n")
        for ticker, amount in list(
            dividend_info.get("top_dividend_stocks", {}).items()
        )[:8]:
            f.write(f"- **{ticker}**: {amount:.2f} PLN\n")

        f.write("\n## Harvard Endowment Strategy (Claude)\n")
        f.write(harvard_report)

    logger.info(f"✅ Report saved: {path}")
    notifier.send_report_notification(
        "Monthly Dividend", f"Netto: {dividend_info.get('net_dividends', 0):.2f} PLN"
    )
    engine.shutdown()


if __name__ == "__main__":
    run_monthly_dividend_report()
