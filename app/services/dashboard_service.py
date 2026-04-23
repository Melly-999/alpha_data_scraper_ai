from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.common import Mode
from app.schemas.dashboard import (
    ActivityFeedItem,
    ApiStatus,
    DashboardSummary,
    EquityCurvePoint,
    ServiceDependencyStatus,
    SystemStatus,
    WatchlistItem,
)
from app.services.account_service import AccountService
from app.services.fixture_data import (
    prototype_activity_feed,
    prototype_equity_curve,
    prototype_watchlist,
)
from app.services.mt5_service import MT5Service
from app.services.risk_service import RiskService
from app.services.signal_service import SignalService


class DashboardService:
    def __init__(
        self,
        *,
        account_service: AccountService,
        signal_service: SignalService,
        risk_service: RiskService,
        mt5_service: MT5Service,
        fallback_mode: bool,
        claude_available: bool,
        news_available: bool,
    ) -> None:
        self._account_service = account_service
        self._signal_service = signal_service
        self._risk_service = risk_service
        self._mt5_service = mt5_service
        self._fallback_mode = fallback_mode
        self._claude_available = claude_available
        self._news_available = news_available

    def get_summary(self) -> DashboardSummary:
        account = self._account_service.get_account_overview()
        signals = self._signal_service.list_signals()
        risk_status = self._risk_service.get_status(
            open_positions=account.open_positions,
            drawdown=account.drawdown,
            daily_loss_used=abs(account.daily_pnl_pct),
        )
        mt5 = self._mt5_service.get_status()
        return DashboardSummary(
            system_status=SystemStatus(
                mt5=ServiceDependencyStatus(
                    active=mt5.connected,
                    detail=mt5.server,
                    latency_ms=mt5.latency_ms,
                    last_update=mt5.last_heartbeat,
                ),
                api=ApiStatus(
                    healthy=True,
                    uptime="runtime",
                    version="0.1.0",
                    fallback_mode=self._fallback_mode,
                ),
                claude=ServiceDependencyStatus(
                    active=self._claude_available,
                    detail="Anthropic Claude",
                    model=(
                        "claude-3-sonnet-20240229" if self._claude_available else None
                    ),
                ),
                news=ServiceDependencyStatus(
                    active=self._news_available,
                    detail="News sentiment pipeline",
                ),
                symbol="EURUSD",
                mode=Mode.DRY_RUN,
                last_tick=mt5.last_heartbeat,
                emergency_stop=self._risk_service.get_config().emergency_pause,
            ),
            account=account,
            ready_signals=[signal for signal in signals if signal.eligible],
            risk_status=risk_status,
            watchlist=[
                WatchlistItem.model_validate(item) for item in prototype_watchlist()
            ],
            activity_feed=[
                ActivityFeedItem.model_validate(item)
                for item in prototype_activity_feed()
            ],
            equity_curve=[
                EquityCurvePoint.model_validate(item)
                for item in prototype_equity_curve()
            ],
            generated_at=datetime.now(timezone.utc),
        )
