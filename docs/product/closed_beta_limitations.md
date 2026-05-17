# MellyTrade Closed Beta Limitations

## Purpose

This document lists known limitations for the MellyTrade Closed Beta.

It helps testers understand what is expected, what is intentionally disabled, and what should be reported as a bug.

## Current beta status

MellyTrade Closed Beta is currently focused on:
- local/demo operation
- read-only terminal UI
- seeded/fallback scanner data
- safety posture visibility
- audit/event display
- degraded service transparency
- browser UI smoke testing

## Intended current behavior

The following behavior is expected:
- Supabase may be degraded or disabled locally
- MT5 may show synthetic mode
- IBKR may show degraded or safe-disconnected status
- News/API sources may show fallback demo items
- scanner rows may be seeded/demo rows
- audit events may use local/fallback display
- frontend should remain read-only
- risk controls should not be editable from the frontend
- live orders should remain blocked

## Known limitations

### Authentication
- No production user authentication yet
- No role-based beta access yet
- No per-user workspace separation yet

### Hosting
- Local-first workflow
- No production deployment guarantee yet
- No SLA / uptime guarantee

### Data
- Demo/fallback data may be used
- Some service statuses may be degraded locally
- Market/news data may not be live
- Scanner results are advisory/demo unless explicitly connected to verified sources

### Broker integration
- Broker surfaces are read-only or safe-disconnected
- No live order execution
- No order placement
- No order cancellation
- No order modification
- No live account management

### Risk system
- Risk posture is locked for beta
- Risk controls are display-only
- max risk must stay <=1%
- dry-run/read-only posture must remain enforced

### Signals / Scanner
- Scanner output is not trading advice
- Scanner labels are research states only
- Human review is required
- No scanner output should be treated as an instruction to trade

### Reporting / Portfolio
- Portfolio and reports may be placeholder/demo
- No real account IDs should be displayed
- Screenshots must avoid secrets/account data
- Exports must exclude secrets

### Payments / Commercial Access
- No production billing yet
- No paid subscription system yet
- No refund/payment policy yet
- Any future paid access requires legal/disclaimer/privacy review first

### Legal / Compliance
- Not investment advice
- Not financial planning
- Not tax/legal advice
- No guaranteed profits
- Users remain responsible for decisions

## What testers should report

Testers should report:
- confusing labels
- missing safety badge
- any visible execution-like button
- any buy/sell/execute wording that feels actionable
- broken layout
- unreadable contrast
- console errors
- unexpected API failures
- hidden or missing demo/read-only status
- any accidental account ID or secret exposure
- anything that looks like live trading could happen

## What testers should not do

Testers should not:
- connect live broker credentials
- attempt to place orders
- use demo signals for real trades
- paste secrets into screenshots or issues
- share private account data
- treat the beta as financial advice

## Exit criteria for broader beta

Before wider beta access, MellyTrade should have:
- clear beta disclaimer
- limitations doc
- bug report template
- browser UI smoke checklist
- screenshot pack with safety badges
- production deployment plan
- authentication/access control plan
- privacy/data handling notes
- no-investment-advice language
- monitoring/logging plan
