from __future__ import annotations

from fastapi import APIRouter

from app.schemas.news import NewsItem
from app.services.news_sentiment import NewsSentimentService

router = APIRouter(tags=["news"])

_news_sentiment_service = NewsSentimentService()


@router.get("/news/sentiment", response_model=list[NewsItem])
def news_sentiment() -> list[NewsItem]:
    """Read-only news sentiment fallback for the Terminal V1 dashboard.

    Returns a static advisory-only list of news sentiment items. GET-only.
    Performs no mutation, no broker connection, no external API calls,
    no scraping, and no order placement. Items are informational context
    only — this endpoint does not trigger trade execution and does not
    constitute financial advice or trading recommendations.
    """
    return _news_sentiment_service.get_sentiment()
