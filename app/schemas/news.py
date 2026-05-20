from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class NewsItem(BaseModel):
    """Read-only news sentiment item for the Terminal V1 dashboard.

    Matches the frontend terminalApi.ts NewsItem type exactly.
    All items are static advisory-only fallback data — no live news feed,
    no scraping, no external API calls, no trading recommendations.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    headline: str
    source: str
    sentiment: Literal["positive", "negative", "neutral"]
    impact: Literal["high", "medium", "low"]
    time: str
