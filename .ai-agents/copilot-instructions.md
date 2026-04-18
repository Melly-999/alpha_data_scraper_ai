# GitHub Copilot Custom Instructions

Custom instructions for GitHub Copilot when working on Alpha AI Trading Terminal.

---

## Core Rules (Non-Negotiable)

### Safety First

- **Auto-trading**: Keep `autotrade.enabled: false` by default. Never enable without explicit user instruction.
- **Dry-run**: Keep `dry_run: true` by default. Never disable without explicit user instruction.
- **Confidence bounds**: Always clamp confidence to `[33, 85]`. Never allow extremes.
- **Min confidence gate**: Enforce `min_confidence >= 70` before live execution.

### Code Quality

- Use `python -m black .` to format all code
- Use `python -m mypy .` for full type checking (must pass)
- Use `python -m flake8 .` for linting (must pass)
- Run `python -m pytest -q` before suggesting code changes
- Never commit code that fails linting/typing/testing

### Path Conventions

- **Always use relative paths**: `./src/file.py` not `/Users/name/project/src/file.py`
- Never use Windows backslashes in code paths
- Relative paths work cross-platform and are required for MCP tools

---

## When Writing Code

### Type Hints (Required)

```python
# ✅ CORRECT
from __future__ import annotations  # Required at top

def generate_signal(df: pd.DataFrame, symbol: str) -> SignalResult:
    """Generate signal with full type safety."""
    pass

# ❌ WRONG
def generate_signal(df, symbol):  # Missing types
    pass
```

### Logging (Required)

```python
# ✅ CORRECT
from core.logger import get_logger
log = get_logger(__name__)
log.info("Signal generated", extra={"confidence": 0.75})

# ❌ WRONG
print(f"Signal: {signal}")  # No logging in production code
```

### Dataclasses (For Return Types)

```python
# ✅ CORRECT
from dataclasses import dataclass

@dataclass
class SignalResult:
    signal: str
    confidence: float
    reason: str

def analyze(df) -> SignalResult:
    return SignalResult(...)

# ❌ WRONG
def analyze(df):
    return {"signal": "BUY", "confidence": 0.75}  # Not structured
```

### Error Handling (Graceful Degradation)

```python
# ✅ CORRECT
try:
    data = mt5.fetch(...)
except:
    log.warning("MT5 failed, using fallback")
    data = _synthetic_rates(...)  # Never crash

# ❌ WRONG
data = mt5.fetch(...)  # Crashes if MT5 fails
```

### Confidence Clamping (Always)

```python
# ✅ CORRECT
import numpy as np
confidence = np.clip(raw_confidence, 33, 85)  # Always clamp

# ❌ WRONG
confidence = raw_confidence  # Could exceed bounds
```

---

## File Organization

### Where to Add Code

**Signal Generation**:

- `signal_generator.py` — BUY/SELL/HOLD logic
- `multi_timeframe.py` — M1/M5/H1 fusion
- `strategy/signal_generator.py` — Regime-aware logic

**Data Fetching**:

- `mt5_fetcher.py` — MT5 + fallback
- `data/fetch.py` — Generic utilities

**Order Execution**:

- `mt5_trader.py` — Placement + risk gates
- `risk/risk_manager.py` — Pre-trade gates

**Analysis & Indicators**:

- `indicators.py` — Basic indicators
- `strategy/indicators.py` — Advanced indicators
- `lstm_model.py` — Price prediction

**Testing**:

- `tests/conftest.py` — Shared fixtures
- `tests/test_*.py` — Test modules

### Never Edit

- `requirements.txt` — Only with approval
- `.github/workflows/` — Only CI experts
- Deployment files (`k8s/`, `docker-compose.yml`) — Only with review

---

## Common Patterns

### Signal Result

```python
SignalResult(
    signal="BUY",           # Must be "BUY", "SELL", "HOLD"
    confidence=0.75,        # Must be [33, 85]
    regime="TRENDING_UP",   # Must be one of three regimes
    reason="RSI overbought" # Human-readable explanation
)
```

### Risk Context

```python
RiskContext(
    daily_loss_limit=500,
    max_open_positions=3,
    min_confidence=0.70,
    current_loss=-200,
    open_positions=1
)
```

### Test with Fixture

```python
def test_signal_generation(sample_ohlcv):
    """Use sample_ohlcv fixture for deterministic tests."""
    result = generate_signal(sample_ohlcv)
    assert 33 <= result.confidence <= 85
```

---

## Before Committing

### Pre-Commit Checklist

```bash
□ python -m black .           # Format
□ python -m flake8 .          # Lint
□ python -m mypy .            # Type check
□ python -m pytest -q         # Tests
□ No secrets in code
□ Relative paths only (./path)
□ All logging uses core/logger.py
□ Confidence values clamped [33, 85]
□ Graceful degradation for optional deps
□ Dataclasses for return types
```

### Git Workflow

```bash
git add .
git commit -m "feat(signal): implement unified signal aggregation"
# Format: [type](scope): description
# Types: feat, fix, docs, test, refactor, chore
git push origin branch-name
# Create PR on GitHub
```

---

## MCP Integration

For long sessions, use MCP tools to save progress:

```python
# At session start:
identify_context({ file_path: "./ai_engine.py" })
get_current_focus()
get_merged_guidelines({ context: "backend" })

# During work:
# ... write code ...

# When changing focus:
create_checkpoint({
    "summary": "Added signal clamping",
    "next_focus": "Claude validation"
})

# When done:
complete_session({
    "final_summary": "Signal aggregation complete",
    "tests_passing": True,
    "ready_for_pr": True
})
```

**Remember**: Always use `./relative/paths` in MCP calls.

---

## Documentation Requirements

### When to Document

```python
change_type = "feature"
complexity = "complex"
# → Documentation required

change_type = "bugfix"
complexity = "simple"
# → Code comments sufficient
```

### Documentation Levels

1. **Code comments**: Simple bugfixes (docstrings)
2. **README updates**: Configuration changes
3. **User guide**: New CLI commands (`docs/GUIDE_*.md`)
4. **Developer guide**: New modules (`docs/DEV_*.md`)
5. **ADR**: Major architectural decisions (`docs/ADR_*.md`)

### Before Creating Docs

```python
check_existing_documentation({
    "title": "Signal Generation",
    "context": "backend",
    "keywords": ["signal", "generation"]
})
# If docs exist, update instead of creating new
```

---

## Common Mistakes to Avoid

❌ **Enabling autotrade by default**

```python
"enabled": true,  # NEVER
```

❌ **Confidence out of bounds**

```python
confidence = 0.95  # Must be [33, 85]
```

❌ **Using print() for logging**

```python
print(f"Signal: {signal}")  # Use log.info()
```

❌ **Absolute paths**

```python
"./Users/name/project/file.py"  # Use ./file.py
```

❌ **No type hints**

```python
def analyze(df):  # Missing types
```

❌ **No fallback for external APIs**

```python
data = mt5.fetch(...)  # No try/except
```

❌ **Hardcoded magic numbers**

```python
if confidence > 0.7:  # Extract to constant
```

❌ **Mixed log levels**

```python
log.info("Debug info...")  # Use log.debug()
```

---

## When You're Stuck

1. **Check AGENTS.md** — Project overview
2. **Check QUICK-REFERENCE.md** — Condensed checklist
3. **Check PATTERNS-REFERENCE.md** — Code patterns used
4. **Check CONTRACT-REFERENCE.md** — Interface contracts
5. **Run tests**: `python -m pytest tests/ -v`
6. **Check related code**: Similar files in codebase
7. **Ask the user** — If truly stuck

---

## Useful Commands (Copy-Paste)

```bash
# Format all code
python -m black .

# Check types
python -m mypy .

# Lint
python -m flake8 .

# Run all tests
python -m pytest -q

# Run one test file
python -m pytest tests/test_signal_generator.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run bot (dry-run)
python main.py

# Run with options
python main.py --symbol EURUSD GBPUSD --continuous --interval 60

# Full pipeline demo
python example_runner.py

# Docker dev
docker-compose up dev

# Kubernetes apply
kubectl apply -f k8s/
```

---

## References

- [AGENTS.md](../AGENTS.md) — Complete project guide (start here)
- [QUICK-REFERENCE.md](./QUICK-REFERENCE.md) — Condensed checklist
- [SKILL.md](./SKILL.md) — Detailed workflows
- [SESSION-WORKFLOW.md](./SESSION-WORKFLOW.md) — MCP integration guide
- [CONTRACT-REFERENCE.md](./CONTRACT-REFERENCE.md) — Critical interfaces
- [PATTERNS-REFERENCE.md](./PATTERNS-REFERENCE.md) — Code patterns
- [DOCUMENTATION-WORKFLOW.md](./DOCUMENTATION-WORKFLOW.md) — Doc rules

---

**Last Updated**: April 2026  
**Model**: Claude Haiku/Sonnet/Opus  
**Focus**: Type-safe, well-tested, production-ready trading system
