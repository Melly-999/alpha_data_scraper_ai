# Closed Beta Bug Report Template

## Quick summary

Describe the issue in one or two sentences.

## Environment

- Date/time:
- OS:
- Browser:
- Local or hosted:
- Backend URL:
- Frontend URL:
- Commit SHA:
- Branch:
- Demo/fallback mode visible: yes/no
- READ ONLY badge visible: yes/no
- DRY RUN ACTIVE visible: yes/no
- LIVE ORDERS BLOCKED visible: yes/no

## Page or area

Select one:

- Terminal Overview
- AI Workspace / Scanner
- Watchlist / Market Overview
- Audit & Events
- Risk Manager
- Broker Status
- Portfolio / Reports
- Settings / Safety
- Other

## Expected behavior

What did you expect to happen?

## Actual behavior

What happened instead?

## Steps to reproduce

## Screenshots

Attach screenshots only if they do not contain:
- secrets
- API keys
- account IDs
- broker credentials
- private financial data

## Console errors

Paste browser console errors here, if any.

## Backend/API observations

Paste only safe, non-secret information.

Do not paste:
- API keys
- service role keys
- broker credentials
- auth tokens
- account IDs

## Safety posture check

Confirm:

- autotrade=false
- dry_run=true
- read_only=true
- live_orders_blocked=true
- max risk<=1%

## Did this expose any unsafe control?

Answer yes/no:

- Buy/Sell button:
- Execute button:
- Connect live broker control:
- Editable risk control:
- Mutation action:
- Live order path:
- Secret/account ID visible:

If yes, describe exactly what you saw.

## Severity

Choose one:

- P0 — safety issue / execution-like control / secret exposure
- P1 — app broken / main UI unusable
- P2 — feature confusing / degraded but usable
- P3 — visual polish / copy issue

## Additional notes

Anything else?
