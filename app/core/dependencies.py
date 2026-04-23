from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyStatus:
    mt5_available: bool
    claude_available: bool
    news_available: bool
    fallback_mode: bool


def probe_dependencies() -> DependencyStatus:
    try:
        import MetaTrader5  # type: ignore  # noqa: F401

        mt5_available = True
    except Exception:
        mt5_available = False

    claude_available = bool(os.getenv("CLAUDE_API_KEY"))
    news_available = bool(os.getenv("NEWSAPI_KEY"))
    fallback_mode = not (mt5_available and claude_available and news_available)
    return DependencyStatus(
        mt5_available=mt5_available,
        claude_available=claude_available,
        news_available=news_available,
        fallback_mode=fallback_mode,
    )
