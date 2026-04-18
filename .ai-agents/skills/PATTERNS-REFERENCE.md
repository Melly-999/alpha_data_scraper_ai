# PATTERNS-REFERENCE.md – Code Patterns for Alpha AI

Verified patterns used in this codebase. Reference when implementing similar features.

---

## Pattern 1: Graceful Degradation (Fallback Pattern)

Used for: Optional dependencies (MT5, TensorFlow, Claude, NewsAPI)

### Structure

```python
def operation_with_fallback(primary_input):
    """Try primary, fall back to alternative if needed."""
    try:
        # Primary approach
        result = try_primary(primary_input)
        log.info("Primary successful")
        return result
    except (ConnectionError, TimeoutError, Exception) as e:
        # Log the failure
        log.warning(f"Primary failed: {e}, using fallback")
        
        # Fallback approach
        result = use_fallback(primary_input)
        return result

# Example: MT5 Data Fetching
def batch_fetch(symbol: str, timeframe: str, count: int) -> pd.DataFrame:
    """Fetch from MT5 or synthetic."""
    try:
        return mt5.copy_rates_range(symbol, timeframe, ...)
    except:
        log.warning("MT5 unavailable, using synthetic data")
        return _synthetic_rates(symbol, timeframe, count)

# Example: LSTM Prediction
def predict_price(df: pd.DataFrame) -> np.ndarray:
    """Predict with LSTM or naive model."""
    try:
        model = LSTMPipeline()
        return model.predict(df)
    except ImportError:
        log.warning("TensorFlow unavailable, using NaiveSequenceModel")
        model = NaiveSequenceModel()
        return model.predict(df)
```

### When to Use

- Any external API call (MT5, Claude, NewsAPI)
- Optional ML libraries (TensorFlow, scikit-learn)
- Network operations (HTTP, WebSocket)
- File operations (file might not exist)

### Test Pattern

```python
def test_mt5_fallback_on_failure(monkeypatch):
    """Verify fallback when MT5 fails."""
    monkeypatch.setattr(mt5, "copy_rates_range", side_effect=ConnectionError())
    
    result = batch_fetch("EURUSD", "M5", 100)
    
    assert result is not None, "Should return fallback data"
    assert len(result) == 100, "Should return correct count"
```

---

## Pattern 2: Dataclass for Return Types

Used for: Structured return values from functions

### Structure

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SignalResult:
    signal: str          # "BUY", "SELL", "HOLD"
    confidence: float    # [33, 85]
    regime: str          # "TRENDING_UP", "TRENDING_DOWN", "RANGING"
    reason: str          # Human-readable explanation

def generate_signal(df: pd.DataFrame) -> SignalResult:
    """Analyze and return structured signal."""
    # ... analysis ...
    return SignalResult(
        signal="BUY",
        confidence=0.72,
        regime="TRENDING_UP",
        reason="RSI overbought with MACD divergence"
    )

# Usage
signal = generate_signal(df)
print(f"Signal: {signal.signal}, Confidence: {signal.confidence}")
```

### Advantages

- Type-safe (mypy checks)
- Self-documenting (fields are clear)
- Immutable (prevents accidental changes)
- Easy to test (can compare dataclass instances)
- Serializable (can convert to dict/JSON)

### When to Use

- Return multiple related values
- Need structure across multiple functions
- Want clear documentation of return value
- Prefer immutability

### Existing Patterns in Codebase

| Class | File | Fields |
|---|---|---|
| `SignalResult` | signal_generator.py | signal, confidence, regime, reason |
| `EngineConfig` | ai_engine.py | symbol, timeframe, min_confidence, ... |
| `UnifiedSignal` | ai_engine.py | signal, confidence, regime, sources |
| `RiskContext` | risk/risk_manager.py | daily_loss_limit, max_positions, ... |
| `ClaudeSignal` | claude_ai.py | is_valid, recommendation, reasoning |

---

## Pattern 3: Type Hints with Forward References

Used for: Full type safety with mypy

### Structure

```python
from __future__ import annotations  # ← REQUIRED at top of file

import pandas as pd
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class Result:
    value: float
    metadata: Dict[str, str]

def analyze_data(
    df: pd.DataFrame,
    symbols: List[str],
    config: Optional[Dict] = None
) -> Optional[Result]:
    """Analyze with full type hints."""
    if df.empty:
        return None
    
    value = df['close'].mean()
    
    return Result(
        value=value,
        metadata={"symbols": ", ".join(symbols)}
    )

# Run: python -m mypy .
# Must have NO errors
```

### Why Forward References?

Without `from __future__ import annotations`:
```python
# Would need to use strings for forward references
def process(result: 'Result') -> 'Result':  # Clunky
    pass
```

With:
```python
# Can use types naturally
def process(result: Result) -> Result:  # Clean
    pass
```

### Best Practices

```python
from __future__ import annotations  # Always at top

import pandas as pd
from typing import Optional, List, Dict, Tuple, Callable

def complex_function(
    data: pd.DataFrame,
    processor: Callable[[pd.DataFrame], pd.DataFrame],
    threshold: float = 0.5,
    debug: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, float], Optional[str]]:
    """Fully typed complex function."""
    
    # Process
    processed = processor(data)
    
    # Calculate metrics
    metrics = {"mean": processed["close"].mean(), "std": processed["close"].std()}
    
    # Optional message
    message = None
    if debug:
        message = f"Processed {len(data)} rows"
    
    return processed, metrics, message
```

### Test Pattern

```python
def test_types_with_mypy():
    """Verify type checking passes."""
    import subprocess
    result = subprocess.run(["python", "-m", "mypy", "."], capture_output=True)
    assert result.returncode == 0, "mypy failed:\n" + result.stderr.decode()
```

---

## Pattern 4: Logging with Context

Used for: Production logging without clutter

### Structure

```python
from core.logger import get_logger

log = get_logger(__name__)

def process_signal(signal: SignalResult, symbol: str) -> bool:
    """Process with contextual logging."""
    
    log.info(
        "Processing signal",
        extra={
            "symbol": symbol,
            "signal": signal.signal,
            "confidence": signal.confidence,
            "regime": signal.regime
        }
    )
    
    if signal.confidence < 0.70:
        log.warning(
            "Low confidence signal",
            extra={"confidence": signal.confidence, "symbol": symbol}
        )
        return False
    
    try:
        # Process...
        execute(signal)
        log.info(f"Signal executed: {signal.signal} for {symbol}")
        return True
    except Exception as e:
        log.error(
            f"Signal execution failed: {e}",
            exc_info=True,
            extra={"symbol": symbol}
        )
        return False
```

### Log Levels

| Level | Use Case | Example |
|---|---|---|
| **DEBUG** | Diagnostic info | State of variables during processing |
| **INFO** | Normal operation | Signal generated, order executed |
| **WARNING** | Something unexpected | Low confidence, daily loss limit near |
| **ERROR** | Something failed | MT5 connection dropped |
| **CRITICAL** | System must stop | Critical contract violation |

### Never Do This

```python
# ❌ Bare print (production code)
print(f"Signal: {signal.signal}")

# ❌ Manual string formatting in log
log.info("Signal=" + str(signal.signal))

# ❌ Excessive logging
for i in range(1000):
    log.debug(f"Processing item {i}")  # Would be 1000 messages!
```

### Always Do This

```python
# ✅ Structured context
log.info("Signal processed", extra={"signal": signal.signal})

# ✅ Use logging directly
log.info(f"Signal: {signal.signal}")

# ✅ Use level appropriately
log.debug("Detailed diagnostic info")  # Only when needed
```

---

## Pattern 5: Configuration Management

Used for: Runtime configuration without hardcoding

### Structure

```json
{
  "symbol": "EURUSD",
  "timeframe": "M5",
  "bars": 700,
  "autotrade": {
    "enabled": false,
    "dry_run": true,
    "min_confidence": 0.70
  }
}
```

```python
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AutoTradeConfig:
    enabled: bool
    dry_run: bool
    min_confidence: float

@dataclass
class Config:
    symbol: str
    timeframe: str
    bars: int
    autotrade: AutoTradeConfig

def load_config(path: str = "./config.json") -> Config:
    """Load config from JSON."""
    with open(path) as f:
        data = json.load(f)
    
    return Config(
        symbol=data["symbol"],
        timeframe=data["timeframe"],
        bars=data["bars"],
        autotrade=AutoTradeConfig(**data["autotrade"])
    )

def save_config(config: Config, path: str = "./config.json"):
    """Save config to JSON."""
    data = {
        "symbol": config.symbol,
        "timeframe": config.timeframe,
        "bars": config.bars,
        "autotrade": {
            "enabled": config.autotrade.enabled,
            "dry_run": config.autotrade.dry_run,
            "min_confidence": config.autotrade.min_confidence,
        }
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

### Usage

```python
# Load
config = load_config()

# Check safety defaults
assert not config.autotrade.enabled, "Auto-trading should be disabled by default"
assert config.autotrade.dry_run, "Dry-run should be enabled by default"

# Use
engine = AIEngine(config)
```

---

## Pattern 6: Input Validation

Used for: Ensuring data integrity before processing

### Structure

```python
from typing import Optional

def process_symbol(symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
    """Process with full validation."""
    
    # Validate input types
    if not isinstance(symbol, str):
        raise TypeError(f"symbol must be str, got {type(symbol)}")
    if not isinstance(timeframe, str):
        raise TypeError(f"timeframe must be str, got {type(timeframe)}")
    
    # Validate non-empty
    if not symbol.strip():
        raise ValueError("symbol cannot be empty")
    if not timeframe.strip():
        raise ValueError("timeframe cannot be empty")
    
    # Validate allowed values
    valid_timeframes = ["M1", "M5", "H1", "D1"]
    if timeframe not in valid_timeframes:
        raise ValueError(f"timeframe must be one of {valid_timeframes}, got {timeframe}")
    
    # Validate symbol format (e.g., EURUSD)
    if not symbol.isupper() or len(symbol) != 6:
        raise ValueError(f"symbol must be uppercase 6-char pair, got {symbol}")
    
    # Now safe to process
    try:
        data = batch_fetch(symbol, timeframe, 700)
        return data
    except Exception as e:
        log.error(f"Processing failed for {symbol}/{timeframe}: {e}")
        return None

# Usage
try:
    df = process_symbol("EURUSD", "M5")
except (TypeError, ValueError) as e:
    log.error(f"Invalid input: {e}")
```

### Validation Hierarchy

```
1. Type checking (is it a string?)
2. Non-empty (does it have content?)
3. Format (does it match pattern?)
4. Range (is value within acceptable bounds?)
5. Allowed values (is it in whitelist?)
6. Dependencies (do other values make sense?)
```

---

## Pattern 7: Testing with Fixtures

Used for: Shared test data across multiple tests

### Structure

```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_ohlcv():
    """260-bar OHLCV data (seed=123, deterministic)."""
    np.random.seed(123)
    
    close = np.random.randn(260).cumsum() * 0.01 + 1.0
    
    return pd.DataFrame({
        'open': close + np.random.randn(260) * 0.001,
        'high': close + np.abs(np.random.randn(260)) * 0.002,
        'low': close - np.abs(np.random.randn(260)) * 0.002,
        'close': close,
        'tick_volume': np.random.randint(1000, 10000, 260),
        'time': pd.date_range(end=pd.Timestamp.now(), periods=260, freq='5min')
    })

# tests/test_indicators.py
def test_rsi_calculation(sample_ohlcv):
    """Test RSI with fixture data."""
    rsi = calculate_rsi(sample_ohlcv)
    
    assert len(rsi) == len(sample_ohlcv)
    assert (rsi >= 0).all() and (rsi <= 100).all()

def test_signal_generation(sample_ohlcv):
    """Test signal with same fixture data."""
    signal = generate_signal(sample_ohlcv)
    
    assert 33 <= signal.confidence <= 85
    assert signal.signal in ["BUY", "SELL", "HOLD"]
```

### Benefits

- **Deterministic**: seed=123 ensures reproducible tests
- **Reusable**: Same data across all tests
- **Realistic**: 260 bars matches typical analysis window
- **Fast**: Pre-computed once, not regenerated per test

### Adding New Fixtures

```python
@pytest.fixture
def market_context():
    """Fixture for market context."""
    return {
        "regime": "TRENDING_UP",
        "volatility": 0.025,
        "news_sentiment": 0.65
    }

def test_signal_with_context(sample_ohlcv, market_context):
    """Test signal generation with market context."""
    signal = generate_signal(sample_ohlcv, market_context)
    # ... assertions ...
```

---

## Pattern 8: Error Handling with Cleanup

Used for: Resource management and cleanup

### Structure

```python
def operation_with_cleanup():
    """Operation with guaranteed cleanup."""
    
    resource = None
    try:
        # Acquire resource
        resource = acquire_mt5_connection()
        log.info("Connection acquired")
        
        # Use resource
        data = resource.fetch_data("EURUSD", "M5", 700)
        log.info(f"Fetched {len(data)} bars")
        
        return data
    
    except (ConnectionError, TimeoutError) as e:
        log.warning(f"Operation failed (will retry): {e}")
        # Try fallback
        return _synthetic_rates("EURUSD", "M5", 700)
    
    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        raise
    
    finally:
        # Always cleanup, even if exception
        if resource is not None:
            try:
                resource.close()
                log.info("Connection closed")
            except Exception as e:
                log.warning(f"Cleanup failed: {e}")

# With context manager (preferred)
def operation_with_context_manager():
    """Cleaner with context manager."""
    
    try:
        with acquire_mt5_connection() as connection:
            data = connection.fetch_data("EURUSD", "M5", 700)
            return data
    
    except ConnectionError:
        log.warning("MT5 failed, using fallback")
        return _synthetic_rates("EURUSD", "M5", 700)
```

---

## Pattern 9: Caching for Performance

Used for: Expensive computations that don't change frequently

### Structure

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedAnalyzer:
    """Analyzer with caching."""
    
    def __init__(self, cache_ttl: int = 60):
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.cache_time = {}
    
    def get_indicator(self, symbol: str, indicator: str) -> float:
        """Get indicator with caching."""
        
        cache_key = f"{symbol}:{indicator}"
        
        # Check if cached and not expired
        if cache_key in self.cache:
            age = (datetime.now() - self.cache_time[cache_key]).total_seconds()
            if age < self.cache_ttl:
                log.debug(f"Cache hit: {cache_key}")
                return self.cache[cache_key]
        
        # Compute if not cached
        log.debug(f"Cache miss: {cache_key}, computing...")
        value = self._compute_indicator(symbol, indicator)
        
        # Store in cache
        self.cache[cache_key] = value
        self.cache_time[cache_key] = datetime.now()
        
        return value
    
    def _compute_indicator(self, symbol: str, indicator: str) -> float:
        """Expensive computation."""
        df = batch_fetch(symbol, "M5", 700)
        
        if indicator == "rsi":
            return calculate_rsi(df).iloc[-1]
        elif indicator == "macd":
            return calculate_macd(df).iloc[-1]
        else:
            raise ValueError(f"Unknown indicator: {indicator}")

# Usage
analyzer = CachedAnalyzer(cache_ttl=60)  # 60 second cache

# First call (computes)
rsi = analyzer.get_indicator("EURUSD", "rsi")

# Second call within 60s (cached)
rsi = analyzer.get_indicator("EURUSD", "rsi")  # Returns cached value
```

---

## Pattern 10: Enum for State Management

Used for: Finite state values (Market Regime, Signal Type)

### Structure

```python
from enum import Enum

class MarketRegime(str, Enum):
    """Market regime states."""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"

class SignalType(str, Enum):
    """Signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

def analyze_regime(df: pd.DataFrame) -> MarketRegime:
    """Determine market regime."""
    
    # ... analysis ...
    
    if trend_up:
        return MarketRegime.TRENDING_UP
    elif trend_down:
        return MarketRegime.TRENDING_DOWN
    else:
        return MarketRegime.RANGING

# Usage
regime = analyze_regime(df)

# Type-safe
if regime == MarketRegime.TRENDING_UP:
    print("Bullish market")
elif regime == MarketRegime.TRENDING_DOWN:
    print("Bearish market")
else:
    print("Range-bound market")

# Can iterate over all values
for r in MarketRegime:
    print(f"Regime: {r.value}")
```

---

## Summary: When to Use Each Pattern

| Pattern | Use Case | Key Files |
|---|---|---|
| **Graceful Degradation** | Optional external deps | mt5_fetcher.py, lstm_model.py, claude_ai.py |
| **Dataclass** | Structured return types | signal_generator.py, ai_engine.py, risk_manager.py |
| **Type Hints** | Type safety | All files (mypy required) |
| **Logging** | Diagnostics | All files (core/logger.py) |
| **Configuration** | Runtime params | config.json, core/config.py |
| **Input Validation** | Data integrity | Before processing user input |
| **Fixtures** | Shared test data | tests/conftest.py |
| **Error Handling** | Reliability | All error paths |
| **Caching** | Performance | Expensive computations |
| **Enum** | State management | strategy/signal_generator.py |

---

All of these patterns are demonstrated in existing code. Reference them when implementing similar features.
