"""
Prometheus metrics exporter for the trading bot.

Exposes /metrics on port 8080 using the prometheus_client library.
Run alongside the main bot or embed via start_metrics_server().

Metrics exposed:
  trading_bot_signals_total          — counter, labels: symbol, signal
  trading_bot_signal_confidence      — gauge,   labels: symbol
  trading_bot_errors_total           — counter, labels: module
  trading_bot_analysis_duration_seconds — gauge, labels: symbol
  trading_bot_claude_duration_seconds   — gauge
  trading_bot_news_sentiment_score      — gauge, labels: symbol
  trading_bot_active_positions          — gauge
  trading_bot_info                      — info,  labels: version, environment
"""

from __future__ import annotations

import logging
import os
import threading
import time
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger("MetricsServer")

# ──────────────────────────────────────────────────────────────────────────────
# Lazy import so the module works even when prometheus_client is absent
# (tests can mock it; prod must have it installed)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Info,
        start_http_server,
    )

    _PROMETHEUS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PROMETHEUS_AVAILABLE = False
    logger.warning(
        "prometheus_client not installed. Metrics endpoint disabled. "
        "Run: pip install prometheus-client"
    )


class TradingBotMetrics:
    """Container for all Prometheus metrics used by the trading bot."""

    def __init__(self, registry: "CollectorRegistry | None" = None) -> None:
        if not _PROMETHEUS_AVAILABLE:
            self._enabled = False
            return

        self._enabled = True
        reg = registry  # None → default global registry

        self.signals_total = Counter(
            "trading_bot_signals_total",
            "Total number of trading signals generated",
            ["symbol", "signal"],
            registry=reg,
        )
        self.signal_confidence = Gauge(
            "trading_bot_signal_confidence",
            "Last signal confidence score (0-100)",
            ["symbol"],
            registry=reg,
        )
        self.errors_total = Counter(
            "trading_bot_errors_total",
            "Total number of errors by module",
            ["module"],
            registry=reg,
        )
        self.analysis_duration = Gauge(
            "trading_bot_analysis_duration_seconds",
            "Duration of the last full analysis cycle per symbol",
            ["symbol"],
            registry=reg,
        )
        self.claude_duration = Gauge(
            "trading_bot_claude_duration_seconds",
            "Duration of the last Claude AI API call",
            registry=reg,
        )
        self.news_sentiment = Gauge(
            "trading_bot_news_sentiment_score",
            "Latest news sentiment score for symbol (-1 to 1)",
            ["symbol"],
            registry=reg,
        )
        self.active_positions = Gauge(
            "trading_bot_active_positions",
            "Number of currently open positions",
            registry=reg,
        )
        self.bot_info = Info(
            "trading_bot",
            "Trading bot version and environment information",
            registry=reg,
        )
        self.bot_info.info(
            {
                "version": os.getenv("BOT_VERSION", "dev"),
                "environment": os.getenv("ENVIRONMENT", "local"),
            }
        )

    # ── convenience helpers ───────────────────────────────────────────────────

    def record_signal(self, symbol: str, signal: str, confidence: float) -> None:
        """Record a generated trading signal."""
        if not self._enabled:
            return
        self.signals_total.labels(symbol=symbol, signal=signal).inc()
        self.signal_confidence.labels(symbol=symbol).set(confidence)

    def record_error(self, module: str) -> None:
        """Increment the error counter for a module."""
        if not self._enabled:
            return
        self.errors_total.labels(module=module).inc()

    def record_analysis_duration(self, symbol: str, seconds: float) -> None:
        if not self._enabled:
            return
        self.analysis_duration.labels(symbol=symbol).set(seconds)

    def record_claude_duration(self, seconds: float) -> None:
        if not self._enabled:
            return
        self.claude_duration.set(seconds)

    def record_sentiment(self, symbol: str, score: float) -> None:
        if not self._enabled:
            return
        self.news_sentiment.labels(symbol=symbol).set(score)

    def set_active_positions(self, count: int) -> None:
        if not self._enabled:
            return
        self.active_positions.set(count)

    @contextmanager
    def time_analysis(self, symbol: str) -> Generator[None, None, None]:
        """Context manager that records analysis wall time."""
        start = time.monotonic()
        try:
            yield
        finally:
            self.record_analysis_duration(symbol, time.monotonic() - start)

    @contextmanager
    def time_claude(self) -> Generator[None, None, None]:
        """Context manager that records Claude API wall time."""
        start = time.monotonic()
        try:
            yield
        finally:
            self.record_claude_duration(time.monotonic() - start)


# ── module-level singleton ────────────────────────────────────────────────────
_metrics: "TradingBotMetrics | None" = None
_server_started = False
_lock = threading.Lock()


def get_metrics() -> TradingBotMetrics:
    """Return the global TradingBotMetrics singleton, creating it if needed."""
    global _metrics
    if _metrics is None:
        with _lock:
            if _metrics is None:
                _metrics = TradingBotMetrics()
    return _metrics


def start_metrics_server(port: int = 8080) -> None:
    """Start the Prometheus HTTP server in a background daemon thread."""
    global _server_started
    if not _PROMETHEUS_AVAILABLE:
        logger.warning("prometheus_client unavailable — metrics server not started.")
        return
    with _lock:
        if _server_started:
            logger.debug("Metrics server already running.")
            return
        start_http_server(port)
        _server_started = True
        logger.info(f"Prometheus metrics server started on :{port}/metrics")


# ── CLI entry point for standalone testing ────────────────────────────────────
if __name__ == "__main__":
    import random

    logging.basicConfig(level=logging.INFO)
    start_metrics_server(8080)
    m = get_metrics()

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    signals = ["BUY", "SELL", "HOLD"]

    print(
        "Metrics server running on :8080/metrics — generating dummy data…  Ctrl-C to stop."
    )
    while True:
        for sym in symbols:
            sig = random.choice(signals)
            conf = random.uniform(40, 95)
            m.record_signal(sym, sig, conf)
            m.record_analysis_duration(sym, random.uniform(0.1, 1.5))
            m.record_sentiment(sym, random.uniform(-1, 1))
        m.record_claude_duration(random.uniform(0.5, 8.0))
        m.set_active_positions(random.randint(0, 5))
        time.sleep(5)
