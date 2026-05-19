# Context7 Docs Lookup Prompt

## When to use

Use this before changing code that depends on external APIs, libraries, or
framework behavior.

## Safety boundaries

- Docs lookup only.
- No code changes.
- No runtime safety weakening.
- No secrets or credentials.

## Copy-paste prompt

```text
Use Context7 to look up current documentation before coding in MellyTrade.

Focus on:
- FastAPI
- Pydantic v2
- React
- Vite
- Supabase
- Playwright/browser tooling

Requirements:
- Summarize the current docs findings.
- Note any API or signature changes that affect the task.
- Do not rely on model memory for current API signatures.
- If docs conflict with local assumptions, prefer the docs and flag the mismatch.
```

## Expected final report format

```text
- Docs queried:
- Key findings:
- API/signature changes:
- Local assumptions to revise:
- Follow-up implementation notes:
```
