# CLAUDE.md — Alpha AI Trading Bot

AI assistant guidance for the `alpha_data_scraper_ai` repository.

---

## Project Overview

**Alpha AI** is a modular, production-ready algorithmic trading terminal built on MetaTrader5 (MT5). It combines technical analysis, LSTM price prediction, multi-timeframe signal fusion, news sentiment, and Claude AI validation into a single pipeline — with full risk gates, dry-run defaults, and Docker/K8s infrastructure.

**Default safety posture**: auto-trading is disabled and dry-run is on. Never change these defaults without explicit user instruction.

---

## Repository Layout

```
alpha_data_scraper_ai/
├── main.py                     # Primary CLI entry point
├── ai_engine.py                # Central AI orchestrator (AIEngine, EngineConfig, UnifiedSignal)
├── claude_ai.py                # Anthropic Claude API client (ClaudeAIClient, ClaudeSignal)
├── example_runner.py           # Full pipeline demonstration
├── grok_alpha_advanced.py      # Advanced GUI-based trading terminal (legacy)
│
├── mt5_fetcher.py              # OHLCV data from MT5 or synthetic fallback
├── mt5_trader.py               # Order execution (dry-run + live, MT5AutoTrader)
├── multi_timeframe.py          # M1/M5/H1 weighted signal fusion
├── news_sentiment.py           # ForexFactory scraping + NewsAPI sentiment
│
├── indicators.py               # Base indicators: RSI, Stoch, MACD, Bollinger Bands
├── signal_generator.py         # BUY/SELL/HOLD signal generation (SignalResult)
├── lstm_model.py               # LSTM pipeline for price prediction (LSTMPipeline)
├── calculator.py               # Position sizing (position_size())
├── rate_limiter.py             # Token-bucket rate limiter
├── secrets_manager.py          # Secrets loading from env/files
├── metrics_server.py           # Prometheus exporter (TradingBotMetrics)
├── backtest.py                 # BacktestEngine, BacktestMetrics, Trade
├── gui.py                      # Console + Tkinter rendering
│
├── strategy/                   # Advanced indicators and signals
│   ├── indicators.py           # ADX, OBV, VWAP, ATR
│   ├── signal_generator.py     # Regime-aware signal gen (MarketRegime)
│   └── signals.py              # Additional signal utilities
├── ai/
│   └── lstm_model.py           # Modular LSTM implementation
├── core/
│   ├── config.py               # Central constants and paths
│   └── logger.py               # Rotating file + console logging
├── risk/
│   └── risk_manager.py         # Pre-trade gates, position sizing (RiskManager, RiskContext)
├── data/
│   └── fetch.py                # Generic data fetching utilities
│
├── tests/
│   ├── conftest.py             # pytest fixtures (260-bar OHLCV, seed=123)
│   ├── test_indicators.py
│   ├── test_signal_generator.py
│   ├── test_signal_generator_unit.py
│   ├── test_lstm_model.py
│   ├── test_calculator.py
│   ├── test_integration_pipeline.py
│   ├── test_integration_gui_pipeline.py
│   ├── test_integration_advanced.py
│   └── test_stress_extended.py
│
├── profiles/                   # Trading config profiles
│   ├── paper_safe.json         # dry_run: true
│   ├── real_conservative.json  # live, lower risk
│   └── real_aggressive.json    # live, higher risk
├── backtest/                   # Backtesting sub-package
├── monitoring/                 # Prometheus + Grafana configs
├── k8s/                        # Kubernetes manifests
├── profiling/                  # CPU/memory profiling scripts
├── .github/workflows/          # CI/CD: pytest, docker, k8s, security
│
├── config.json                 # Default runtime config (symbol, timeframe, autotrade gates)
├── requirements.txt            # Full runtime dependencies
├── requirements-ci.txt         # Minimal CI dependencies (no MT5/tensorflow)
├── Dockerfile / Dockerfile.prod
├── docker-compose.yml
├── .flake8                     # line-length=88, ignores E203/W503
├── mypy.ini                    # Python 3.12, ignore_missing_imports=True
└── .pre-commit-config.yaml     # black, flake8, mypy hooks
```

---

## Data Flow

```
MT5 API (or Synthetic fallback)
    ↓  batch_fetch()
OHLCV DataFrame
    ↓  add_indicators()
RSI / Stoch / MACD / BB / ADX / OBV / VWAP / ATR
    ↓  LSTMPipeline.predict()
Price delta + uncertainty
    ↓  generate_signal()
SignalResult (BUY/SELL/HOLD, confidence 33–85%, MarketRegime)
    ↓  MultiTimeframeAnalyzer
Weighted M1/M5/H1 fusion
    ↓  SentimentAnalyzer
News sentiment overlay
    ↓  AIEngine → ClaudeAIClient
UnifiedSignal with Claude validation
    ↓  RiskManager
Pre-trade gates (min 70% confidence, daily loss cap, open position cap)
    ↓  MT5AutoTrader (dry_run=True by default)
Order execution / dry-run log
    ↓  BacktestEngine
Historical performance metrics
```

---

## Key Classes and Contracts

| Class | File | Key Methods |
|---|---|---|
| `AIEngine` | `ai_engine.py` | `generate_signal(symbol)` |
| `EngineConfig` | `ai_engine.py` | dataclass — confidence thresholds, API keys |
| `ClaudeAIClient` | `claude_ai.py` | `get_signal(context)` |
| `LSTMPipeline` | `lstm_model.py` | `train(df)`, `predict(df)` |
| `MultiTimeframeAnalyzer` | `multi_timeframe.py` | `analyze(symbol)` |
| `SentimentAnalyzer` | `news_sentiment.py` | `get_sentiment(symbol)` |
| `SignalResult` | `signal_generator.py` | dataclass — `signal`, `confidence`, `regime` |
| `MarketRegime` | `strategy/signal_generator.py` | `TRENDING_UP`, `TRENDING_DOWN`, `RANGING` |
| `RiskManager` | `risk/risk_manager.py` | `check(signal, context)` |
| `MT5AutoTrader` | `mt5_trader.py` | `execute(signal)` |
| `BacktestEngine` | `backtest.py` | `run(df)` → `BacktestMetrics` |
| `TradingBotMetrics` | `metrics_server.py` | Prometheus gauge/counter updates |

Signal confidence is always clamped to `[33, 85]`. The minimum confidence gate for live trade execution is `70` (configurable in `config.json`).

---

## Development Commands

```bash
# Install dependencies (full)
pip install -r requirements.txt

# Install minimal (CI-compatible, no MT5/tensorflow)
pip install -r requirements-ci.txt

# Format / lint / type-check
python -m black .
python -m flake8 .
python -m mypy .

# Pre-commit (runs black + flake8 + mypy on staged files)
pre-commit install
pre-commit run --all-files

# Run all tests
python -m pytest -q
./run_tests.sh          # Linux/Mac
.\run_tests.ps1 -q      # Windows

# Tests with coverage report
python -m pytest --cov=. --cov-report=html

# Run the bot (dry-run by default)
python main.py
python main.py --symbol EURUSD GBPUSD --continuous --interval 60

# Full pipeline demo
python example_runner.py

# Profiling
python profiling/profile_cpu.py
python profiling/profile_memory.py
```

### Docker

```bash
docker-compose up app          # Run bot
docker-compose up tests        # Run tests
docker-compose up dev          # Dev shell
./docker-build.sh              # Build images

# Monitoring stack (Prometheus + Grafana)
docker-compose -f monitoring/docker-compose.monitoring.yml up
```

---

## Configuration

`config.json` is the primary runtime config. Key fields:

```jsonc
{
  "symbol": "EURUSD",
  "timeframe": "M5",
  "bars": 700,
  "autotrade": {
    "enabled": false,       // NEVER enable without explicit user instruction
    "dry_run": true,        // Keep true unless user explicitly disables
    "min_confidence": 0.70
  }
}
```

Use profile files to switch trading modes:
- `profiles/paper_safe.json` — safe paper trading (default for dev)
- `profiles/real_conservative.json` — live, conservative
- `profiles/real_aggressive.json` — live, aggressive

---

## Coding Conventions

- **Formatter**: `black`, line length 88
- **Linter**: `flake8` (ignores E203, W503)
- **Types**: Full type hints, `mypy`-checked with `ignore_missing_imports = True`
- **Forward references**: Use `from __future__ import annotations` at top of file
- **Naming**:
  - Classes → `PascalCase`
  - Functions/variables → `snake_case`
  - Constants → `UPPER_SNAKE_CASE`
  - Private helpers → `_leading_underscore`
- **Dataclasses**: Prefer `@dataclass` for structured return types and configuration objects (see `SignalResult`, `EngineConfig`, `RiskContext`, `Trade`)
- **Logging**: Use `core/logger.py` (`get_logger(__name__)`), never `print()` in production code
- **Error handling**: Graceful degradation with logging — wrap optional dependencies (MT5, TensorFlow, Claude) in try/except; provide fallbacks

---

## Testing Guidelines

- Test framework: `pytest`
- Shared fixtures in `tests/conftest.py` — use `sample_ohlcv` (260-bar DataFrame, `seed=123`) for deterministic tests
- CI uses `requirements-ci.txt` — do not add tests that require `MetaTrader5` or `tensorflow` without a fallback/skip
- Confidence bounds: always assert `33 <= confidence <= 85` in signal tests
- New features require corresponding tests; integration tests preferred for pipeline changes
- Run `pytest -q` before committing

---

## Environment Variables / Secrets

Loaded by `secrets_manager.py`. Set in environment or Docker secrets:

| Variable | Purpose |
|---|---|
| `CLAUDE_API_KEY` | Anthropic Claude API key |
| `NEWSAPI_KEY` | NewsAPI.org key for sentiment |
| `MT5_LOGIN` | MT5 account login |
| `MT5_PASSWORD` | MT5 account password |
| `MT5_SERVER` | MT5 broker server address |

Never commit secrets to the repository. Use `.env` files locally (git-ignored).

---

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|---|---|---|
| `pytest.yml` | push/PR to main | Tests, black, flake8, mypy |
| `docker.yml` | push to main | Build + push Docker images |
| `deploy-k8s.yml` | push to main | Apply Kubernetes manifests |
| `security.yml` | scheduled | Dependency security scan |

CI installs `requirements-ci.txt` (no heavy ML/MT5 deps). All tests must pass before merging.

---

## Graceful Degradation Map

| Dependency | Fallback |
|---|---|
| MetaTrader5 | Synthetic OHLCV data (`_synthetic_rates()`, seeded random) |
| TensorFlow/LSTM | `NaiveSequenceModel` (last-value prediction) |
| Claude AI | Skip validation, use local signal confidence only |
| NewsAPI / ForexFactory | Skip sentiment, neutral score (0.0) |

---

## Safety Rules for AI Assistants

1. **Never enable live trading** (`autotrade.enabled: true` or `dry_run: false`) without explicit user instruction in the current session.
2. **Never commit or expose secrets** (API keys, MT5 credentials).
3. **Preserve confidence clamping** (`[33, 85]`) and the `min_confidence=70` gate — these are risk controls.
4. **Do not remove fallbacks** for optional dependencies (MT5, TF, Claude, NewsAPI).
5. **Run tests before pushing**: `python -m pytest -q` must pass.
6. **Format before committing**: `black .` and `flake8 .` must pass.
7. **Branch**: develop on `claude/add-claude-documentation-HCUMe`; never push directly to `main` without a PR.
8. **Use `core/logger.py`** for all logging — no bare `print()` in non-GUI production code.
9. **Dataclasses for return types**: follow the existing pattern for structured outputs.
10. **Minimal changes**: fix what was asked; do not refactor surrounding code or add unrequested features.
