# MellyTrade v3

End-to-end MT5 → Backend → Cloudflare Worker → Dashboard pipeline that rides
on the `alpha_data_scraper_ai` LSTM. Strict risk rules are enforced at the
backend layer and cannot be loosened at runtime.

```
MT5 bridge  ──POST /signal──▶  FastAPI backend  ──POST /api/publish──▶  CF Worker  ──GET /api/signals──▶  React dashboard
                                     │
                                     └─ SQLite / Postgres (audit log)
```

## Components

| Path | Purpose |
|---|---|
| `mellytrade-api/` | FastAPI service, risk gates, signal persistence |
| `mt5/` | LSTM adapter + MT5 bridge that posts to `/signal` |
| `mellytrade/` | Cloudflare Worker (hub) + React/Vite `dashboard/` |
| `docs/` | Additional usage/deployment notes |

## Risk rules (enforced, never loosened)

- `MAX_RISK_PERCENT = 1.0` — signals above are rejected with `risk_above_max`
- `MIN_CONFIDENCE = 70` — below is rejected with `confidence_below_min`
- Every BUY/SELL must carry a consistent `stop_loss` and `take_profit`
- Per-symbol `COOLDOWN_SECONDS = 60` — reject with `cooldown_active`

## Quick start

```bash
# backend
cd mellytrade_v3/mellytrade-api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
pytest                                # should report 7 passed
uvicorn app.main:app --reload --port 8000

# worker (Cloudflare)
cd ../mellytrade
npm install
npm run dev                           # default: http://127.0.0.1:8787

# dashboard
cd dashboard
npm install
npm run dev                           # default: http://127.0.0.1:5173

# MT5 bridge (one-shot)
cd ../../..
python -m mellytrade_v3.mt5.mt5_bridge

# LSTM + adapter diagnostic (no network)
python -m mellytrade_v3.mt5.check_setup
```

## Claude Code — SessionStart hook

On the Claude Code web sandbox the repo's SessionStart hook auto-installs
`requirements-ci.txt` + `mellytrade-api/requirements.txt` and exports
`PYTHONPATH`. See `../.claude/hooks/session-start.sh` and
`docs/MELLYTRADE_V3.md`.

See `../DEPLOYMENT_GUIDE.md` for production guidance.
