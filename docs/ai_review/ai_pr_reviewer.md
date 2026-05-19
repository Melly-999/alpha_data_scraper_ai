# AI PR Reviewer

## Purpose in MellyTrade

`ai-pr-reviewer` is a reviewer assistant for pull requests. In MellyTrade it may be used to provide a second-pass code review for docs, tests, and tooling changes.

It is not a merge authority, approval authority, or release gate. Human review remains required for every change.

## What it should review

- Safety invariants and read-only posture
- Test coverage and missing regression checks
- Scope creep and unrelated changes
- Secrets exposure and credential handling
- Broker, MT5, and IBKR execution risk
- Frontend order-button or live-connect risk
- API route safety and execution-shaped endpoints

## What it must not do

- Provide investment advice
- Recommend enabling live trading
- Suggest weakening risk controls
- Approve or merge pull requests automatically
- Post misleading trading guidance

## Integration shape

The upstream project is a local FastAPI plus CLI review app that fetches PR diffs from GitHub and sends them to an LLM for commentary. It is suitable for manual, advisory review only.

For MellyTrade, keep it outside the trading runtime and use it only as a development aid.

