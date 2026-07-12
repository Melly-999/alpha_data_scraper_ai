# Root Module Inventory

This inventory records the public repository hygiene audit for MELLYTRADE-GITHUB-CREDIBILITY-CLEANUP-001. It is intentionally conservative: root-level Python modules were not moved or refactored unless import/reference checks proved they were isolated artifacts.

## Public Demo Boundary

The public read-only demo is the FastAPI app under `app/`, the React + TypeScript + Vite frontend under `frontend/`, the Tauri thin shell under `frontend/src-tauri/`, and the safety/test/documentation evidence around those surfaces. Legacy CLI, MT5, backtest, and research modules can remain useful for local research, but they are not part of the public read-only demo surface.

Safety posture remains unchanged: `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, max risk per trade <= 1%, no live broker execution, no order placement controls, and stop-loss/take-profit requirements remain enforced in paper/simulation modules.

## Removed In This Cleanup

| Path | Classification | Evidence | Action |
|---|---|---|---|
| `.github/workflows/auto-commit-results.yml` | SAFE_TO_REMOVE | Scheduled workflow had `contents: write`, ran the trading bot, committed `results/` and `logs/`, then pushed to `main`. | Removed. |
| `.github/workflows/trade-signal-commit.yml` | SAFE_TO_REMOVE | Dispatch workflow had `contents: write`, committed signal JSON to `results/signals/`, pushed to `main`, and opened automatic signal issues. | Removed. |
| `github_integration.py` | SAFE_TO_REMOVE | Repository-wide search found no active runtime/test imports outside its own setup docs/snippet. The file implemented commit-and-push helpers for generated trading results. | Removed. |
| `GITHUB_INTEGRATION_SETUP.md` | SAFE_TO_REMOVE | Setup guide encouraged PAT/token setup, automatic commits, automatic pushes, and signal issues. | Removed. |
| `GITHUB_INTEGRATION_QUICK_START.md` | SAFE_TO_REMOVE | Quick start promoted auto-committing and pushing signals/results. | Removed. |
| `GITHUB_INTEGRATION_SNIPPET.py` | SAFE_TO_REMOVE | Snippet only referenced the removed integration module and was not imported by active runtime/tests. | Removed. |
| `.instructions.md` | SAFE_TO_REMOVE | Repository instructions promoted automatic signal/result commits, direct pushes to `main`, and signal issues using the removed integration. | Removed. |
| `alpha_data_scraper_ai_updated.zip` | SAFE_TO_REMOVE | Generated archive artifact tracked at repository root. | Removed. |
| `.venv/` | SAFE_TO_REMOVE | Local virtual environment content was tracked, including interpreter/pip executables and `pyvenv.cfg`. | Removed from the tracked tree. |

## Remaining Root Modules

| Path | Classification | Rationale / current handling |
|---|---|---|
| `main.py` | ACTIVE_TOOLING | Legacy CLI/research runner. It imports `mt5_trader.py`, `indicators.py`, `lstm_model.py`, `mt5_fetcher.py`, and signal utilities. It is not the public FastAPI demo entrypoint, but it is an active local tooling entrypoint and was not moved. |
| `app/main.py` | ACTIVE_RUNTIME | FastAPI read-only demo entrypoint used by the public API surface and safety tests. Not a root file, listed here as the runtime anchor. |
| `frontend/` | ACTIVE_RUNTIME | React + TypeScript + Vite public web/mobile terminal. Not a root file, listed here as the frontend anchor. |
| `frontend/src-tauri/` | ACTIVE_RUNTIME | Tauri thin shell for the hosted app. Not a root file, listed here as the desktop anchor. |
| `ai_engine.py` | LEGACY_RESEARCH | Root signal/portfolio orchestration using broker and Claude integration. No active public demo import found during this audit; retained for local research compatibility. |
| `claude_ai.py` | LEGACY_RESEARCH | Anthropic/Claude signal analysis wrapper used by legacy/research paths. Retained because root tooling references this family of modules. |
| `backtest.py` | LEGACY_RESEARCH | Historical replay engine. It models trades for research/backtesting and is not part of the public read-only demo. Retained. |
| `calculator.py` | LEGACY_RESEARCH | Fixed-risk position-sizing helper. Retained because deleting finance utilities without broader tests would be unnecessary risk. |
| `mt5_trader.py` | LEGACY_RESEARCH | MT5 execution wrapper with `enabled=False` and `dry_run=True` defaults; imported by `main.py`. Retained and not exposed as public demo runtime. |
| `grok_alpha_advanced.py` | LEGACY_RESEARCH | Large legacy desktop/GUI research terminal with MT5-oriented code. No active public demo import found; retained for review rather than broad deletion. |
| `example_runner.py` | ACTIVE_TOOLING | Local demonstration runner referenced by project guidance; retained. |
| `daily_analysis.py`, `weekly_analysis.py`, `monthly_dividend_report.py` | ACTIVE_TOOLING | Local reporting scripts; retained. |
| `execution_service.py` | UNKNOWN_REQUIRES_REVIEW | Root-level service predates the app package. Kept until a dedicated execution-surface audit can prove removal is safe. |
| `scheduler.py` | ACTIVE_TOOLING | Local scheduler script; retained. |
| `webhook_server.py` | UNKNOWN_REQUIRES_REVIEW | Legacy server-style root script; retained pending dedicated route/import audit. |
| `gui.py` | LEGACY_RESEARCH | Console rendering/live GUI helper used by root CLI flow. Retained. |
| `mt5_fetcher.py`, `indicators.py`, `lstm_model.py`, `multi_timeframe.py`, `news_sentiment.py`, `signal_generator.py` | LEGACY_RESEARCH | Legacy signal pipeline modules used by local CLI/research paths. Retained. |
| `metrics_server.py`, `notifications.py`, `rate_limiter.py`, `secrets_manager.py`, `drawdown_guard.py` | ACTIVE_TOOLING | Utility/support modules with potential local tooling usage. Retained. |
| `test_parser.py` | UNKNOWN_REQUIRES_REVIEW | Root-level test/helper script. Kept pending test layout cleanup. |

## Follow-Up Recommendations

- Split legacy CLI/research modules into a documented `legacy/` or `research/` package only after import, test, and docs coverage can prove the move is safe.
- Keep public demo work anchored on `app/main.py`, `frontend/`, `frontend/src-tauri/`, `tests/app/test_safety_invariants.py`, and `tests/app/test_openapi_forbidden_paths.py`.
- Do not reintroduce workflows that commit generated trading artifacts or push to `main`.
