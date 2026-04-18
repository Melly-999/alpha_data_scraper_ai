# QUICK-REFERENCE.md – Alpha AI Agent Checklist

**Condensed checklist** for every conversation (~400 tokens). Full details in AGENTS.md and skills/ directory.

---

## Every Session: 5-Step MCP Workflow

```bash
1. identify_context({ file_path: "./ai_engine.py" })           # Know WHERE you are
2. get_current_focus()  OR  start_session(...)                 # Know WHAT you're doing
3. get_merged_guidelines({ context: "backend" })               # Load RULES
4. [YOUR WORK HERE]
5. complete_session() or create_checkpoint()                   # Save PROGRESS
```

⚠️ **ALWAYS use relative paths**: `./path` not `/absolute/path`

---

## Core Rules (Non-Negotiable)

| Rule | Impact | Status |
|---|---|---|
| `autotrade.enabled` stays FALSE | Live trading requires explicit user permission | 🔴 CRITICAL |
| `dry_run: true` by default | All orders are paper-traded unless disabled | 🔴 CRITICAL |
| Confidence clamped `[33, 85]` | Risk control; never override | 🔴 CRITICAL |
| Min gate = 70% for live trade | Pre-trade filter; configurable | 🟡 IMPORTANT |
| Fallbacks for MT5/TF/Claude | Graceful degradation required | 🟡 IMPORTANT |
| Use `./core/logger.py` not print() | Production code must log properly | 🟡 IMPORTANT |
| Relative paths everywhere | Cross-platform compatibility | 🟡 IMPORTANT |

---

## Pre-Commit Checklist

```bash
✓ Format: python -m black .
✓ Lint: python -m flake8 .
✓ Types: python -m mypy .
✓ Tests: python -m pytest -q
✓ No secrets in code
✓ Dataclasses for return types
✓ All logging via core/logger.py
✓ Graceful fallbacks for optional deps
```

---

## Quick Reference: Key Files

| File | Purpose | When to Edit |
|---|---|---|
| `config.json` | Runtime configuration | Changing trading params |
| `ai_engine.py` | Signal orchestration | Adding signal sources or validation logic |
| `claude_ai.py` | Claude API integration | Claude prompt/parsing changes |
| `mt5_fetcher.py` | Data fetching | New data sources or indicators |
| `mt5_trader.py` | Order execution | Trading logic changes |
| `lstm_model.py` | Price prediction | ML model changes |
| `signal_generator.py` | BUY/SELL logic | Signal generation rules |
| `risk/risk_manager.py` | Pre-trade gates | Risk filter changes |
| `multi_timeframe.py` | Timeframe fusion | Weighting logic changes |
| `news_sentiment.py` | Sentiment analysis | Sentiment sources or parsing |
| `tests/conftest.py` | Test fixtures | Adding shared test data |

---

## Test Fixtures (pytest)

All tests use `conftest.py`:
- **sample_ohlcv** — 260-bar DataFrame, seed=123 (deterministic)

```python
def test_signal(sample_ohlcv):
    result = generate_signal(sample_ohlcv)
    assert 33 <= result.confidence <= 85
```

---

## Signal Pipeline Summary

```
MT5/Synthetic Data
  ↓
Technical Indicators (RSI, Stoch, MACD, BB, ADX, OBV, VWAP, ATR)
  ↓
LSTM Prediction (or NaiveModel if TF unavailable)
  ↓
SignalResult (BUY/SELL/HOLD, confidence [33-85])
  ↓
MultiTimeframe Fusion (M1/M5/H1 weighted)
  ↓
News Sentiment (or neutral if APIs unavailable)
  ↓
Claude AI Validation (or skip if Claude unavailable)
  ↓
RiskManager (gates: min 70%, daily loss cap, max open positions)
  ↓
MT5AutoTrader (execute if dry_run=false, else log)
```

---

## Graceful Degradation Quick Map

```
MetaTrader5 ──→ Synthetic OHLCV (seeded random)
TensorFlow  ──→ NaiveSequenceModel (last value)
Claude AI   ──→ Skip validation (use local confidence)
NewsAPI     ──→ Skip sentiment (neutral = 0.0)
```

---

## Development Commands (Copy-Paste Ready)

```bash
# Format
python -m black .

# Lint
python -m flake8 .

# Type check
python -m mypy .

# Test all
python -m pytest -q

# Test one file
python -m pytest tests/test_indicators.py -v

# Test with coverage
python -m pytest --cov=. --cov-report=html

# Run bot (dry-run)
python main.py

# Run with options
python main.py --symbol EURUSD GBPUSD --continuous --interval 60

# Demo pipeline
python example_runner.py

# Backtest
python -c "from backtest import BacktestEngine; ..."

# Docker dev
docker-compose up dev

# Kubernetes apply
kubectl apply -f k8s/
```

---

## Dataclass Pattern (Return Types)

Always use `@dataclass` for structured returns:

```python
from dataclasses import dataclass

@dataclass
class SignalResult:
    signal: str          # BUY, SELL, HOLD
    confidence: float    # [33, 85]
    regime: str          # TRENDING_UP, TRENDING_DOWN, RANGING
    reason: str          # Human-readable explanation

# Usage
result = generate_signal(df)
assert 33 <= result.confidence <= 85
```

Existing examples:
- `SignalResult` → signal_generator.py
- `EngineConfig` → ai_engine.py
- `UnifiedSignal` → ai_engine.py
- `RiskContext` → risk/risk_manager.py
- `ClaudeSignal` → claude_ai.py

---

## Logging Pattern

```python
from core.logger import get_logger

log = get_logger(__name__)

# Never use print() in production
log.info("Signal generated", extra={"confidence": 0.75})
log.warning("High loss today")
log.error("MT5 connection failed, using synthetic data")
```

---

## Type Hints (Required)

```python
from __future__ import annotations  # Required at top

def generate_signal(df: pd.DataFrame) -> SignalResult:
    """Generate signal with full type safety."""
    pass

# Optional typing
from typing import Optional, List, Dict

def fetch_data(symbol: str) -> Optional[pd.DataFrame]:
    pass
```

---

## Environment Variables

```bash
CLAUDE_API_KEY=sk-ant-...        # Anthropic
NEWSAPI_KEY=...                  # NewsAPI.org
MT5_LOGIN=12345                  # Account ID
MT5_PASSWORD=xxx                 # Password
MT5_SERVER=broker.server.com     # Broker endpoint
```

Set in `.env` (git-ignored) or Docker secrets.

---

## Safety Rule Enforcement Checklist

- [ ] `autotrade.enabled` not set to true without permission
- [ ] `dry_run: true` is the default
- [ ] Confidence clamped to [33, 85]
- [ ] Min confidence gate >= 70
- [ ] All fallbacks in place (MT5, TF, Claude, NewsAPI)
- [ ] No bare print() statements
- [ ] No secrets in code
- [ ] Relative paths used everywhere
- [ ] All tests pass
- [ ] Code formatted with black
- [ ] Type hints complete (mypy passes)

---

## More Details

- **Full AGENTS.md** — ./AGENTS.md (comprehensive guide)
- **Session Workflow** — ./.ai-agents/skills/SESSION-WORKFLOW.md
- **Code Patterns** — ./.ai-agents/skills/PATTERNS-REFERENCE.md
- **Contracts** — ./.ai-agents/skills/CONTRACT-REFERENCE.md
- **Documentation** — ./.ai-agents/skills/DOCUMENTATION-WORKFLOW.md

---

**When in doubt**: Check AGENTS.md or ask for clarification. Context is finite—use it wisely!
