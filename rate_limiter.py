"""
Token-bucket rate limiter for external API calls (Claude AI, NewsAPI, etc.).

Thread-safe implementation suitable for both synchronous and async use.

Usage
-----
    limiter = RateLimiter(calls_per_second=0.5)   # 1 call every 2 s

    # Block until allowed:
    limiter.acquire()
    response = requests.get(...)

    # Non-blocking check:
    if limiter.try_acquire():
        response = requests.get(...)

    # Context manager:
    with limiter:
        response = requests.get(...)

    # Decorator:
    @limiter.limit
    def fetch_signal(symbol):
        ...
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from typing import Callable, TypeVar

logger = logging.getLogger("RateLimiter")

F = TypeVar("F", bound=Callable)


class RateLimiter:
    """Thread-safe token bucket rate limiter.

    Args:
        calls_per_second: Maximum number of calls allowed per second.
                          E.g. 0.5 → 1 call every 2 seconds.
        burst: Maximum burst size (tokens stored when idle). Defaults to 1.
    """

    def __init__(self, calls_per_second: float = 1.0, burst: int = 1) -> None:
        if calls_per_second <= 0:
            raise ValueError("calls_per_second must be positive")
        if burst < 1:
            raise ValueError("burst must be at least 1")

        self._rate = calls_per_second
        self._burst = float(burst)
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    # ── core token bucket logic ───────────────────────────────────────────────

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time (must be called under lock)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def try_acquire(self) -> bool:
        """Consume one token without blocking. Returns True if acquired."""
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    def acquire(self, timeout: float | None = None) -> bool:
        """Block until a token is available, then consume it.

        Args:
            timeout: Maximum seconds to wait. None = wait forever.

        Returns:
            True if a token was acquired, False if timed out.
        """
        deadline = time.monotonic() + timeout if timeout is not None else None

        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
                # Calculate wait until next token
                wait = (1.0 - self._tokens) / self._rate

            # Respect deadline
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait = min(wait, remaining)

            logger.debug(f"Rate limited — sleeping {wait:.2f}s")
            time.sleep(wait)

    # ── convenience interfaces ────────────────────────────────────────────────

    def __enter__(self) -> "RateLimiter":
        self.acquire()
        return self

    def __exit__(self, *_) -> None:
        pass

    def limit(self, func: F) -> F:
        """Decorator that rate-limits calls to *func*."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens (informational)."""
        with self._lock:
            self._refill()
            return self._tokens


# ── Pre-configured limiters for common services ───────────────────────────────

def claude_limiter(calls_per_minute: int = 10) -> RateLimiter:
    """Rate limiter for Claude AI API (default: 10 req/min)."""
    return RateLimiter(calls_per_second=calls_per_minute / 60.0, burst=2)


def news_api_limiter(calls_per_hour: int = 100) -> RateLimiter:
    """Rate limiter for NewsAPI (default: 100 req/hr free tier)."""
    return RateLimiter(calls_per_second=calls_per_hour / 3600.0, burst=5)


def mt5_limiter(calls_per_second: float = 5.0) -> RateLimiter:
    """Rate limiter for MetaTrader5 data requests."""
    return RateLimiter(calls_per_second=calls_per_second, burst=10)
