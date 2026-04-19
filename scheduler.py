# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from daily_analysis import run_daily_analysis
from weekly_analysis import run_weekly_analysis
from monthly_dividend_report import run_monthly_dividend_report
from notifications import AlphaNotifier
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notifier = AlphaNotifier()


def wrapped_daily():
    logger.info("📅 Executing Daily Analysis")
    run_daily_analysis()


def wrapped_weekly():
    logger.info("📅 Executing Weekly Analysis")
    run_weekly_analysis()


def wrapped_monthly():
    logger.info("📅 Executing Monthly Dividend Report")
    run_monthly_dividend_report()


def start_scheduler():
    """Start APScheduler with daily/weekly/monthly jobs"""
    scheduler = BackgroundScheduler(timezone="Europe/Warsaw")

    # Daily 08:30
    scheduler.add_job(wrapped_daily, CronTrigger(hour=8, minute=30), id="daily")

    # Weekly Monday 09:00
    scheduler.add_job(
        wrapped_weekly, CronTrigger(day_of_week="mon", hour=9, minute=0), id="weekly"
    )

    # Monthly 1st day 10:00
    scheduler.add_job(
        wrapped_monthly, CronTrigger(day=1, hour=10, minute=0), id="monthly"
    )

    scheduler.start()

    logger.info("✅ Alpha AI Scheduler started")
    logger.info("   Daily  → 08:30 codziennie")
    logger.info("   Weekly → 09:00 w poniedziałki")
    logger.info("   Monthly→ 10:00 1. dnia miesiąca")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    start_scheduler()
