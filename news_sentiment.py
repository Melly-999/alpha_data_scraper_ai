"""News sentiment analysis from ForexFactory and NewsAPI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
import logging

import requests  # type: ignore[import-untyped]
from bs4 import BeautifulSoup  # type: ignore[import-untyped]

logger = logging.getLogger("NewsSentiment")


@dataclass
class NewsItem:
    """Single news event."""

    source: str  # "ForexFactory" or "NewsAPI"
    title: str
    content: str
    sentiment: str  # "POSITIVE", "NEUTRAL", "NEGATIVE"
    impact: str  # "High", "Medium", "Low" (ForexFactory only)
    currency: str  # "USD", "EUR", etc.
    timestamp: datetime
    url: str


@dataclass
class SentimentScore:
    """Aggregated sentiment score."""

    currency: str
    positive_count: int
    neutral_count: int
    negative_count: int
    average_sentiment: float  # -1.0 to 1.0
    high_impact_count: int  # ForexFactory high impact only
    last_update: datetime


class ForexFactoryScraper:
    """Scrape ForexFactory economic calendar."""

    BASE_URL = "https://www.forexfactory.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    IMPACT_PRIORITY = {"High": 3, "Medium": 2, "Low": 1}

    @classmethod
    def fetch_calendar(cls, days_ahead: int = 7) -> Optional[List[NewsItem]]:
        """
        Fetch economic calendar from ForexFactory.

        Args:
            days_ahead: Number of days to look ahead.

        Returns:
            List of NewsItem objects, or None on error.
        """
        try:
            url = f"{cls.BASE_URL}/calendar.php"
            response = requests.get(url, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            events = []

            # Find calendar table rows (basic parsing)
            for row in soup.find_all("tr", class_="calendar__row"):
                try:
                    # Extract event name, impact, currency, forecast, etc.
                    currency = cls._extract_currency(row)
                    impact = cls._extract_impact(row)
                    title = cls._extract_title(row)
                    base_time = cls._extract_time(row)

                    if not currency or not title:
                        continue

                    # Skip if older than today
                    if base_time and base_time < datetime.now(timezone.utc):
                        continue

                    sentiment = cls._infer_sentiment_from_title(title)

                    events.append(
                        NewsItem(
                            source="ForexFactory",
                            title=title,
                            content=f"Impact: {impact}",
                            sentiment=sentiment,
                            impact=impact,
                            currency=currency,
                            timestamp=base_time or datetime.now(timezone.utc),
                            url=f"{cls.BASE_URL}/calendar.php",
                        )
                    )
                except Exception as e:
                    logger.debug(f"Error parsing calendar row: {e}")
                    continue

            logger.info(f"Fetched {len(events)} events from ForexFactory")
            return events

        except Exception as e:
            logger.error(f"ForexFactory fetch failed: {e}")
            return None

    @staticmethod
    def _extract_currency(row) -> Optional[str]:
        """Extract currency code from row."""
        try:
            curr_elem = row.find("td", class_="calendar__currency")
            if curr_elem:
                return curr_elem.text.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_impact(row) -> str:
        """Extract impact level: 'High', 'Medium', 'Low'."""
        try:
            impact_elem = row.find("td", class_="calendar__impact")
            if impact_elem:
                # Infer from icon color: red=High, orange=Medium, yellow=Low
                if "red" in str(impact_elem):
                    return "High"
                elif "orange" in str(impact_elem):
                    return "Medium"
                else:
                    return "Low"
        except Exception:
            pass
        return "Low"

    @staticmethod
    def _extract_title(row) -> Optional[str]:
        """Extract event title."""
        try:
            title_elem = row.find("td", class_="calendar__event")
            if title_elem:
                return title_elem.text.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_time(row) -> Optional[datetime]:
        """Extract event time as datetime."""
        try:
            time_elem = row.find("td", class_="calendar__time")
            if time_elem:
                time_str = time_elem.text.strip()
                # Parse "HH:MM" format (assume UTC)
                if time_str and ":" in time_str:
                    h, m = map(int, time_str.split(":"))
                    dt = datetime.now(timezone.utc).replace(hour=h, minute=m, second=0)
                    return dt
        except Exception:
            pass
        return None

    @staticmethod
    def _infer_sentiment_from_title(title: str) -> str:
        """Infer sentiment from event title."""
        positive_keywords = ["beat", "above", "strong", "growth", "gain"]
        negative_keywords = ["miss", "below", "weak", "fall", "decline", "loss"]

        title_lower = title.lower()

        pos_count = sum(1 for kw in positive_keywords if kw in title_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in title_lower)

        if pos_count > neg_count:
            return "POSITIVE"
        elif neg_count > pos_count:
            return "NEGATIVE"
        return "NEUTRAL"


class NewsAPIClient:
    """Fetch financial news from NewsAPI."""

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, api_key: str):
        """Initialize with NewsAPI key."""
        self.api_key = api_key

    def fetch_forex_news(
        self, currencies: Optional[List[str]] = None
    ) -> Optional[List[NewsItem]]:
        """
        Fetch news about forex currencies.

        Args:
            currencies: List of currency codes (e.g., ["USD", "EUR", "GBP"]).

        Returns:
            List of NewsItem objects, or None on error.
        """
        if not currencies:
            currencies = ["USD", "EUR", "GBP", "JPY"]

        try:
            all_news = []
            for currency in currencies:
                query = f"{currency} forex OR trading OR economy"
                params = {
                    "q": query,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": self.api_key,
                    "pageSize": 20,
                }

                response = requests.get(self.BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "error":
                    logger.warning(f"NewsAPI error: {data.get('message')}")
                    continue

                for article in data.get("articles", []):
                    pub_date = datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )
                    # Skip older than 24h
                    if (datetime.now(timezone.utc) - pub_date) > timedelta(days=1):
                        continue

                    sentiment = self._analyze_sentiment_newsapi(
                        article.get("title", "") + " " + article.get("description", "")
                    )

                    all_news.append(
                        NewsItem(
                            source="NewsAPI",
                            title=article.get("title", ""),
                            content=article.get("description", ""),
                            sentiment=sentiment,
                            impact="N/A",
                            currency=currency,
                            timestamp=pub_date,
                            url=article.get("url", ""),
                        )
                    )

            logger.info(f"Fetched {len(all_news)} news items from NewsAPI")
            return all_news

        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}")
            return None

    @staticmethod
    def _analyze_sentiment_newsapi(text: str) -> str:
        """Simple sentiment analysis using keyword matching."""
        positive_keywords = [
            "growth",
            "gain",
            "strong",
            "beat",
            "above",
            "rally",
            "surge",
            "bull",
        ]
        negative_keywords = [
            "fall",
            "decline",
            "weakness",
            "miss",
            "below",
            "crash",
            "bear",
            "drop",
        ]

        text_lower = text.lower()

        pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if pos_count > neg_count:
            return "POSITIVE"
        elif neg_count > pos_count:
            return "NEGATIVE"
        return "NEUTRAL"


class SentimentAnalyzer:
    """Aggregate sentiment from multiple sources."""

    def __init__(self, newsapi_key: Optional[str] = None):
        """Initialize with optional NewsAPI key."""
        self.newsapi = NewsAPIClient(newsapi_key) if newsapi_key else None

    def analyze_sentiment(
        self, include_forexfactory: bool = True, include_newsapi: bool = True
    ) -> Dict[str, SentimentScore]:
        """
        Analyze sentiment for all tracked currencies.

        Returns:
            Dict keyed by currency, with SentimentScore values.
        """
        all_news = []

        if include_forexfactory:
            ff_news = ForexFactoryScraper.fetch_calendar()
            if ff_news:
                all_news.extend(ff_news)

        if include_newsapi and self.newsapi:
            api_news = self.newsapi.fetch_forex_news()
            if api_news:
                all_news.extend(api_news)

        # Aggregate by currency
        sentiment_map: Dict[str, SentimentScore] = {}
        for news in all_news:
            currency = news.currency
            if currency not in sentiment_map:
                sentiment_map[currency] = SentimentScore(
                    currency=currency,
                    positive_count=0,
                    neutral_count=0,
                    negative_count=0,
                    average_sentiment=0.0,
                    high_impact_count=0,
                    last_update=datetime.now(timezone.utc),
                )

            score = sentiment_map[currency]

            # Count by sentiment
            if news.sentiment == "POSITIVE":
                score.positive_count += 1
            elif news.sentiment == "NEGATIVE":
                score.negative_count += 1
            else:
                score.neutral_count += 1

            # High impact count (ForexFactory only)
            if news.impact == "High":
                score.high_impact_count += 1

        # Compute average sentiment (-1 to 1)
        for currency, score in sentiment_map.items():
            total = score.positive_count + score.neutral_count + score.negative_count
            if total > 0:
                score.average_sentiment = (
                    score.positive_count - score.negative_count
                ) / total
            score.last_update = datetime.now(timezone.utc)

        logger.info(f"Sentiment analysis complete for {len(sentiment_map)} currencies")
        return sentiment_map

    def get_currency_signal(
        self, currency: str, sentiment_score: SentimentScore
    ) -> str:
        """
        Generate trading signal from sentiment score.

        Returns:
            "BUY" (strong positive), "SELL" (strong negative), "HOLD" (neutral).
        """
        avg_sentiment = sentiment_score.average_sentiment

        # High impact events carry more weight
        if sentiment_score.high_impact_count > 0:
            if avg_sentiment > 0.5:
                return "BUY"
            elif avg_sentiment < -0.5:
                return "SELL"

        # Regular sentiment
        if avg_sentiment > 0.3:
            return "BUY"
        elif avg_sentiment < -0.3:
            return "SELL"
        return "HOLD"
