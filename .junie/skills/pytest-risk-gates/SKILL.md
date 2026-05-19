# Pytest Risk Gates

Use this skill when adding or reviewing pytest safety tests.

## Test Goals

- Assert safety invariants.
- Fail on forbidden terms in active routes or UI.
- Confirm expected safety flags remain present.
- Ensure no live order or execution route exposure.
- Keep tests deterministic.
- Avoid external network dependency.

## Good Assertions

- Read-only API paths remain GET-only.
- `autotrade=false` remains preserved.
- `dry_run=true` remains preserved.
- `live_orders_blocked=true` remains preserved.
- Order or execution affordances do not appear in the UI.

