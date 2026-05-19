# AI PR Reviewer Safety Policy

This policy defines the review rules that must stay in place for MellyTrade.

## Required fail or warn conditions

- Fail or warn if `autotrade=true` appears
- Fail or warn if `dry_run=false` appears
- Fail or warn if `live_orders_blocked=false` appears
- Fail or warn if `max risk > 1%` appears
- Fail or warn if new broker execution code appears
- Fail or warn if MT5 or IBKR order routing appears
- Fail or warn if frontend contains Buy, Sell, Execute, Place Order, Go Live, or Connect Broker controls
- Fail or warn if `.env`, tokens, credentials, account IDs, or webhook URLs appear
- Fail or warn if new non-paper order or execution endpoints appear

## Allowlist guidance

- Allow `/api/paper/**` only when it is clearly paper-only, sandbox-only, dry-run-only, and human-review oriented

## Reviewer behavior

- Comments are advisory only
- Human review is required
- The reviewer must not approve or merge pull requests
- The reviewer must not provide investment advice
- The reviewer must not recommend enabling live trading

## MellyTrade safety posture to reinforce

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `max risk <= 1%`
- No live broker execution
- No order buttons
- No secrets
- No workflow escalation

