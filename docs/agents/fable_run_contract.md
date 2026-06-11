# Fable 5 Run Contract — MellyTrade

Operating contract for using Anthropic Claude **Fable 5** (via Claude Code or
compatible agent harnesses) on the `alpha_data_scraper_ai` repository.

- **Status:** Active
- **Scope:** Documentation for agent operators and for the agent itself
- **Related prompts:** [fable_pr_review_prompt.md](fable_pr_review_prompt.md) ·
  [fable_vision_ui_qa_prompt.md](fable_vision_ui_qa_prompt.md) ·
  lessons in [docs/knowledge/fable_lessons/](../knowledge/fable_lessons/README.md)

---

## 1. Purpose of Fable 5 in MellyTrade

Fable 5 is the strongest available reasoning/review model in our toolchain. In
MellyTrade it is used as a **senior engineer and review gate**, not as an
autocomplete. Typical assignments:

- Long-running, multi-phase repo tasks (brand pipelines, showcase packs,
  evidence capture, multi-PR chains)
- PR review gates before marking ready / merging
- UI / screenshot / vision QA of the terminal, dashboard, and mobile surfaces
- Writing and maintaining project memory ("lessons learned")
- Demo-freeze-friendly execution where scope discipline matters more than speed

## 2. When to use Fable 5

- Tasks spanning many steps, files, or PRs where context retention pays off
- Review gates where a wrong PASS verdict is expensive
- Safety-sensitive wording (README, brand, public docs) that must not overclaim
- Vision QA on UI screenshots
- Anything that needs a verifiable PASS/BLOCKED report at the end

## 3. When NOT to use Fable 5

- One-line edits, typo fixes, mechanical renames — use a smaller model or do it
  by hand
- Tasks that are purely interactive exploration with no deliverable
- Anything requiring live broker connectivity or real-money behavior — that is
  out of scope for this repository entirely, regardless of model

**Cost-awareness rule:** Fable 5 is for hard or long tasks. If the task fits in
one small diff and one validation run, it does not need the strongest model.

## 4. Forbidden data — never put these in prompts, files, or screenshots

- Secrets of any kind
- Tokens, session cookies, signing keys
- API keys (Anthropic, NewsAPI, broker, hosting, anything)
- `.env` values or contents of any environment file
- Broker credentials (MT5 / IBKR / XTB / Alpaca or any other)
- Account IDs, broker order IDs, customer identifiers
- Private user or client data
- Screenshots containing any of the above, private windows, e-mail, or chat

If a task appears to require any of this, the correct output is **BLOCKED**
with an explanation — not a workaround.

## 5. Required working style

Every Fable 5 run on this repo follows the same loop:

1. **Inspect first.** Read the relevant files and docs before editing anything.
2. **Identify current branch and dirty files.** `git status --short`,
   `git branch --show-current`. Never work on `main` directly; never commit
   from a branch with unrelated dirty changes without isolating them.
3. **Plan scope.** State which files are allowed to change. Anything outside
   that list is a stop condition, not a judgment call.
4. **Modify only allowed files.** Stage with explicit pathspecs only — never
   `git add .` or `git add -A`.
5. **Verify claims with tool output.** Dimensions, hashes, link targets, PR
   metadata, render checks — measure, do not assume.
6. **Run validation where available.** `git diff --check`,
   `python scripts/validate_safety_config.py`, focused static scans of changed
   files, and build/tests when runtime files are touched.
7. **Produce a PASS/BLOCKED final report** listing changed files, validation
   commands with real results, scan findings, and safety confirmation.

**The honesty rule:** never claim a validation passed unless the command
actually ran in this session and actually passed. If a tool cannot run, report
the exact blocker. A skipped check is reported as skipped, with the reason.

## 6. Safety contract for trading-related work

All work must preserve the repository safety posture:

```text
autotrade           = false
dry_run             = true
read_only           = true   (where applicable)
live_orders_blocked = true
execution_enabled   = false  (where applicable)
max_risk_per_trade  = <= 1%
posture             = advisory-only, human review before merge
```

Hard prohibitions for any Fable 5 run:

- No broker execution paths, no live trading UX
- No buy/sell/order/execute/submit controls in any UI or doc (mentioning them
  inside explicit prohibition text is allowed)
- No profit claims, no financial advice, no invented metrics or traction
- No enabling flags (`autotrade=true`, `dry_run=false`,
  `execution_enabled=true`) anywhere, including examples

## 7. Demo-freeze friendly behavior

When a demo freeze is active or plausible:

- Prefer docs-only and evidence-only changes
- Keep diffs small, additive, and reviewable
- Never touch hosted runtime, deploy config, or workflows without an explicit
  task that says so
- Every change lands via a Draft PR and a human review gate — no direct pushes
  to `main`, no self-merges without an explicit merge task

## 8. Privacy and retention caution

Prompts, transcripts, and screenshots may be retained by tooling outside this
repository. Treat every prompt as potentially persistent:

- Keep sensitive paths, personal data, and credentials out of prompts
- Capture screenshots of the rendered target only — never the full desktop,
  other windows, tabs, or notification areas
- Store local evidence outside the repository unless a task explicitly
  approves committing it

## 9. Final report requirement

Every run ends with a structured report containing at minimum: PASS/BLOCKED
status, branch and SHAs, exact changed files, validation commands and their
real results, static scan summary, safety confirmation, and the recommended
next step. The report is written in English.
