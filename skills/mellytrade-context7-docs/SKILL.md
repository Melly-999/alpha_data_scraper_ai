# mellytrade-context7-docs

## Purpose

Look up current docs before coding against external APIs or libraries.

## When to use

Use when a task depends on libraries or APIs that may have changed.

## Hard safety boundaries

- Documentation lookup only.
- No file edits.
- No runtime safety weakening.
- No secrets or private paths.

## Step-by-step procedure

1. Identify the external libraries in scope.
2. Use Context7 to look up current docs.
3. Summarize the findings.
4. Highlight any API or signature changes.
5. Hand the findings to implementation or review work.

## Validation expectations

- Current docs must be summarized before implementation.
- Model memory must not be treated as the source of truth.

## Final report template

```text
- Libraries:
- Docs sources:
- Key findings:
- API/signature changes:
- Follow-up actions:
```
