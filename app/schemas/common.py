from __future__ import annotations

from enum import Enum


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ClaudeStatus(str, Enum):
    VALIDATED = "VALIDATED"
    INSUFFICIENT = "INSUFFICIENT"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class BlockedReason(str, Enum):
    COOLDOWN = "COOLDOWN"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MAX_POSITIONS = "MAX_POSITIONS"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"
    MISSING_PROTECTION = "MISSING_PROTECTION"
    NO_TRADE_SIGNAL = "NO_TRADE_SIGNAL"
    RISK_LIMIT = "RISK_LIMIT"


class Severity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class OrderStatus(str, Enum):
    FILLED = "FILLED"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderSource(str, Enum):
    AI = "AI"
    MANUAL = "MANUAL"


class LogCategory(str, Enum):
    SYSTEM = "SYSTEM"
    SIGNALS = "SIGNALS"
    EXECUTION = "EXECUTION"
    RISK = "RISK"
    MT5 = "MT5"
    API = "API"


class Mode(str, Enum):
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"


class DataSource(str, Enum):
    MT5 = "mt5"
    FALLBACK = "fallback"
    SYNTHETIC = "synthetic"
    TECHNICAL_MODEL = "technical_model"
    FIXTURE = "fixture"
    BACKTEST = "backtest"
