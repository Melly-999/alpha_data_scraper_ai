# Closed Beta Readiness

## Product positioning
MellyTrade should be positioned as:
- read-only AI trading research terminal
- educational/research dashboard
- no investment advice
- no live trading
- no order execution

## Must-have before giving access to people
1. Private access/auth
2. Demo mode without secrets
3. Clear disclaimer
4. Privacy policy draft
5. Terms of use draft
6. Rate limits
7. Monitoring/logs
8. Error/degraded-state UX
9. User data separation
10. Support/contact process
11. Cost controls for API usage
12. Security review

## Not allowed in beta
- personal investment advice
- guaranteed profits
- auto execution
- copy trading
- personalized position sizing
- live order routing
- broker credentials from users unless secure auth model exists

## Beta-safe feature list
- watchlist
- signal preview as educational observation
- risk dashboard
- audit feed
- paper/demo mode
- reports
- read-only broker status

## Release gates

### Technical gate
- read-only startup path passes local smoke
- GET-only routes respond correctly
- frontend build and safety validation stay green

### Safety gate
- autotrade remains false
- dry_run remains true
- read_only remains true
- live_orders_blocked remains true
- max risk stays at or below 1 percent

### Legal/compliance wording gate
- no investment advice language
- no profit guarantees
- no live trading claims
- no broker execution promises

### Security gate
- no secrets in repo or docs
- auth model defined before any private beta access
- logs and audit trails reviewed for sensitive leakage

### UX gate
- degraded states are obvious
- no hidden action buttons on read-only screens
- beta users can find safety status quickly

## Related closed beta docs

- `docs/product/closed_beta_disclaimer.md`
- `docs/product/closed_beta_limitations.md`
- `docs/product/closed_beta_bug_report_template.md`
- `docs/qa/browser_ui_smoke_checklist.md`
