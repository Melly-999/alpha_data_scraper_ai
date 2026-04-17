# MellyTrade v3 — operations notes

## Environment variables

### `mellytrade-api/.env`

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | yes | `sqlite:///./mellytrade.db` | Use Postgres for prod |
| `FASTAPI_KEY` | yes | — | Presented as `X-API-Key` header |
| `CF_HUB_URL` | no | — | Worker `/api/publish` endpoint |
| `CF_API_SECRET` | no | — | Sent as `X-Hub-Secret` |
| `COOLDOWN_SECONDS` | yes | `60` | Per-symbol cooldown |
| `MIN_CONFIDENCE` | yes | `70` | Minimum confidence to accept |
| `MAX_RISK_PERCENT` | yes | `1.0` | Hard cap on position risk |
| `ALPHA_REPO_PATH` | yes (bridge) | — | Absolute path to `alpha_data_scraper_ai` |
| `ALPHA_LSTM_CLASS` | no | `lstm_model.LSTMPipeline` | Class loaded by the adapter |
| `ALPHA_LSTM_FUNCTION` | no | — | Optional callable overriding the class |
| `ALPHA_LSTM_CHECKPOINT` | no | — | Optional path to a pre-trained checkpoint |
| `MT5_SYMBOL`, `MT5_TIMEFRAME`, `MT5_BARS` | no | `EURUSD`, `M5`, `300` | MT5 bridge fetch params |
| `MT5_SL_PIPS`, `MT5_TP_PIPS`, `MT5_RISK_PERCENT` | no | `20`, `40`, `0.5` | MT5 bridge trade sizing |
| `MELLYTRADE_API_URL` | no | `http://127.0.0.1:8000` | Where the bridge POSTs `/signal` |
| `CLOUDMCP_TOKEN` | no | — | Shared token for `.mcp.json` / `.cursor/mcp.json` |

### Worker secrets

```bash
wrangler secret put CF_API_SECRET
wrangler kv:namespace create SIGNALS   # replace ID in wrangler.toml
```

## Running the backend

```bash
cd mellytrade_v3/mellytrade-api
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q                              # 7 tests
uvicorn app.main:app --reload --port 8000
# If port 8000 is busy:
# uvicorn app.main:app --reload --port 8001
```

Smoke test:

```bash
curl -s http://127.0.0.1:8000/health | jq .

curl -s -X POST http://127.0.0.1:8000/signal \
  -H "X-API-Key: $FASTAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"EURUSD","action":"BUY","confidence":75,
       "risk_percent":0.5,"entry_price":1.1000,
       "stop_loss":1.0980,"take_profit":1.1040,"source":"manual"}' | jq .
```

## MT5 bridge

`mt5/mt5_bridge.py` fetches OHLCV (via `mt5_fetcher.MT5Fetcher` or an injected
fetcher for tests), calls `lstm_signal_adapter.predict_signal` with a real
DataFrame, and POSTs the result to `/signal`.

### Datasource requirements

The LSTM adapter expects a `pandas.DataFrame` with at least these
case-insensitive columns (in any order — the adapter normalises and
re-orders them so `close` sits at index 0):

- `close`, `open`, `high`, `low` — required
- `volume` — optional but forwarded when present

The adapter enforces a minimum of **40 bars**. Anything smaller, missing
a required column, or passed as `None` falls back to `HOLD` with a
`fallback:*` reason so the backend risk gates reject it.

### LSTM lifecycle

`lstm_model.LSTMPipeline` is stateful — it needs `fit()` before
`predict_next_delta()`. The adapter caches one instance per
`ALPHA_LSTM_CLASS` value and runs `fit` on the first OHLCV batch it
sees; subsequent calls only predict. Call
`mellytrade_v3.mt5.lstm_signal_adapter.reset_cache()` to drop the cached
instance (e.g. at start of a new session, or in tests).

Without a real OHLCV DataFrame the adapter always returns a HOLD fallback —
this is by design so missing data never leaks into live trading.

```python
from mellytrade_v3.mt5.mt5_bridge import run_once, BridgeConfig
cfg = BridgeConfig(api_url="http://127.0.0.1:8000",
                   api_key="<FASTAPI_KEY>",
                   symbol="EURUSD")
print(run_once(cfg))
```

### One-shot CLI

```bash
# from repo root
python -m mellytrade_v3.mt5.mt5_bridge
# or (with PYTHONPATH pre-set by the SessionStart hook):
python mellytrade_v3/mt5/mt5_bridge.py
```

Exit code is `0` when the bridge posts a signal, reports HOLD, or skips
(no OHLCV); any other status returns `1`.

### Setup diagnostic

`mellytrade_v3/mt5/check_setup.py` verifies the LSTM + adapter wiring
end-to-end without touching the network or the API:

```bash
python -m mellytrade_v3.mt5.check_setup
# or:
python mellytrade_v3/mt5/check_setup.py
```

It prints the resolved `ALPHA_*` env vars, runs the fallback path (no
OHLCV → HOLD + `is_fallback`), and feeds a 120-bar synthetic OHLCV frame
through `LSTMPipeline.fit()` + `predict_next_delta()`. Exit code `0` on
success, `1` otherwise.

## Dashboard

```bash
cd mellytrade_v3/mellytrade/dashboard
npm install
npm run dev   # http://127.0.0.1:5173
```

The dashboard proxies `/api/*` to the worker (`VITE_WORKER_URL`,
default `http://127.0.0.1:8787`).

## Worker

```bash
cd mellytrade_v3/mellytrade
npm install
npm run dev   # http://127.0.0.1:8787
```

Routes:
- `POST /api/publish` — secret-gated ingest from the backend
- `GET  /api/signals` — last 50 signals for the dashboard
- `GET  /api/health`  — liveness

## Test inventory

| Suite | Count | Command |
|---|---|---|
| `mellytrade-api/tests` | 7 | `cd mellytrade-api && pytest -q` |
| `mt5/tests` | 3 | `cd mellytrade_v3 && pytest mt5/tests -q` |

## Claude Code — SessionStart hook

The repo ships a `SessionStart` hook at `.claude/hooks/session-start.sh`,
registered via `.claude/settings.json`. On the Claude Code web sandbox
(where `CLAUDE_CODE_REMOTE=true`) it installs `requirements-ci.txt` and
`mellytrade_v3/mellytrade-api/requirements.txt`, then exports
`PYTHONPATH` so `mellytrade_v3.*` and the root `lstm_model` module are
importable without manual setup. Nothing runs on local sessions.

Disable the hook locally by ensuring `CLAUDE_CODE_REMOTE` is unset (or
set to anything other than `true`). The hook writes `PYTHONPATH` to
`$CLAUDE_ENV_FILE` when provided by the runtime, so subsequent commands
see both the repo root and `mellytrade_v3/` on the import path.

## Outstanding follow-ups

- Wire a real Postgres `DATABASE_URL` for staging/prod.
- Swap in real CloudMCP tokens for `.mcp.json` / `.cursor/mcp.json`.
- Add the Unity "AI Signal Visualization Dashboard" project under
  `C:\AI\MellyTrade_Workspace\07_Unity_Projects`.
- Extend the CF Worker with a Durable Object / WebSocket channel if
  sub-second dashboard updates are needed.
