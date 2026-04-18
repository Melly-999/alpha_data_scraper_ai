# AGENTS.md – Alpha AI Trading Terminal

Agent guidance for the `alpha_data_scraper_ai` project. Use this as your primary reference when working on this codebase.

---

## Project Overview

**Alpha AI** is a production-ready algorithmic trading terminal combining:
- **MT5/Multi-Broker Integration** (XTB, IBKR, Alpaca)
- **Technical Analysis** (RSI, Stoch, MACD, Bollinger Bands, ADX, OBV, VWAP, ATR)
- **LSTM Price Prediction** (sequence-to-sequence time-series forecasting)
- **Multi-Timeframe Signal Fusion** (M1/M5/H1 weighted decision)
- **Claude AI Validation** (final signal confirmation via Anthropic API)
- **Risk Gates** (pre-trade filters, position sizing, daily loss caps)
- **Automated Reporting** (daily, weekly, monthly analysis reports)

**Safety Default**: Auto-trading is **disabled** by default; `dry_run: true`. Never enable live trading without explicit user instruction.

---

## Quick MCP Workflow

Before any work session, establish context:

```bash
# 1. Identify your current context (relative path required!)
identify_context({ file_path: "./ai_engine.py" })

# 2. Get current focus (or start new session)
get_current_focus()  # or  start_session({ context: "backend", current_focus: "signal generation" })

# 3. Load merged guidelines for your context
get_merged_guidelines({ context: "backend" })

# 4. [Do your work]

# 5. Save progress when changing direction
create_checkpoint({ summary: "Implemented unified signal aggregation", next_focus: "risk gates" })

# 6. When done
complete_session()
```

⚠️ **CRITICAL**: Use relative paths in all MCP tool calls: `./src/file.ts` not `/Users/name/project/src/file.ts`

---

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGNAL PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MT5 Data        Technical          LSTM           Signal   │
│  (or Synthetic)  Indicators         Prediction     Gen      │
│  │               │                  │              │        │
│  └─ mt5_fetcher  ├─ indicators      ├─ lstm_model  ├─ BUY   │
│  └─ mt5_trader   ├─ strategy/       └─ sequence    ├─ SELL  │
│                  │    indicators        model      ├─ HOLD  │
│                  └─ strategy/           (ML)       │ [33-85]│
│                      signal_gen                    │        │
│                                                     │        │
│                    ┌──────────────────────────────┘         │
│                    │                                         │
│         Multi-Timeframe Fusion (M1/M5/H1)                   │
│         multi_timeframe.py → weighted blend                 │
│                    │                                         │
│                    ▼                                         │
│         ┌──────────────────────┐                            │
│         │  News Sentiment      │                            │
│         │  news_sentiment.py   │                            │
│         │  (ForexFactory,      │                            │
│         │   NewsAPI)           │                            │
│         └──────────────────────┘                            │
│                    │                                         │
│                    ▼                                         │
│         ┌──────────────────────┐                            │
│         │  Claude AI Engine    │  ◄── Anthropic API         │
│         │  ai_engine.py        │  ◄── claude_ai.py          │
│         │  claude_ai.py        │     (Signal validation)    │
│         │  (UnifiedSignal)     │                            │
│         └──────────────────────┘                            │
│                    │                                         │
│                    ▼                                         │
│         ┌──────────────────────┐                            │
│         │  Risk Manager        │                            │
│         │  risk_manager.py     │                            │
│         │  (Pre-trade gates)   │                            │
│         └──────────────────────┘                            │
│                    │                                         │
│                    ▼                                         │
│         ┌──────────────────────┐                            │
│         │  MT5 Executor        │                            │
│         │  mt5_trader.py       │                            │
│         │  dry_run: true       │◄── Safety default          │
│         └──────────────────────┘                            │
│                    │                                         │
│                    ▼                                         │
│    Order Execution / Dry-Run Log                            │
│    metrics_server.py (Prometheus)                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Dev Environment Setup

### Installation (Full Stack)

```bash
# 1. Install all dependencies (includes MT5, TensorFlow, etc.)
pip install -r requirements.txt

# 2. Install pre-commit hooks (black, flake8, mypy)
pre-commit install

# 3. Setup environment (copy template)
cp .env.example .env
# EDIT .env - set CLAUDE_API_KEY, MT5 credentials
```

### Installation (CI-Minimal)

```bash
# For CI/CD (no MT5, TensorFlow) - used in GitHub Actions
pip install -r requirements-ci.txt
```

### Development Commands

```bash
# Format code
python -m black .

# Lint
python -m flake8 .

# Type check
python -m mypy .

# All checks (pre-commit)
pre-commit run --all-files

# Run all tests
python -m pytest -q
./run_tests.ps1      # Windows
./run_tests.sh       # Linux/Mac

# With coverage
python -m pytest --cov=. --cov-report=html

# Run the bot (dry-run, default)
python main.py
python main.py --symbol EURUSD GBPUSD --continuous --interval 60

# Full pipeline demo
python example_runner.py

# Backtesting
python -c "from backtest import BacktestEngine; ..."

# CPU profiling
python profiling/profile_cpu.py

# Memory profiling
python profiling/profile_memory.py
```

### Docker

```bash
# Run bot in Docker (24/7)
docker-compose up app

# Run tests in container
docker-compose up tests

# Dev shell
docker-compose up dev

# Build all images
./docker-build.sh

# Monitoring (Prometheus + Grafana)
docker-compose -f monitoring/docker-compose.monitoring.yml up
```

### Kubernetes (Production)

```bash
# Apply manifests (assumes cluster + credentials)
kubectl apply -f k8s/

# Port-forward monitoring
kubectl port-forward -n alpha-ai svc/prometheus 9090:9090
kubectl port-forward -n alpha-ai svc/grafana 3000:3000
```

---

## Code Conventions

| Convention | Rule | Example |
|---|---|---|
| **Formatter** | black, line length 88 | `python -m black .` |
| **Linter** | flake8 (E203, W503 ignored) | `python -m flake8 .` |
| **Types** | Full mypy checks | `from __future__ import annotations` |
| **Names** | PascalCase (classes), snake_case (functions/vars) | `class SignalResult`, `def generate_signal()` |
| **Constants** | UPPER_SNAKE_CASE | `CONFIDENCE_MIN = 33` |
| **Privates** | _leading_underscore | `def _synthetic_rates()` |
| **Dataclasses** | Use @dataclass for return types | `SignalResult`, `EngineConfig`, `RiskContext` |
| **Logging** | Use `core/logger.py`, never bare print() | `log = get_logger(__name__)` |
| **Paths** | Forward slashes only | `./src/handler.ts` (never `\`) |
| **Imports** | `from __future__ import annotations` at top | Required for type hints |
| **Error Handling** | Graceful degradation + fallbacks | MT5 → synthetic; TF → NaiveModel; Claude → local |

---

## Key Classes & Contracts

| Class | File | Purpose | Key Methods |
|---|---|---|---|
| `AIEngine` | `ai_engine.py` | Central orchestrator | `generate_signal(symbol)` |
| `EngineConfig` | `ai_engine.py` | Configuration (dataclass) | N/A (config holder) |
| `UnifiedSignal` | `ai_engine.py` | Final validated signal | `signal`, `confidence`, `regime` |
| `ClaudeAIClient` | `claude_ai.py` | Anthropic API wrapper | `get_signal(context)` |
| `ClaudeSignal` | `claude_ai.py` | Claude response (dataclass) | `is_valid`, `recommendation` |
| `LSTMPipeline` | `lstm_model.py` | Time-series prediction | `train(df)`, `predict(df)` |
| `MultiTimeframeAnalyzer` | `multi_timeframe.py` | M1/M5/H1 fusion | `analyze(symbol)` |
| `SentimentAnalyzer` | `news_sentiment.py` | Sentiment scoring | `get_sentiment(symbol)` |
| `SignalResult` | `signal_generator.py` | Raw signal (dataclass) | `signal`, `confidence`, `regime` |
| `MarketRegime` | `strategy/signal_generator.py` | Enum: TRENDING_UP/DOWN, RANGING | N/A (enum) |
| `RiskManager` | `risk/risk_manager.py` | Pre-trade validation | `check(signal, context)` |
| `RiskContext` | `risk/risk_manager.py` | Risk parameters (dataclass) | `daily_loss_cap`, `max_open_pos` |
| `MT5AutoTrader` | `mt5_trader.py` | Order execution | `execute(signal)` |
| `BacktestEngine` | `backtest.py` | Historical replay | `run(df)` → `BacktestMetrics` |
| `TradingBotMetrics` | `metrics_server.py` | Prometheus exporter | `gauge()`, `counter()` |

**Critical Rule**: Confidence is always clamped to `[33, 85]`. Minimum gate for live execution: `70` (configurable in `config.json`).

---

## Configuration

Primary file: `config.json`

```json
{
  "symbol": "EURUSD",
  "timeframe": "M5",
  "bars": 700,
  "autotrade": {
    "enabled": false,        // ⚠️ NEVER true without explicit user instruction
    "dry_run": true,         // ✅ Keep true unless user explicitly disables
    "min_confidence": 0.70
  }
}
```

**Profile-Based Switching**:
- `./profiles/paper_safe.json` — dry_run: true (safe testing)
- `./profiles/real_conservative.json` — live, lower risk
- `./profiles/real_aggressive.json` — live, higher risk

Use profiles to switch modes:
```bash
python main.py --profile profiles/real_conservative.json
```

---

## File Organization

### Root-Level Entry Points
- `main.py` — CLI interface, argument parsing
- `example_runner.py` — Full pipeline demonstration
- `grok_alpha_advanced.py` — Legacy GUI terminal

### Core Logic (Root)
- `ai_engine.py` — Signal orchestration + Claude integration
- `claude_ai.py` — Anthropic client wrapper
- `mt5_fetcher.py` — Data fetching (MT5 or fallback synthetic)
- `mt5_trader.py` — Order execution (dry-run + live)
- `lstm_model.py` — Sequence prediction model
- `indicators.py` — Base technical indicators
- `signal_generator.py` — BUY/SELL/HOLD generation
- `multi_timeframe.py` — M1/M5/H1 weighted fusion
- `news_sentiment.py` — ForexFactory + NewsAPI sentiment
- `calculator.py` — Position sizing
- `rate_limiter.py` — Token-bucket rate limiting
- `metrics_server.py` — Prometheus metrics exporter
- `backtest.py` — Backtesting engine
- `secrets_manager.py` — Environment & secrets loading
- `gui.py` — Console rendering

### Subdirectories
- `./strategy/` — Advanced indicators (ADX, OBV, VWAP, ATR) + regime-aware signal gen
- `./ai/` — Modular ML implementations
- `./core/` — Logging, config constants
- `./risk/` — Risk gates, position sizing validation
- `./data/` — Data fetching utilities
- `./brokers/` — Adapter pattern for XTB, IBKR, Alpaca
- `./tests/` — pytest fixtures + test suite (260-bar seed=123)
- `./profiles/` — JSON trading config profiles
- `./monitoring/` — Prometheus + Grafana configs
- `./k8s/` — Kubernetes manifests
- `./profiling/` — CPU/memory profiling scripts
- `./docs/` — Markdown documentation
- `./.github/workflows/` — CI/CD (pytest, docker, k8s, security)

---

## Safety Rules for Agents

1. **Never enable auto-trading** (`autotrade.enabled: true`) without explicit user instruction in current session
2. **Keep dry_run: true** unless user explicitly disables
3. **Preserve confidence clamping** `[33, 85]` and min_confidence gate (70) — these are risk controls
4. **Do not remove fallbacks** for MT5, TensorFlow, Claude, NewsAPI
5. **Always use relative paths** in all references (e.g., `./src/file.py` not `/abs/path`)
6. **Run tests before committing**: `python -m pytest -q` must pass
7. **Format before committing**: `black . && flake8 .` must pass
8. **Never commit secrets** (API keys, credentials) — use `.env` files (git-ignored)
9. **Use `core/logger.py`** for all logging — never bare `print()` in production code
10. **Dataclasses for return types** — follow existing pattern for structured outputs

---

## Testing & CI/CD

### Local Testing
```bash
# Run all tests
python -m pytest -q

# Run specific test file
python -m pytest tests/test_indicators.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Match a test pattern
python -m pytest -k "signal" -v
```

### Fixtures (pytest)
All tests use shared fixtures from `tests/conftest.py`:
- `sample_ohlcv` — 260-bar OHLCV DataFrame (seed=123, deterministic)

### CI/CD Workflows (GitHub Actions)
- `.github/workflows/pytest.yml` — Tests, black, flake8, mypy
- `.github/workflows/docker.yml` — Build + push Docker images
- `.github/workflows/deploy-k8s.yml` — Apply Kubernetes manifests
- `.github/workflows/security.yml` — Dependency security scan

### CI Requirements
- Install `requirements-ci.txt` (no MT5/TensorFlow)
- All tests must pass
- `black .` and `flake8 .` must have no errors
- `mypy .` must have no errors

---

## Graceful Degradation Map

The system has fallbacks for all optional dependencies:

| Dependency | Fallback | Used When |
|---|---|---|
| **MetaTrader5** | Synthetic OHLCV (seeded random) | MT5 unavailable |
| **TensorFlow/LSTM** | NaiveSequenceModel (last-value) | TF unavailable |
| **Claude AI** | Skip validation, use local confidence | Claude API fails |
| **NewsAPI / ForexFactory** | Skip sentiment (neutral = 0.0) | News APIs unavailable |

---

## Secrets & Environment

Managed by `secrets_manager.py`. Set in environment or `.env` (git-ignored):

```bash
CLAUDE_API_KEY=sk-ant-...        # Anthropic
NEWSAPI_KEY=...                  # NewsAPI.org
MT5_LOGIN=...                    # MT5 account
MT5_PASSWORD=...                 # MT5 password
MT5_SERVER=...                   # MT5 broker server
```

⚠️ **Never commit `.env` files or credentials to repository.**

---

## Advanced References

- **MCP Workflow Integration**: See `.ai-agents/skills/SESSION-WORKFLOW.md`
- **Code Patterns**: See `.ai-agents/skills/PATTERNS-REFERENCE.md`
- **Contracts & Interfaces**: See `.ai-agents/skills/CONTRACT-REFERENCE.md`
- **Documentation Rules**: See `.ai-agents/skills/DOCUMENTATION-WORKFLOW.md`
- **Quick Checklist**: See `.ai-agents/QUICK-REFERENCE.md`

---

## Branch & PR Guidelines

- **Branch name**: `claude/feature-name` or `feature/name` (never push directly to main)
- **PR title format**: `[feature|fix|docs|test] Brief description`
- **Commit format**: Descriptive messages, conventional commits preferred
- **Before PR**: Run `black .`, `flake8 .`, `mypy .`, `pytest -q`
- **PR checks**: CI must pass (tests, linting, types, security)

---

## Useful Links

- [CLAUDE.md](./CLAUDE.md) — Original AI assistant guidance
- [README.md](./README.md) — Polish-language project intro
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) — Production deployment
- [GITHUB_INTEGRATION_QUICK_START.md](./GITHUB_INTEGRATION_QUICK_START.md) — GitHub setup
- [Anthropic Claude Docs](https://docs.anthropic.com) — Claude API reference
- [MetaTrader5 Docs](https://www.mql5.com/en/docs/integration/python_metatrader5) — MT5 Python binding

---

**Last Updated**: April 2026  
**Agent-Focused Context**: See `.ai-agents/` directory for detailed reference guides
