from monitoring.telegram_push import TelegramAlertPublisher
from monitoring.propfirm_stream import PropFirmRiskStream

publisher = TelegramAlertPublisher()
risk_stream = PropFirmRiskStream()


def handle_dashboard_payload(payload: dict):
    stats = payload.get("stats", {})
    risk_event = risk_stream.evaluate(stats)

    payload.setdefault("risk_events", []).insert(0, risk_event)

    publisher.publish_dashboard_event_sync(payload)


if __name__ == "__main__":
    print(
        "Telegram realtime stream ready. Connect this handler to /equity-stream consumer."
    )
