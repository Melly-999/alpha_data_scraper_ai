# Reusable Prompt Pack

This pack provides copy-paste task prompts for safe AI-assisted development in
MellyTrade.

## Purpose

- Standardize how Claude Code, Codex, OpenCode, VS Code/Cursor-style workflows,
  and local fallback reviewers are used.
- Keep prompts consistent across tasks.
- Reinforce safety checks before any implementation or review step.

These prompts are task templates, not permission to change runtime safety.

## How to use it

- **Claude Code**: use the planning, review, safety audit, and cleanup prompts.
- **Codex**: use the implementation prompt, Context7 lookup prompt, and
  publish gate prompt.
- **OpenCode**: use the same prompts for local multi-provider sessions.
- **VS Code / Cursor style workflows**: paste the prompt that matches the task
  into the agent or chat panel before editing.
- **LM Studio / Ollama**: use only as local fallback reviewers for cheap or
  offline review support. Do not treat them as the source of truth for current
  library APIs.

## Prompt catalog

| Prompt file | Use when |
|---|---|
| `prompts/ai_workflow/planning_prompt.md` | Before any code or docs change |
| `prompts/ai_workflow/context7_docs_lookup_prompt.md` | Before touching external APIs or libraries |
| `prompts/ai_workflow/implementation_prompt.md` | For a small scoped implementation |
| `prompts/ai_workflow/safety_audit_prompt.md` | Before merge or publish decisions |
| `prompts/ai_workflow/frontend_devtools_prompt.md` | If frontend files changed |
| `prompts/ai_workflow/review_prompt.md` | For diff and PR review |
| `prompts/ai_workflow/publish_gate_prompt.md` | Before push and draft PR creation |
| `prompts/ai_workflow/cleanup_gate_prompt.md` | After merge, before branch cleanup |

## Recommended task flow

1. Run the planning prompt.
2. Run the Context7 docs lookup prompt.
3. Run the implementation prompt.
4. Run the safety audit prompt.
5. If frontend changed, run the frontend DevTools prompt.
6. Run the review prompt.
7. Run the publish gate prompt.
8. Run the cleanup gate prompt after merge.

## Copy/paste quick start

```text
1. Use the planning prompt to define scope.
2. Use the Context7 lookup prompt for current APIs.
3. Use the implementation prompt for the smallest safe patch.
4. Use the safety audit prompt before merge.
5. If frontend changed, run the frontend DevTools prompt.
6. Use the review prompt for PR review.
7. Use the publish gate prompt before push and draft PR.
8. Use the cleanup gate prompt after merge.
```

## Validation commands

```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app -q
cd frontend
npm run build
```

Run the frontend build only if frontend/runtime files changed. If it is
skipped, the final report must say so explicitly.
