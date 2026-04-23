from __future__ import annotations

from dataclasses import dataclass

from app.core.dependencies import DependencyStatus, probe_dependencies
from app.core.settings import Settings, load_settings
from app.core.state import RuntimeState
from app.services.account_service import AccountService
from app.services.dashboard_service import DashboardService
from app.services.log_service import LogService
from app.services.mt5_service import MT5Service
from app.services.risk_service import RiskService
from app.services.signal_service import ServiceDependencies, SignalService


@dataclass
class AppContainer:
    settings: Settings
    dependencies: DependencyStatus
    runtime_state: RuntimeState
    log_service: LogService
    account_service: AccountService
    mt5_service: MT5Service
    risk_service: RiskService
    signal_service: SignalService
    dashboard_service: DashboardService


def build_container() -> AppContainer:
    settings = load_settings()
    dependencies = probe_dependencies()
    runtime_state = RuntimeState()
    log_service = LogService()
    account_service = AccountService()
    mt5_service = MT5Service(mt5_available=dependencies.mt5_available)
    risk_service = RiskService(settings.config_path, log_service)
    signal_service = SignalService(
        risk_service=risk_service,
        log_service=log_service,
        account_service=account_service,
        dependencies=ServiceDependencies(
            claude_available=dependencies.claude_available,
            news_available=dependencies.news_available,
        ),
    )
    dashboard_service = DashboardService(
        account_service=account_service,
        signal_service=signal_service,
        risk_service=risk_service,
        mt5_service=mt5_service,
        fallback_mode=dependencies.fallback_mode,
        claude_available=dependencies.claude_available,
        news_available=dependencies.news_available,
    )
    return AppContainer(
        settings=settings,
        dependencies=dependencies,
        runtime_state=runtime_state,
        log_service=log_service,
        account_service=account_service,
        mt5_service=mt5_service,
        risk_service=risk_service,
        signal_service=signal_service,
        dashboard_service=dashboard_service,
    )
