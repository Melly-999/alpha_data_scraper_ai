# MellyTrade API

Read-only REST API for the MellyTrade Direction B trader dashboard. It exposes
health, signal history, audit events, risk configuration, and alert-center
context for decision support.

## Safety Notice

This API is read-only by design for Direction B:

- No live execution endpoints
- No order placement
- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- Max risk remains <= 1% per signal

Do not add execution, order placement, close, flatten, or mutation routes to this
service without an explicitly approved future execution phase.

## Authentication

`GET /health` is public. All other endpoints require the configured
`FASTAPI_KEY` via the `X-API-Key` header.

```bash
curl -H "X-API-Key: test-key" http://127.0.0.1:8000/signals
```

For local development, set `FASTAPI_KEY` in the environment or `.env`. The
development default logs a warning and must not be used for production.

## Local Backend Startup

```bash
cd mellytrade_v3/mellytrade-api
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend tests:

```bash
python -m pytest -q
```

## Smoke Tests

From the repository root, run one of the read-only smoke scripts after starting
the backend and frontend:

```bash
bash scripts/smoke-test.sh
.\scripts\smoke-test.ps1
```

The smoke scripts validate dashboard read endpoints and do not place orders.

## Endpoints

### `GET /health`

System health and safety posture snapshot.

Response:

```json
{
  "status": "ok",
  "service": "mellytrade-api",
  "version": "0.1.0",
  "cooldown_seconds": 60,
  "min_confidence": 70.0,
  "max_risk_percent": 1.0,
  "database": "sqlite",
  "dry_run": true,
  "autotrade_enabled": false,
  "read_only": true,
  "live_orders_blocked": true
}
```

### `GET /signals`

Signal feed with optional filtering. Confidence is displayed with the Alpha
pipeline clamp range `[33, 85]`.

Query parameters:

- `symbol`: filter by symbol, for example `EURUSD`
- `status`: `accepted` or `rejected`
- `since`: ISO8601 lower timestamp bound
- `until`: ISO8601 upper timestamp bound
- `limit`: max records, default `50`, range `1..500`

Response: bare list of signal objects. There is no wrapper object and no
`total` field.

```json
[
  {
    "id": 1,
    "created_at": "2026-04-30T10:15:00Z",
    "symbol": "EURUSD",
    "action": "BUY",
    "confidence": 72.0,
    "confidence_clamped": 72.0,
    "risk_pct": 0.85,
    "entry_price": 1.0850,
    "stop_loss": 1.0830,
    "take_profit": 1.0890,
    "source": "alpha_lstm",
    "status": "accepted",
    "reason": "",
    "rejection_reason": null,
    "dry_run": true,
    "read_only": true
  }
]
```

### `GET /audit`

Audit feed derived from persisted signal decisions plus safety-state events.

Query parameters:

- `event_type`: optional audit event type filter
- `limit`: max records, default `100`, range `1..500`

Response:

```json
{
  "events": [
    {
      "type": "signal_accepted",
      "timestamp": "2026-04-30T10:15:00Z",
      "severity": "info",
      "message": "BUY EURUSD accepted (confidence 72)",
      "detail": {
        "symbol": "EURUSD",
        "action": "BUY",
        "confidence": 72.0,
        "risk_pct": 0.85,
        "source": "api"
      },
      "signal_id": 1
    }
  ],
  "dry_run": true,
  "read_only": true,
  "live_orders_blocked": true
}
```

### `GET /risk/config`

Risk gate configuration and current safety posture.

Response:

```json
{
  "min_confidence": 70.0,
  "max_risk_percent": 1.0,
  "cooldown_seconds": 60,
  "dry_run": true,
  "autotrade_enabled": false,
  "read_only": true,
  "live_orders_blocked": true,
  "gates": [
    {
      "name": "max_risk_percent",
      "active": true,
      "description": "Reject signals with risk_percent > 1"
    }
  ]
}
```

### `GET /alerts`

Read-only alert-center feed. Alerts are derived from safety posture, rejected
risk/cooldown signal records, backend-degraded conditions where applicable, and
a high-impact-news placeholder for a future data pass.

Query parameters:

- `limit`: max records, default `100`, range `1..500`

Response:

```json
[
  {
    "id": "safety-dry-run-active",
    "timestamp": "2026-04-30T10:15:00Z",
    "severity": "success",
    "category": "safety",
    "title": "Dry run active",
    "message": "No live orders will be sent while dry_run is active.",
    "source": "settings",
    "symbol": null,
    "signal_id": null,
    "read_only": true,
    "metadata": {
      "dry_run": true
    }
  }
]
```

## Frontend Integration

The React frontend uses the Vite dev proxy:

- Browser path: `/melly-api`
- Backend target: `http://127.0.0.1:8000`
- Optional override: `VITE_MELLY_API_BASE_URL`
- Optional key: `VITE_MELLY_API_KEY`, sent as `X-API-Key`

The frontend Melly client is intentionally GET-only.

## Type Contracts

Frontend contracts live in `frontend/src/types/melly.ts`. They are kept
separate from legacy `frontend/src/types/api.ts` shapes so Direction B dashboard
contracts stay explicit.

## Safety Guarantees

- No POST/PUT/PATCH/DELETE dashboard mutation endpoints
- No live execution endpoints
- No order placement logic
- `dry_run`, `read_only`, and `live_orders_blocked` are surfaced in responses
- Risk gate rejection reasons are preserved for audit and alert views
- `max_risk_percent` remains bounded by the Direction B 1% invariant
