# Broker Support Matrix

This matrix documents the current MellyTrade broker registry behavior.
The registry is read-only by default, and `safe-disconnected` remains
the default adapter.

| Adapter | Default? | Paper? | Read-only? | Execution enabled? | Live orders blocked? | Account snapshot | Positions | Real network required? | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `safe-disconnected` | Yes | N/A | Yes | No | Yes | Safe zero snapshot | Empty list | No | Safe disconnected default |
| `ibkr-paper` | No | Yes | Yes | No | Yes | Safe zero by default; mocked or local read-only snapshot when enabled | Empty list by default; mocked or local read-only positions when enabled | Optional localhost Paper socket only when env-enabled | Optional read-only paper adapter |

## Registry Notes

- `create_default_registry()` registers `safe-disconnected` and
  `ibkr-paper`.
- `default_adapter_id` remains `safe-disconnected`.
- `get_default()` remains the safe disconnected adapter.
- `get("ibkr-paper")` returns the IBKR Paper read-only adapter.
- Both adapters expose safety flags through typed schemas.

## Endpoint Notes

The registry is exposed through GET-only endpoints:

```text
GET /api/brokers
GET /api/brokers/{adapter_id}/status
GET /api/brokers/{adapter_id}/account
GET /api/brokers/{adapter_id}/positions
```

Non-GET methods remain blocked with `405`, and the OpenAPI forbidden
path scan must remain clean.

## Safety Notes

- No execution routes are registered.
- No order, cancel, modify, or broker execution methods are exposed.
- No live broker credentials are required or stored.
- No account IDs are displayed in the registry cards.
- `autotrade=false`, `dry_run=true`, `read_only=true`, and
  `live_orders_blocked=true` remain preserved.
- Max risk per trade remains `<= 1%`.
