from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class CacheEnvelope(Generic[T]):
    value: T
    generated_at: datetime
    cache_age_seconds: int
    stale: bool


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = Lock()
        self._value: T | None = None
        self._generated_at: datetime | None = None

    def get_or_set(self, loader: Callable[[], T]) -> CacheEnvelope[T]:
        with self._lock:
            now = datetime.now(timezone.utc)
            if (
                self._value is not None
                and self._generated_at is not None
                and now - self._generated_at < self._ttl
            ):
                return CacheEnvelope(
                    value=self._value,
                    generated_at=self._generated_at,
                    cache_age_seconds=int((now - self._generated_at).total_seconds()),
                    stale=False,
                )

            value = loader()
            self._value = value
            self._generated_at = now
            return CacheEnvelope(
                value=value,
                generated_at=now,
                cache_age_seconds=0,
                stale=False,
            )

    def clear(self) -> None:
        with self._lock:
            self._value = None
            self._generated_at = None
