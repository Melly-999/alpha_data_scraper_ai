# MellyTrade API (Sprint 1A)

Read-only REST API for the MellyTrade Direction B trader dashboard. Provides signal data, audit trails, health status, and risk configuration snapshots.

## Safety First

This API is **read-only by design**. No execution routes are exposed. The system runs with:
- `dry_run=true` (no live orders)
- `autotrade=false` (no automated execution)
- `read_only=true` (decision support only)
- Max risk capped at 1% per position

## Endpoints

### `GET /health`

System health and safety posture snapshot.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-04-30T10:30:00Z",
  "dry_run": true,
  "autotrade_enabled": false,
  "read_only": true,
  "db_healthy": true
}
```

### `GET /signals`

Signal feed with optional filtering. Confidence is clamped to [33, 85]%.

**Query Parameters:**
- `symbol` (str): Filter by symbol (e.g. "EURUSD")
- `status` (str): Filter by "accepted" or "rejected"
- `since` (ISO8601): Only signals after this timestamp
- `until` (ISO8601): Only signals before this timestamp
- `limit` (int, default=50): Max records to return

**Response:**
```json
{
  "signals": [
    {
      "id": "sig_abc123",
      "symbol": "EURUSD",
      "direction": "BUY",
      "confidence": 72,
      "confidence_clamped": 72,
      "strategy": "MTF_TREND",
      "risk_pct": 0.85,
      "status": "accepted",
      "rejection_reason": null,
      "dry_run": true,
      "read_only": true,
      "created_at": "2026-04-30T10:15:00Z"
    }
  ],
  "total": 145
}
```

### `GET /audit`

Audit trail of events: signal decisions, risk gates, safety state changes.

**Query Parameters:**
- `event_type` (str): Filter by event type (e.g. "signal_accepted", "risk_gate_failed")
- `since` (ISO8601): Only events after this timestamp
- `limit` (int, default=50): Max records to return

**Response:**
```json
{
  "events": [
    {
      "timestamp": "2026-04-30T10:15:00Z",
      "type": "signal_accepted",
      "severity": "info",
      "message": "EURUSD BUY signal accepted (confidence 72%)",
      "signal_id": "sig_abc123",
      "detail": {
        "symbol": "EURUSD",
        "direction": "BUY",
        "confidence": 72
      }
    },
    {
      "timestamp": "2026-04-30T10:00:00Z",
      "type": "dry_run_active",
      "severity": "info",
      "message": "Dry-run mode enabled",
      "signal_id": null,
      "detail": {}
    }
  ],
  "dry_run": true,
  "read_only": true,
  "live_orders_blocked": true
}
```

### `GET /risk/config`

Risk gate configuration snapshot.

**Response:**
```json
{
  "max_risk_pct": 1.0,
  "min_confidence_threshold": 70,
  "max_daily_loss_pct": 5.0,
  "max_open_positions": 3,
  "live_orders_blocked": true
}
```

## Authentication

All endpoints are public by default. To require authentication, set the `API_KEY` environment variable:

```bash
export API_KEY="your-secret-key"
```

Clients must then send the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8000/signals
```

## Local Development

### Setup

```bash
cd mellytrade_v3/mellytrade-api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Run

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend listens on `http://localhost:8000`.

### Test

```bash
python -m pytest -q
```

27 tests covering signal filtering, audit events, safety posture, and API contracts.

## Frontend Integration

The React frontend (`frontend/`) connects to this API via:

- Base URL: `http://localhost:5173/melly-api` (dev proxy) or `VITE_MELLY_API_BASE_URL` env var
- API key: optional `VITE_MELLY_API_KEY` env var (sent as `X-API-Key` header)
- Polling: 12s for audit, 15s for signals, 30s for health, 60s for risk config

See `frontend/README.md` for frontend setup.

## Type Contracts

TypeScript types for API responses are defined in `frontend/src/types/melly.ts` (separate from legacy `types/api.ts` to avoid collision).

## Safety Guarantees

- ✓ No POST/PUT/DELETE endpoints exposed
- ✓ Confidence clamped to [33, 85]%
- ✓ Rejection reasons logged for audit trail
- ✓ Dry-run and read-only flags always present in responses
- ✓ Risk gates snapshot always available
- ✓ All timestamps in ISO8601 UTC
