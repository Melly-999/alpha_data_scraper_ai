# Backend GET-Only Endpoint

Use this skill when adding a backend preview or advisory endpoint for MellyTrade.

## Rules

- Endpoints must be `GET` only.
- Response schemas must preserve or include safety flags when trading-related:
  - `read_only=true`
  - `dry_run=true`
  - `live_orders_blocked=true`
  - `risk_allowed=false` where applicable
  - `execution_mode="dry_run_only"` where applicable
  - `requires_human_review=true` where applicable
- No broker, MT5, or IBKR calls.
- No persistence writes unless explicitly requested.
- No secrets.

## Tests Required

- Endpoint returns `200`.
- Method is GET-only.
- OpenAPI does not expose forbidden paths.
- Safety flags are canonical and not weakened.

## Implementation Notes

- Keep the surface advisory only.
- Prefer preview, draft, or sandbox semantics.
- Do not add order placement, execution, or live-connect behavior.

