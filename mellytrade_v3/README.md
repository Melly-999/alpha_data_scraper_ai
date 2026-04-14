# MellyTrade v3

Integrated monorepo starter with:
- `mellytrade-api/` FastAPI risk + logging + SQLite/Postgres persistence + publish flow
- `mellytrade/` Cloudflare Worker + Durable Object WebSocket hub
- `mellytrade/dashboard/` React/Vite dashboard
- `mt5/` MT5 bridge + ensemble combiner + alpha_data_scraper_ai adapter
- `scripts/` bootstrap / install helpers

## Local start

### 1) API
```bash
cd mellytrade-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload --port 8000
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

### 4) MT5 bridge
```bash
cd mt5
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python mt5_bridge.py
```

## End-to-end flow
MT5 bridge -> FastAPI `/signal` -> DB log -> Cloudflare Worker `/api/publish` -> Durable Object -> dashboard websocket clients.
