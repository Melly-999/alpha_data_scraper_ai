from __future__ import annotations

from app.schemas.news import NewsItem

_FALLBACK_ITEMS: tuple[NewsItem, ...] = (
    NewsItem(
        id="news-fallback-1",
        headline="ECB holds rates — EUR supported near 1.0800 (safe fallback)",
        source="MellyTrade Safe Fallback",
        sentiment="neutral",
        impact="low",
        time="09:30",
    ),
    NewsItem(
        id="news-fallback-2",
        headline="Gold testing resistance near 2330; macro tone cautious (safe fallback)",
        source="MellyTrade Safe Fallback",
        sentiment="neutral",
        impact="low",
        time="08:45",
    ),
    NewsItem(
        id="news-fallback-3",
        headline="Yen weakness persists; BoJ holds accommodation (safe fallback)",
        source="MellyTrade Safe Fallback",
        sentiment="neutral",
        impact="low",
        time="07:50",
    ),
)


class NewsSentimentService:
    """Returns a static advisory-only news sentiment fallback.

    No external news API calls. No scraping. No broker connections.
    No network calls. No persistence writes. Read-only and deterministic.
    """

    def get_sentiment(self) -> list[NewsItem]:
        return list(_FALLBACK_ITEMS)
