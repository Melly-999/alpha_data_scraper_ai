from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.schemas.analytics import AnalyticsMetric, AnalyticsSummary
from app.services.cache import TTLCache


class AnalyticsService:
    def __init__(self, *, default_symbol: str) -> None:
        self._default_symbol = default_symbol
        self._cache: TTLCache[AnalyticsSummary] = TTLCache(ttl_seconds=30)

    def get_summary(self) -> AnalyticsSummary:
        envelope = self._cache.get_or_set(self._build_summary)
        return envelope.value.model_copy(
            update={"cache_age_seconds": envelope.cache_age_seconds}
        )

    def clear_cache(self) -> None:
        self._cache.clear()

    def _build_summary(self) -> AnalyticsSummary:
        try:
            from backtest import BacktestEngine
            from indicators import add_indicators
            from mt5_fetcher import MT5Fetcher
            from signal_generator import generate_signal

            fetcher = MT5Fetcher(symbol=self._default_symbol, timeframe="M5", seed=11)
            df = fetcher.get_latest_rates(bars=360)

            def signal_func(window):
                enriched = add_indicators(window)
                latest = enriched.iloc[-1]
                prev_close = float(enriched.iloc[-2]["close"])
                current_close = float(latest["close"])
                lstm_delta = current_close - prev_close
                result = generate_signal(latest, lstm_delta)
                return result.signal, result.confidence

            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=14)
            engine = BacktestEngine(
                symbol=self._default_symbol,
                initial_balance=10000.0,
                risk_per_trade=0.01,
            )
            metrics = engine.backtest(
                signal_func=signal_func,
                start_date=start_date,
                end_date=end_date,
                lookback_bars=min(80, max(len(df) // 3, 40)),
            )
            if metrics is None:
                raise RuntimeError("Backtest engine returned no metrics")

            return AnalyticsSummary(
                symbol=self._default_symbol,
                timeframe="M5",
                total_trades=metrics.total_trades,
                win_rate=round(metrics.win_rate * 100, 2),
                sharpe_ratio=round(metrics.sharpe_ratio, 2),
                max_drawdown=round(metrics.max_drawdown, 2),
                profit_factor=round(metrics.profit_factor, 2),
                total_return=round(metrics.total_return, 2),
                source="backtest_engine",
                fallback=False,
                generated_at=datetime.now(timezone.utc),
                cache_age_seconds=0,
                highlights=[
                    AnalyticsMetric(
                        label="Win Rate",
                        value=round(metrics.win_rate * 100, 2),
                        formatted=f"{metrics.win_rate * 100:.2f}%",
                    ),
                    AnalyticsMetric(
                        label="Sharpe",
                        value=round(metrics.sharpe_ratio, 2),
                        formatted=f"{metrics.sharpe_ratio:.2f}",
                    ),
                    AnalyticsMetric(
                        label="Max DD",
                        value=round(metrics.max_drawdown, 2),
                        formatted=f"{metrics.max_drawdown:.2f}%",
                    ),
                    AnalyticsMetric(
                        label="Profit Factor",
                        value=round(metrics.profit_factor, 2),
                        formatted=f"{metrics.profit_factor:.2f}x",
                    ),
                ],
            )
        except Exception:
            return AnalyticsSummary(
                symbol=self._default_symbol,
                timeframe="M5",
                total_trades=18,
                win_rate=61.11,
                sharpe_ratio=1.24,
                max_drawdown=3.42,
                profit_factor=1.68,
                total_return=4.93,
                source="fallback_analytics",
                fallback=True,
                generated_at=datetime.now(timezone.utc),
                cache_age_seconds=0,
                highlights=[
                    AnalyticsMetric(
                        label="Win Rate",
                        value=61.11,
                        formatted="61.11%",
                    ),
                    AnalyticsMetric(label="Sharpe", value=1.24, formatted="1.24"),
                    AnalyticsMetric(
                        label="Max DD",
                        value=3.42,
                        formatted="3.42%",
                    ),
                    AnalyticsMetric(
                        label="Profit Factor",
                        value=1.68,
                        formatted="1.68x",
                    ),
                ],
            )
