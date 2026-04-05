"""Trading system configuration."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "trading.log"

# Market / instruments
DEFAULT_SYMBOLS: tuple[str, ...] = ("EURUSD",)
DEFAULT_TIMEFRAME = "M15"

# Session
TRADING_SESSION_START = "08:00"
TRADING_SESSION_END = "18:00"
TIMEZONE = "UTC"

# Risk
ACCOUNT_BALANCE = 100_000.0
MAX_POSITION_SIZE_LOTS = 1.0
MAX_DAILY_LOSS_PCT = 2.0
MAX_OPEN_POSITIONS = 5
RISK_PER_TRADE_PCT = 1.0
STOP_LOSS_PIPS = 20.0
PIP_VALUE_PER_LOT = 10.0  # approx USD per pip per 1.0 lot (e.g. EURUSD)
MIN_CONFIDENCE_TO_TRADE = 50

# Execution
BROKER_NAME = "paper"
SLIPPAGE_POINTS = 2
ORDER_TIMEOUT_SEC = 30

# Backtest
BACKTEST_INITIAL_BALANCE = 100_000.0
BACKTEST_COMMISSION_PER_LOT = 7.0

# Prop-firm / FTMO compliance
FTMO_MODE = True
START_BALANCE = ACCOUNT_BALANCE  # reference balance for daily-loss display
