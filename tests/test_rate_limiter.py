"""Unit tests for rate_limiter.py."""

from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from rate_limiter import RateLimiter, claude_limiter, mt5_limiter, news_api_limiter


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------

def test_negative_rate_raises() -> None:
    with pytest.raises(ValueError, match="calls_per_second"):
        RateLimiter(calls_per_second=-1.0)


def test_zero_rate_raises() -> None:
    with pytest.raises(ValueError, match="calls_per_second"):
        RateLimiter(calls_per_second=0.0)


def test_burst_less_than_one_raises() -> None:
    with pytest.raises(ValueError, match="burst"):
        RateLimiter(calls_per_second=1.0, burst=0)


def test_valid_construction() -> None:
    rl = RateLimiter(calls_per_second=2.0, burst=3)
    assert rl.available_tokens == 3.0


# ---------------------------------------------------------------------------
# try_acquire
# ---------------------------------------------------------------------------

def test_try_acquire_succeeds_when_tokens_available() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=1)
    assert rl.try_acquire() is True


def test_try_acquire_fails_when_depleted() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=1)
    rl.try_acquire()  # consume the single token
    assert rl.try_acquire() is False


def test_try_acquire_drains_all_burst_tokens() -> None:
    burst = 3
    rl = RateLimiter(calls_per_second=1.0, burst=burst)
    results = [rl.try_acquire() for _ in range(burst + 1)]
    assert results[:burst] == [True] * burst
    assert results[burst] is False


def test_try_acquire_reduces_available_tokens() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=2)
    before = rl.available_tokens
    rl.try_acquire()
    assert rl.available_tokens < before


# ---------------------------------------------------------------------------
# acquire with timeout
# ---------------------------------------------------------------------------

def test_acquire_returns_true_when_token_available() -> None:
    rl = RateLimiter(calls_per_second=10.0, burst=1)
    assert rl.acquire(timeout=1.0) is True


def test_acquire_times_out_when_no_tokens() -> None:
    # Very slow refill: 0.01 tokens/sec → ~100s to refill from 0
    rl = RateLimiter(calls_per_second=0.01, burst=1)
    rl.try_acquire()  # drain the token

    with patch("time.sleep"):  # skip actual sleeping
        result = rl.acquire(timeout=0.001)

    assert result is False


def test_acquire_without_timeout_consumes_token() -> None:
    rl = RateLimiter(calls_per_second=100.0, burst=2)
    result = rl.acquire(timeout=1.0)
    assert result is True
    assert rl.available_tokens < 2.0


# ---------------------------------------------------------------------------
# available_tokens property
# ---------------------------------------------------------------------------

def test_available_tokens_equals_burst_on_construction() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=5)
    assert rl.available_tokens == 5.0


def test_available_tokens_decreases_after_acquisition() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=2)
    rl.try_acquire()
    assert rl.available_tokens < 2.0


def test_available_tokens_does_not_exceed_burst() -> None:
    rl = RateLimiter(calls_per_second=100.0, burst=2)
    time.sleep(0.1)  # let refill happen — should not exceed burst
    assert rl.available_tokens <= 2.0


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

def test_context_manager_acquires_and_exits() -> None:
    rl = RateLimiter(calls_per_second=100.0, burst=1)
    with rl:
        pass  # should not raise
    # After use, one token consumed
    assert rl.available_tokens < 1.0


def test_context_manager_returns_self() -> None:
    rl = RateLimiter(calls_per_second=100.0, burst=1)
    with rl as ctx:
        assert ctx is rl


# ---------------------------------------------------------------------------
# limit decorator
# ---------------------------------------------------------------------------

def test_limit_decorator_calls_function() -> None:
    rl = RateLimiter(calls_per_second=100.0, burst=1)
    call_log: list[int] = []

    @rl.limit
    def my_func(x: int) -> int:
        call_log.append(x)
        return x * 2

    result = my_func(5)
    assert result == 10
    assert call_log == [5]


def test_limit_decorator_preserves_function_name() -> None:
    rl = RateLimiter(calls_per_second=1.0, burst=1)

    @rl.limit
    def some_function():
        pass

    assert some_function.__name__ == "some_function"


def test_limit_decorator_blocks_when_no_tokens() -> None:
    """Decorator must consume a token — second call should wait or time out."""
    rl = RateLimiter(calls_per_second=100.0, burst=1)
    counter = {"n": 0}

    @rl.limit
    def inc():
        counter["n"] += 1

    inc()  # consumes the token
    # Token consumed; patch sleep to avoid real delay
    with patch("time.sleep"):
        inc()  # will refill quickly due to high rate in patched env
    assert counter["n"] == 2


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

def test_concurrent_try_acquire_does_not_exceed_burst() -> None:
    burst = 5
    rl = RateLimiter(calls_per_second=0.001, burst=burst)  # very slow refill
    successes: list[bool] = []
    lock = threading.Lock()

    def worker():
        result = rl.try_acquire()
        with lock:
            successes.append(result)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sum(successes) <= burst


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def test_claude_limiter_returns_rate_limiter() -> None:
    rl = claude_limiter()
    assert isinstance(rl, RateLimiter)


def test_claude_limiter_custom_calls_per_minute() -> None:
    rl = claude_limiter(calls_per_minute=60)
    # 60 calls/min = 1 call/sec
    assert abs(rl._rate - 1.0) < 1e-9


def test_news_api_limiter_returns_rate_limiter() -> None:
    rl = news_api_limiter()
    assert isinstance(rl, RateLimiter)


def test_news_api_limiter_custom_rate() -> None:
    rl = news_api_limiter(calls_per_hour=3600)
    # 3600 calls/hr = 1 call/sec
    assert abs(rl._rate - 1.0) < 1e-9


def test_mt5_limiter_returns_rate_limiter() -> None:
    rl = mt5_limiter()
    assert isinstance(rl, RateLimiter)


def test_mt5_limiter_custom_rate() -> None:
    rl = mt5_limiter(calls_per_second=10.0)
    assert abs(rl._rate - 10.0) < 1e-9


# ---------------------------------------------------------------------------
# Token refill logic
# ---------------------------------------------------------------------------

def test_tokens_refill_over_time() -> None:
    # Start with a fully-drained limiter then check that tokens grow
    rl = RateLimiter(calls_per_second=100.0, burst=1)
    rl.try_acquire()  # drain
    assert rl.available_tokens < 1.0

    time.sleep(0.05)  # 100 tokens/s * 0.05s = 5 theoretical tokens, capped at burst=1
    assert rl.available_tokens > 0.0
