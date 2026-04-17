# MellyTrade v3

Integrated monorepo starter with:
- `mellytrade-api/` FastAPI risk + logging + SQLite/Postgres persistence + publish flow
- `mellytrade/` Cloudflare Worker + Durable Object WebSocket hub
- `mellytrade/dashboard/` React/Vite dashboard
- `mt5/` MT5 bridge + ensemble combiner + alpha_data_scraper_ai adapter
- `scripts/` bootstrap / install helpers

## Local start

Risk gates are enforced by the API before publish: `X-API-Key` is required,
`MAX_RISK_PERCENT=1.0`, `MIN_CONFIDENCE=70`, `stopLoss` and `takeProfit` are
mandatory, and duplicate symbol/direction signals are blocked for
`COOLDOWN_SECONDS=120`.

### 1) API
```bash
cd mellytrade-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### 2) Cloudflare worker
```bash
cd mellytrade
npm install
npm run dev
```

### 3) Dashboard
```bash
cd mellytrade/dashboard
npm install
npm run dev
```

The Vite dev server proxies `/ws` and `/api` to the local Worker on
`http://127.0.0.1:8787`.

### 4) MT5 bridge
```bash
cd mt5
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python mt5_bridge.py
```

Set `ALPHA_REPO_PATH` and either `ALPHA_LSTM_CLASS` or `ALPHA_LSTM_FUNCTION` to
wire the bridge to `alpha_data_scraper_ai`; without those values the adapter
falls back to HOLD and the technical weighting remains active.

## End-to-end flow
MT5 bridge -> FastAPI `/signal` -> DB log -> Cloudflare Worker `/api/publish` -> Durable Object -> dashboard websocket clients.
