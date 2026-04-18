# notifications.py
import yaml
import requests
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class AlphaNotifier:
    def __init__(self):
        config_path = Path("config/notifications.yaml")
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {
                "telegram": {"enabled": False},
                "discord": {"enabled": False},
            }
            logger.warning("notifications.yaml not found")

    def send_report_notification(self, report_type: str, summary: str = ""):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
🚀 **Alpha AI Report**
**Typ:** {report_type}
**Czas:** {ts}
**Podsumowanie:** {summary}
        """.strip()

        # Telegram
        if self.config.get("telegram", {}).get("enabled"):
            try:
                token = self.config["telegram"]["bot_token"]
                chat_id = self.config["telegram"]["chat_id"]
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                requests.post(url, json={"chat_id": chat_id, "text": message})
                logger.info("✅ Telegram sent")
            except Exception as e:
                logger.error(f"Telegram error: {e}")

        # Discord
        if self.config.get("discord", {}).get("enabled"):
            try:
                webhook = self.config["discord"]["webhook_url"]
                requests.post(webhook, json={"content": message})
                logger.info("✅ Discord sent")
            except Exception as e:
                logger.error(f"Discord error: {e}")
