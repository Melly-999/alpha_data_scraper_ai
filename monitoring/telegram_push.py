from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

try:
    from telegram import Bot  # type: ignore
except Exception:  # pragma: no cover
    Bot = None


@dataclass
class TelegramAlertConfig:
    token: str
    chat_id: str
    min_confidence: float = 70.0
    send_equity_alerts: bool = True
    send_risk_alerts: bool = True


class TelegramAlertPublisher:
    def __init__(self, config: TelegramAlertConfig | None = None) -> None:
        if config is None:
            token = os.getenv("TELEGRAM_BOT_TOKEN", "")
            chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
            min_conf = float(os.getenv("TELEGRAM_MIN_CONFIDENCE", "70"))
            config = TelegramAlertConfig(
                token=token,
                chat_id=chat_id,
                min_confidence=min_conf,
            )
        self.config = config
        self._last_signal_key = ""
        self._last_equity_bucket: float | None = None
        self._last_risk_status = ""

    @property
    def enabled(self) -> bool:
        return bool(Bot and self.config.token and self.config.chat_id)

    async def _send(self, text: str) -> None:
        if not self.enabled:
            return
        bot = Bot(token=self.config.token)
        await bot.send_message(chat_id=self.config.chat_id, text=text)

    def _signal_message(self, signal_row: dict[str, Any]) -> str:
        return (
            "ALPHA AI SIGNAL\n"
            f"Symbol: {signal_row.get('symbol')}\n"
            f"Signal: {signal_row.get('signal')}\n"
            f"Confidence: {signal_row.get('confidence')}%\n"
            f"Score: {signal_row.get('score')}\n"
            f"Close: {signal_row.get('last_close')}\n"
        )

    def _equity_message(self, stats_row: dict[str, Any], bucket: float) -> str:
        return (
            "ALPHA AI EQUITY ALERT\n"
            f"Equity: {stats_row.get('equity')}\n"
            f"Profit: {stats_row.get('profit')}\n"
            f"Drawdown %: {stats_row.get('drawdown_pct')}\n"
            f"Bucket: {bucket}\n"
        )

    def _risk_message(self, risk_row: dict[str, Any]) -> str:
        return (
            "ALPHA AI RISK EVENT\n"
            f"Status: {risk_row.get('status')}\n"
            f"Reason: {risk_row.get('reason')}\n"
            f"Symbol: {risk_row.get('symbol')}\n"
            f"Signal: {risk_row.get('signal')}\n"
            f"Confidence: {risk_row.get('confidence')}\n"
        )

    async def publish_dashboard_event(self, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return

        signals = payload.get("signals", []) or []
        stats = payload.get("stats", {}) or {}
        risk_events = payload.get("risk_events", []) or []

        if signals:
            top = signals[0]
            signal = str(top.get("signal", "HOLD")).upper()
            confidence = float(top.get("confidence", 0.0) or 0.0)
            signal_key = f"{top.get('symbol')}|{signal}|{top.get('created_at')}"
            if signal in {"BUY", "SELL"} and confidence >= self.config.min_confidence:
                if signal_key != self._last_signal_key:
                    self._last_signal_key = signal_key
                    await self._send(self._signal_message(top))

        if self.config.send_equity_alerts and stats:
            equity = float(stats.get("equity", 0.0) or 0.0)
            bucket = round(equity / 100.0) * 100.0 if equity else 0.0
            if self._last_equity_bucket is None:
                self._last_equity_bucket = bucket
            elif bucket != self._last_equity_bucket:
                self._last_equity_bucket = bucket
                await self._send(self._equity_message(stats, bucket))

        if self.config.send_risk_alerts and risk_events:
            latest = risk_events[0]
            status = str(latest.get("status", ""))
            if status and status != self._last_risk_status:
                self._last_risk_status = status
                await self._send(self._risk_message(latest))

    def publish_dashboard_event_sync(self, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        try:
            asyncio.run(self.publish_dashboard_event(payload))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.create_task(self.publish_dashboard_event(payload))
