---
name: alpha-trading-system
description: Algorithmic trading terminal with Claude AI validation, technical analysis, and risk management. Use when working on signal generation, data fetching, order execution, risk gates, or LSTM prediction models. MT5 integration with fallbacks for graceful degradation.
---

# Alpha AI Trading System Skill

Comprehensive skill for working on the `alpha_data_scraper_ai` project. This hub points to detailed workflows and reference materials.

---

## Quick Start (5 minutes)

### Common Tasks

**Working on signals?**

- See: [SIGNAL-GENERATION.md](./SIGNAL-GENERATION.md)
- Files: `signal_generator.py`, `multi_timeframe.py`, `claude_ai.py`

**Working on data/MT5?**

- See: [DATA-FETCHING.md](./DATA-FETCHING.md)
- Files: `mt5_fetcher.py`, `mt5_trader.py`, `metrics_server.py`

**Working on risk management?**

- See: [RISK-GATES.md](./RISK-GATES.md)
- Files: `risk/risk_manager.py`, `calculator.py`

**Working on ML/LSTM?**

- See: [LSTM-PIPELINE.md](./LSTM-PIPELINE.md)
- Files: `lstm_model.py`, `ai/lstm_model.py`, `indicators.py`

**Writing tests?**

- See: [TESTING-PATTERNS.md](./TESTING-PATTERNS.md)
- Files: `tests/conftest.py`, `tests/test_*.py`

**Setting up documentation?**

- See: [DOCUMENTATION-WORKFLOW.md](./DOCUMENTATION-WORKFLOW.md)

---

## MCP Tool Integration

Before any work, establish context with MCP:

```python
# Python example (or use terminal commands)
from mcp_client import MCPClient

client = MCPClient()

# 1. Identify context
context = client.identify_context(file_path="./ai_engine.py")
print(context)  # { "project": "alpha_data_scraper_ai", "context": "backend" }

# 2. Get current focus
focus = client.get_current_focus()

# 3. Load guidelines
guidelines = client.get_merged_guidelines(context="backend")

# 4. Start session if needed
if not focus:
    client.start_session({
        "context": "backend",
        "current_focus": "signal generation",
        "goal": "Implement unified signal aggregation"
    })

# 5. Do your work...

# 6. Create checkpoint when changing focus
client.create_checkpoint({
    "summary": "Implemented signal clamping [33-85]",
    "next_focus": "Claude validation"
})
```

**Critical**: Always use relative paths: `./path/file.py` not `/absolute/path`

---

## Architecture Map

The system follows a **Progressive Disclosure** pattern:

### Layer 1: Minimal Core Context

Start here when first looking at a file:

- **Entry Point**: `main.py` — CLI interface
- **Orchestrator**: `ai_engine.py` — Signal pipeline coordination
- **Config**: `config.json` — Runtime parameters

### Layer 2: Domain-Specific Modules

Dig deeper based on what you're working on:

**Data Layer**: `mt5_fetcher.py`, `mt5_trader.py`
**Analysis Layer**: `indicators.py`, `signal_generator.py`, `lstm_model.py`
**Fusion Layer**: `multi_timeframe.py`, `news_sentiment.py`
**AI Layer**: `claude_ai.py`, `ai_engine.py`
**Risk Layer**: `risk/risk_manager.py`
**Output Layer**: `mt5_trader.py`, `metrics_server.py`

### Layer 3: Advanced References

Pull in as needed:

- **Testing**: See TESTING-PATTERNS.md
- **Patterns**: See PATTERNS-REFERENCE.md
- **Contracts**: See CONTRACT-REFERENCE.md
- **Session Workflow**: See SESSION-WORKFLOW.md

---

## Key Concepts

### Signal Confidence

- **Range**: Always `[33, 85]` (clamped)
- **Why**: Risk control—neither extreme certainty nor extreme doubt
- **Live Threshold**: `70` minimum for execution (configurable)
- **Do Not**: Override clamping logic

```python
# Example
result = generate_signal(df)
assert 33 <= result.confidence <= 85, "Confidence out of bounds!"
```

### Market Regime

Enum from `strategy/signal_generator.py`:

- `TRENDING_UP` — Price moving up steadily
- `TRENDING_DOWN` — Price moving down steadily
- `RANGING` — Oscillating in a range

Affects signal interpretation and weighting.

### Graceful Degradation

When optional dependencies fail, system continues:

```python
# Example: MT5 fallback
try:
    data = mt5.fetch(symbol, timeframe, count)
except:
    log.warning("MT5 unavailable, using synthetic data")
    data = _synthetic_rates(symbol, timeframe, count)  # Fallback
```

**Implement this pattern** for:

- MetaTrader5 → Synthetic OHLCV
- TensorFlow → NaiveSequenceModel
- Claude API → Skip validation
- NewsAPI → Neutral sentiment (0.0)

### Relative Paths (CRITICAL)

All file references must use `./` prefix:

```python
# CORRECT
import_data("./data/sample.csv")
load_config("./config.json")

# WRONG (breaks on different systems)
import_data("/Users/name/project/data/sample.csv")
load_config("C:\\Users\\name\\project\\config.json")
```

---

## Dataclass Pattern

Return structured types using `@dataclass`:

```python
from dataclasses import dataclass

@dataclass
class SignalResult:
    signal: str          # "BUY", "SELL", "HOLD"
    confidence: float    # [33, 85]
    regime: str          # "TRENDING_UP", "TRENDING_DOWN", "RANGING"
    reason: str          # Explanation

# Usage
result = generate_signal(df)
print(result.signal, result.confidence, result.regime)
```

See existing patterns:

- `SignalResult` (signal_generator.py)
- `EngineConfig` (ai_engine.py)
- `RiskContext` (risk/risk_manager.py)

---

## Logging Pattern

Use `core/logger.py` everywhere:

```python
from core.logger import get_logger

log = get_logger(__name__)

# Log with context
log.info("Signal generated", extra={"confidence": 0.75, "symbol": "EURUSD"})
log.warning("Daily loss limit approaching")
log.error("Claude API failed, skipping validation", exc_info=True)

# NEVER do this in production:
print("Signal generated")  # ❌ NO
```

---

## Testing Pattern

Use fixtures from `tests/conftest.py`:

```python
import pytest
from tests.conftest import sample_ohlcv

def test_signal_generation(sample_ohlcv):
    """Test signal gen with deterministic 260-bar data (seed=123)."""
    result = generate_signal(sample_ohlcv)
    assert 33 <= result.confidence <= 85
    assert result.signal in ["BUY", "SELL", "HOLD"]
    assert result.regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING"]

# Run:
# python -m pytest tests/test_signal_generator.py -v
```

---

## Type Hints (Required)

Always add full type hints:

```python
from __future__ import annotations  # Required at top!
import pandas as pd
from typing import Optional, List
from signal_generator import SignalResult

def analyze(df: pd.DataFrame, symbol: str) -> Optional[SignalResult]:
    """Analyze data and return signal or None if insufficient data."""
    if len(df) < 50:
        return None

    # ... analysis logic ...
    return SignalResult(signal="BUY", confidence=0.72, regime="TRENDING_UP", reason="...")
```

Check types: `python -m mypy .`

---

## Anti-Patterns to Avoid

| Anti-Pattern                  | Problem                      | Solution                       |
| ----------------------------- | ---------------------------- | ------------------------------ |
| Bare `print()` statements     | No control, hard to suppress | Use `core/logger.py`           |
| Hard-coded paths              | Breaks on different systems  | Use relative `./path`          |
| Windows backslashes           | Fails on Unix                | Always use `/`                 |
| No fallbacks                  | Crashes when dep fails       | Implement graceful degradation |
| Overriding confidence clamp   | Risk control bypassed        | Never touch `[33, 85]` bounds  |
| Enabling autotrade by default | Accidental live trading      | Keep `enabled: false`          |
| Direct print debugging        | Clutters output              | Use logger with levels         |
| No return type hints          | Type safety lost             | Use full `-> Type` hints       |
| Inline magic numbers          | Hard to maintain             | Extract to constants           |
| Long functions                | Hard to test                 | Keep functions < 30 lines      |

---

## File Organization: Where to Add What

### Signal Generation

- `signal_generator.py` — BUY/SELL/HOLD logic
- `multi_timeframe.py` — M1/M5/H1 fusion
- `strategy/signal_generator.py` — Regime-aware logic
- `claude_ai.py` — Claude validation

### Data Fetching

- `mt5_fetcher.py` — MT5 connection + fallback
- `data/fetch.py` — Generic utilities
- `news_sentiment.py` — External data sources

### Order Execution

- `mt5_trader.py` — MT5 order placement
- `risk/risk_manager.py` — Pre-trade gates
- `calculator.py` — Position sizing

### Analysis & Indicators

- `indicators.py` — Base indicators
- `strategy/indicators.py` — Advanced indicators
- `lstm_model.py` — Price prediction

### Testing

- `tests/conftest.py` — Shared fixtures
- `tests/test_*.py` — Test modules

### Configuration

- `config.json` — Runtime params
- `core/config.py` — Constants
- `profiles/*.json` — Profile variants

---

## Workflow Template: From Start to Commit

### 1. Identify Context

```bash
identify_context({ file_path: "./signal_generator.py" })
```

### 2. Start Session

```bash
start_session({
    "context": "backend",
    "current_focus": "signal generation",
    "goal": "Add regime-aware weighting"
})
```

### 3. Load Guidelines

```bash
get_merged_guidelines({ context: "backend" })
```

### 4. Implement (with Testing)

```bash
# Edit files
# python -m pytest tests/ -v  # test as you go
# python -m black .            # format
# python -m mypy .             # type check
```

### 5. Checkpoint Progress

```bash
create_checkpoint({
    "summary": "Added MarketRegime enum and regime weighting to signal gen",
    "next_focus": "Claude AI integration"
})
```

### 6. Commit

```bash
git add .
git commit -m "feat(signal): add regime-aware weighting for TRENDING_UP/DOWN/RANGING"
```

### 7. Complete Session

```bash
complete_session()
```

---

## Common Patterns Reference

See detailed workflow files for each pattern:

- **Signal Generation**: SESSION-WORKFLOW.md → Signal Generation section
- **Data Fetching**: SESSION-WORKFLOW.md → Data Fetching section
- **Risk Gates**: SESSION-WORKFLOW.md → Risk Management section
- **Testing**: TESTING-PATTERNS.md
- **Error Handling**: PATTERNS-REFERENCE.md → Graceful Degradation section
- **Configuration**: SESSION-WORKFLOW.md → Configuration section

---

## Performance Considerations

- **MT5 Polling**: Rate-limited by `rate_limiter.py` (token-bucket)
- **LSTM Training**: 2 epochs default, configurable in `config.json`
- **Signal Freshness**: M1 updates every minute; M5 every 5 minutes
- **Metrics Export**: Prometheus scrape interval (typically 15s)
- **Docker Resources**: See `docker-compose.yml` for CPU/memory limits

---

## Deployment Targets

| Target             | Config                 | See                         |
| ------------------ | ---------------------- | --------------------------- |
| **Local Dev**      | `config.json` + `.env` | AGENTS.md → Dev Environment |
| **Docker Local**   | `docker-compose.yml`   | `docker-compose up app`     |
| **Kubernetes**     | `k8s/` manifests       | DEPLOYMENT_GUIDE.md         |
| **GitHub Actions** | `.github/workflows/`   | CI/CD section               |

---

## References to Detailed Workflows

| File                        | Purpose                              | When to Read                 |
| --------------------------- | ------------------------------------ | ---------------------------- |
| `SESSION-WORKFLOW.md`       | Step-by-step MCP workflow + examples | When starting a work session |
| `CONTRACT-REFERENCE.md`     | Critical interfaces & validation     | When adding new modules      |
| `PATTERNS-REFERENCE.md`     | Code patterns used in project        | When implementing features   |
| `DOCUMENTATION-WORKFLOW.md` | Rules for writing docs               | When updating documentation  |
| `TESTING-PATTERNS.md`       | Test structure & pytest patterns     | When writing tests           |

---

## Next Steps

1. **Start a session**: `start_session(...)` with your goal
2. **Check the checklist**: See QUICK-REFERENCE.md
3. **Pick a task**: Signal gen? Data fetch? Risk gates?
4. **Read the workflow**: Find it in PATTERNS-REFERENCE.md or SESSION-WORKFLOW.md
5. **Follow the pattern**: Implement, test, commit
6. **Save progress**: `create_checkpoint(...)` when done

---

**Remember**: Context is finite. Use progressive disclosure. If a file is over 500 lines, break it into domain-specific files and reference them from the main SKILL.md.
