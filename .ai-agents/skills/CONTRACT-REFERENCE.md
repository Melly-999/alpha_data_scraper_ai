# CONTRACT-REFERENCE.md – Critical Interfaces

Critical contracts that must be upheld in all implementations. Validate code against these rules before committing.

---

## Contract 1: Signal Result Structure

**Location**: `signal_generator.py`  
**Status**: CRITICAL  
**Validation**: Always validate before returning

```python
@dataclass
class SignalResult:
    signal: str          # MUST be "BUY", "SELL", or "HOLD"
    confidence: float    # MUST be in range [33, 85] (CLAMPED)
    regime: str          # MUST be "TRENDING_UP", "TRENDING_DOWN", or "RANGING"
    reason: str          # Human-readable explanation
```

### Contract Rules

| Rule | Validation | Enforcement |
|---|---|---|
| `signal` is valid | Must be in `["BUY", "SELL", "HOLD"]` | Raises ValueError if not |
| `confidence` is clamped | Must satisfy `33 <= confidence <= 85` | Auto-clamp: `np.clip(x, 33, 85)` |
| `regime` is valid | Must be in `["TRENDING_UP", "TRENDING_DOWN", "RANGING"]` | Raises ValueError if not |
| `reason` is non-empty | Must be non-empty string | Raises ValueError if empty |

### Validation Code Pattern

```python
def generate_signal(df: pd.DataFrame) -> SignalResult:
    """Generate signal with contract validation."""
    
    # ... calculation ...
    
    raw_confidence = 0.72
    signal = "BUY"
    regime = "TRENDING_UP"
    reason = "RSI overbought with MACD divergence"
    
    # VALIDATE & CLAMP
    confidence = np.clip(raw_confidence, 33, 85)
    
    assert signal in ["BUY", "SELL", "HOLD"], f"Invalid signal: {signal}"
    assert 33 <= confidence <= 85, f"Confidence out of bounds: {confidence}"
    assert regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING"], f"Invalid regime: {regime}"
    assert reason, "Reason cannot be empty"
    
    return SignalResult(
        signal=signal,
        confidence=confidence,
        regime=regime,
        reason=reason
    )
```

### Test Pattern

```python
def test_signal_result_contract():
    """Validate SignalResult contracts."""
    result = generate_signal(sample_ohlcv)
    
    # Test confidence bounds
    assert 33 <= result.confidence <= 85, "Confidence out of bounds"
    
    # Test signal enum
    assert result.signal in ["BUY", "SELL", "HOLD"], "Invalid signal"
    
    # Test regime enum
    assert result.regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING"], "Invalid regime"
    
    # Test reason non-empty
    assert len(result.reason) > 0, "Reason cannot be empty"
```

---

## Contract 2: Risk Manager Pre-Trade Gates

**Location**: `risk/risk_manager.py`  
**Status**: CRITICAL  
**Enforcement**: Applied before ANY order execution

```python
@dataclass
class RiskContext:
    daily_loss_limit: float  # Max loss for the day (e.g., 500 USD)
    max_open_positions: int  # Max concurrent trades (e.g., 3)
    min_confidence: float    # Min signal confidence (e.g., 0.70)
    current_loss: float      # Current P&L for the day
    open_positions: int      # Current number of open trades

class RiskManager:
    def check(self, signal: SignalResult, context: RiskContext) -> bool:
        """
        Return True if signal passes ALL gates, False otherwise.
        MUST NOT execute trade if any gate fails.
        """
        # Gate 1: Confidence minimum
        if signal.confidence < context.min_confidence:
            log.warning(f"Signal rejected: confidence {signal.confidence} < min {context.min_confidence}")
            return False
        
        # Gate 2: Daily loss limit
        if context.current_loss <= -context.daily_loss_limit:
            log.warning(f"Signal rejected: daily loss limit exceeded ({context.current_loss})")
            return False
        
        # Gate 3: Max open positions
        if context.open_positions >= context.max_open_positions:
            log.warning(f"Signal rejected: max open positions ({context.open_positions}) reached")
            return False
        
        return True
```

### Contract Rules

| Gate | Rule | Action |
|---|---|---|
| **Confidence** | `signal.confidence >= min_confidence` | Reject if lower |
| **Daily Loss** | `current_loss > -daily_loss_limit` | Stop trading if exceeded |
| **Max Positions** | `open_positions < max_open_positions` | Reject if max reached |

### Validation Pattern

```python
def execute_signal(signal: SignalResult, context: RiskContext) -> bool:
    """Execute signal ONLY if it passes risk gates."""
    
    risk_mgr = RiskManager()
    
    if not risk_mgr.check(signal, context):
        log.info(f"Signal rejected by risk manager: {signal.signal}")
        return False
    
    # Safe to execute
    log.info(f"Signal approved by risk manager: {signal.signal}")
    return True
```

### Test Pattern

```python
def test_risk_gate_confidence():
    """Gate 1: Confidence minimum."""
    mgr = RiskManager()
    context = RiskContext(
        daily_loss_limit=500,
        max_open_positions=3,
        min_confidence=0.70,
        current_loss=0,
        open_positions=1
    )
    
    # Signal too low confidence
    signal = SignalResult(signal="BUY", confidence=0.65, regime="TRENDING_UP", reason="...")
    assert not mgr.check(signal, context), "Should reject low confidence"
    
    # Signal meets minimum
    signal = SignalResult(signal="BUY", confidence=0.75, regime="TRENDING_UP", reason="...")
    assert mgr.check(signal, context), "Should accept meeting minimum"

def test_risk_gate_daily_loss():
    """Gate 2: Daily loss limit."""
    mgr = RiskManager()
    context = RiskContext(
        daily_loss_limit=500,
        max_open_positions=3,
        min_confidence=0.70,
        current_loss=-600,  # Over limit
        open_positions=1
    )
    
    signal = SignalResult(signal="BUY", confidence=0.75, regime="TRENDING_UP", reason="...")
    assert not mgr.check(signal, context), "Should reject when daily loss exceeded"

def test_risk_gate_max_positions():
    """Gate 3: Max open positions."""
    mgr = RiskManager()
    context = RiskContext(
        daily_loss_limit=500,
        max_open_positions=3,
        min_confidence=0.70,
        current_loss=0,
        open_positions=3  # At max
    )
    
    signal = SignalResult(signal="BUY", confidence=0.75, regime="TRENDING_UP", reason="...")
    assert not mgr.check(signal, context), "Should reject when max positions reached"
```

---

## Contract 3: MT5 Fallback Behavior

**Location**: `mt5_fetcher.py`  
**Status**: CRITICAL  
**Enforcement**: Apply graceful degradation pattern

```python
def batch_fetch(symbol: str, timeframe: str, count: int) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data. On failure, return synthetic data (fallback).
    MUST NOT crash—graceful degradation required.
    """
    try:
        # Try real MT5 API
        data = mt5.copy_rates_range(symbol, timeframe, start, end)
        log.info(f"Fetched {len(data)} bars from MT5 for {symbol}")
        return pd.DataFrame(data)
    except ConnectionError:
        log.warning(f"MT5 connection failed, using synthetic data for {symbol}")
        return _synthetic_rates(symbol, timeframe, count)
    except Exception as e:
        log.error(f"MT5 fetch error: {e}, using synthetic data", exc_info=True)
        return _synthetic_rates(symbol, timeframe, count)

def _synthetic_rates(symbol: str, timeframe: str, count: int) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data (seeded for reproducibility).
    Used when MT5 is unavailable.
    """
    np.random.seed(123)  # Deterministic for testing
    
    # Generate realistic OHLCV with open ~= close, high > open/close, low < open/close
    close = np.random.randn(count).cumsum() * 0.001 + 1.0
    
    return pd.DataFrame({
        'open': close + np.random.randn(count) * 0.001,
        'high': close + np.abs(np.random.randn(count)) * 0.002,
        'low': close - np.abs(np.random.randn(count)) * 0.002,
        'close': close,
        'tick_volume': np.random.randint(1000, 10000, count),
        'time': pd.date_range(end=pd.Timestamp.now(), periods=count, freq='5min')
    })
```

### Contract Rules

| Rule | Enforcement |
|---|---|
| **Never crash** | Try/except + fallback to synthetic |
| **Log failures** | Always log MT5 errors |
| **Deterministic fallback** | Seed=123 for reproducibility |
| **Return valid OHLCV** | DataFrame with [open, high, low, close, volume, time] |

### Validation Pattern

```python
def verify_ohlcv_contract(df: pd.DataFrame) -> bool:
    """Validate OHLCV data structure."""
    required_cols = ['open', 'high', 'low', 'close', 'tick_volume']
    assert all(col in df.columns for col in required_cols), "Missing OHLCV columns"
    
    # OHLCV relationship: high >= max(open, close), low <= min(open, close)
    assert (df['high'] >= df[['open', 'close']].max(axis=1)).all(), "high < open or close"
    assert (df['low'] <= df[['open', 'close']].min(axis=1)).all(), "low > open or close"
    
    # No NaN/Inf values
    assert not df.isnull().any().any(), "DataFrame contains NaN values"
    assert not df.isin([np.inf, -np.inf]).any().any(), "DataFrame contains Inf values"
    
    return True
```

### Test Pattern

```python
def test_mt5_fallback_on_failure(monkeypatch):
    """Verify fallback to synthetic when MT5 fails."""
    # Mock MT5 to fail
    monkeypatch.setattr(mt5, "copy_rates_range", side_effect=ConnectionError("MT5 down"))
    
    # Should return synthetic data, not crash
    df = batch_fetch("EURUSD", "M5", 100)
    assert df is not None, "Should return synthetic data on MT5 failure"
    assert len(df) == 100, "Should return requested count"
    assert verify_ohlcv_contract(df), "Synthetic data must be valid OHLCV"
```

---

## Contract 4: Confidence Clamping

**Location**: `signal_generator.py`, `multi_timeframe.py`, `claude_ai.py`  
**Status**: CRITICAL  
**Enforcement**: Every confidence value must be clamped

```python
import numpy as np

def clamp_confidence(raw_confidence: float) -> float:
    """
    Clamp confidence to [33, 85] range.
    MUST be applied after every confidence calculation.
    """
    clamped = np.clip(raw_confidence, 33, 85)
    
    if clamped != raw_confidence:
        log.debug(f"Confidence clamped: {raw_confidence} → {clamped}")
    
    return float(clamped)

# USAGE PATTERN:
def generate_signal(df: pd.DataFrame) -> SignalResult:
    # ... calculate raw_confidence ...
    raw_confidence = (0.5 + rsi_score + macd_score) / 2  # e.g., 0.72
    
    # CLAMP IMMEDIATELY
    confidence = clamp_confidence(raw_confidence)  # Always [33, 85]
    
    return SignalResult(..., confidence=confidence, ...)
```

### Contract Rules

| Rule | Enforcement |
|---|---|
| **Range** | Always clamp to `[33, 85]` |
| **Never override** | Do not bypass clamping |
| **Log if changed** | Debug log when clamping modifies value |
| **Type**: float | Convert to float if needed |

### Test Pattern

```python
def test_confidence_always_clamped():
    """Every signal must have confidence in [33, 85]."""
    test_cases = [
        ("EURUSD", 100),  # Could give raw_confidence > 85
        ("GBPUSD", 50),   # Could give raw_confidence < 33
        ("USDJPY", 200),  # Extreme case
    ]
    
    for symbol, count in test_cases:
        df = batch_fetch(symbol, "M5", count)
        signal = generate_signal(df)
        
        assert 33 <= signal.confidence <= 85, \
            f"Confidence {signal.confidence} out of bounds for {symbol}"
```

---

## Contract 5: Data Flow Integrity

**Location**: `ai_engine.py`  
**Status**: CRITICAL  
**Enforcement**: Validate at each pipeline stage

```python
class AIEngine:
    def generate_signal(self, symbol: str) -> UnifiedSignal:
        """
        Pipeline: Fetch → Analyze → Fuse → Validate → Return
        MUST validate output at each stage.
        """
        
        # Stage 1: Fetch (must not crash)
        df = self._fetch_data(symbol)
        if df is None:
            log.error(f"Failed to fetch data for {symbol}")
            return None
        assert verify_ohlcv_contract(df), "Invalid OHLCV after fetch"
        
        # Stage 2: Analyze (must return SignalResult)
        signal = self._analyze(df)
        assert signal is not None, "Analysis returned None"
        assert 33 <= signal.confidence <= 85, "Confidence out of bounds after analysis"
        
        # Stage 3: Fuse (must preserve confidence bounds)
        fused = self._fuse_timeframes(signal)
        assert fused is not None, "Fusion returned None"
        assert 33 <= fused.confidence <= 85, "Confidence out of bounds after fusion"
        
        # Stage 4: Validate (Claude validation)
        validated = self._validate_with_claude(fused)
        if validated is None:
            log.warning("Claude validation skipped or failed")
            validated = fused  # Use unfused result
        assert 33 <= validated.confidence <= 85, "Confidence out of bounds after validation"
        
        # Stage 5: Return (must be UnifiedSignal)
        return validated
```

### Contract Rules

| Stage | Contract |
|---|---|
| **Fetch** | Must not crash; fallback to synthetic if needed |
| **Analyze** | Must return SignalResult with confidence [33, 85] |
| **Fuse** | Must preserve confidence bounds after weighting |
| **Validate** | Must not modify confidence outside [33, 85] |
| **Return** | Must return UnifiedSignal or None (never crash) |

### Validation Pattern

```python
def validate_pipeline_integrity(signal: UnifiedSignal) -> bool:
    """
    Verify signal integrity through entire pipeline.
    Use before executing order.
    """
    if signal is None:
        return False
    
    checks = [
        (33 <= signal.confidence <= 85, "Confidence out of bounds"),
        (signal.signal in ["BUY", "SELL", "HOLD"], "Invalid signal"),
        (signal.regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING"], "Invalid regime"),
        (len(signal.reason) > 0, "Reason cannot be empty"),
    ]
    
    for check, msg in checks:
        assert check, msg
    
    return True
```

---

## Contract 6: Logging Standards

**Location**: All files  
**Status**: IMPORTANT  
**Enforcement**: No bare print() in production code

```python
from core.logger import get_logger

log = get_logger(__name__)

# CORRECT PATTERNS:
log.info("Signal generated", extra={"signal": "BUY", "confidence": 0.75})
log.warning("Daily loss limit approaching", extra={"current_loss": -450})
log.error("MT5 connection failed", exc_info=True)

# INCORRECT (never do these in production):
print("Signal generated")  # ❌ Can't suppress
print(f"Confidence: {signal.confidence}")  # ❌ Goes to stdout
print(signal)  # ❌ No context
```

### Contract Rules

| Rule | Enforcement |
|---|---|
| **Use core.logger** | All logging via `get_logger()` |
| **No bare print()** | Only in `if __name__ == "__main__"` for CLI output |
| **Add context** | Include relevant variables in `extra` dict |
| **Log exceptions** | Use `exc_info=True` for error tracebacks |
| **Appropriate level** | INFO (normal), WARNING (issues), ERROR (problems), DEBUG (diagnostic) |

---

## Validation Commands

Run these before every commit:

```bash
# Type check (must pass)
python -m mypy .

# Lint (must pass)
python -m flake8 .

# Format (must pass)
python -m black --check .

# Tests (must pass - validates contracts)
python -m pytest tests/ -v

# Quick validation script
python -c "
from signal_generator import SignalResult
import numpy as np

# Test confidence clamping
for raw in [10, 33, 50, 85, 100]:
    clamped = np.clip(raw, 33, 85)
    assert 33 <= clamped <= 85
    print(f'✓ {raw} → {clamped}')
"
```

---

## When Contracts Are Violated

**Response Protocol**:

1. **Stop execution** — Do not proceed
2. **Log error** — Record exact violation
3. **Revert changes** — Undo what caused violation
4. **Add test** — Prevent future violations
5. **Review code** — Understand root cause

Example:

```python
# Violation detected
try:
    result = generate_signal(df)
    assert 33 <= result.confidence <= 85
except AssertionError:
    log.error(f"CRITICAL: Confidence {result.confidence} violates contract", exc_info=True)
    
    # Emergency: revert to previous logic
    result = fallback_signal()
    
    # Add test to prevent regression
    # See: test_confidence_bounds()
```

---

**Summary**: These contracts are non-negotiable. Validate against them before every commit.
