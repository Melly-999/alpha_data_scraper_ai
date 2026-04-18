# daily_analysis.py
from ai_engine import AlphaAIEngine
from brokers.broker_factory import get_broker
from notifications import AlphaNotifier
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_daily_analysis():
    logger.info("🚀 Daily Analysis started")
    engine = AlphaAIEngine()
    broker = get_broker()
    notifier = AlphaNotifier()

    # Analyze
    result = engine.analyze_and_decide()

    # Get cash data if available
    try:
        dividend_info = broker.get_dividend_analysis()
    except Exception as exc:
        logger.debug("Broker dividend/cash data unavailable: %s", exc)
        dividend_info = {}

    # Save report
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d")
    path = f"reports/daily_{ts}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Alpha AI Snapshot – {ts}\n\n")
        f.write(f"**Portfolio Value:** {result.get('portfolio_value', 0):.2f} PLN\n")
        f.write(f"**Positions:** {result.get('positions_count', 0)}\n")
        if dividend_info:
            f.write(
                f"**Dywidendy netto:** {dividend_info.get('net_dividends', 0):.2f} PLN\n"
            )
        f.write("\n## Risk Analysis\n")
        f.write(result.get("risk_report_summary", "Report ready"))

    logger.info(f"✅ Report saved: {path}")
    notifier.send_report_notification(
        "Daily Analysis", f"Value: {result.get('portfolio_value', 0):.2f} PLN"
    )
    engine.shutdown()


if __name__ == "__main__":
    run_daily_analysis()
