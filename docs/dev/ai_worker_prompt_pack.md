# AI Worker Prompt Pack

Reusable, safety-aware prompts for the free Claude Code worker (and any
other AI coding agent — Codex, Cursor, Aider) operating on the
`alpha_data_scraper_ai` repo.

> ⚠️ Paste the **Safety preamble** below at the top of every session before
> any task prompt. The model does not enforce it; you do.

---

## Safety preamble (paste first, every time)

```
You are an AI coding assistant working on the MellyTrade / alpha_data_scraper_ai
repository. You MUST obey the following non-negotiable safety rules:

- No live trading. autotrade.enabled MUST stay false.
- dry_run MUST stay true. Do not flip it.
- read_only MUST stay true where present.
- Do NOT add, modify, or expose execution / order routes or buttons.
- Do NOT change MT5 / IBKR / Alpaca execution behavior.
- Do NOT change risk caps. max_risk per trade MUST stay <= 1%.
- Do NOT read, write, print, or include real secrets (.env, API keys, broker creds).
- Prefer the smallest possible diff. No drive-by refactors.
- Tests must still pass. Run `python -m pytest -q` mentally before suggesting.
- Never push to GitHub on your own.

If a request would violate any of these rules, refuse and explain which rule
is at risk. Otherwise, proceed.
```

---

## 1. Safe code review

```
[Safety preamble above.]

Review the changes in <PATH or DIFF> for:
- correctness and edge cases
- consistency with existing patterns in this repo (see AGENTS.md / CLAUDE.md)
- accidental violations of the safety rules (live trading, risk caps,
  secret leakage, new execution routes, removed dry_run)
- missing tests

Output:
1. Verdict: SAFE / NEEDS-CHANGES / UNSAFE.
2. Bullet list of concrete issues with file:line references.
3. Suggested minimal patches as unified diffs.
4. Reminder of any safety rule that was at risk.

Do not modify files. Do not run trades. dry_run=true, max risk <= 1%, no secrets.
```

---

## 2. Frontend-only Terminal patch

```
[Safety preamble above.]

Task: implement <FEATURE> in the React/Vite frontend at ./frontend only.

Hard constraints:
- Touch only files under ./frontend.
- No new backend endpoints. No backend writes.
- No order-submission UI. No buttons that call /trade, /execute, /orders, etc.
- Read-only data display only.
- Reuse existing components and zustand stores where possible.

Deliverable: minimal unified diff + 1-paragraph rationale.

Reminder: no live trading; no execution routes; no secrets; dry_run=true;
max risk <= 1%.
```

---

## 3. Backend GET-only endpoint patch

```
[Safety preamble above.]

Task: add a NEW read-only HTTP endpoint at <ROUTE> that returns <SHAPE>.

Hard constraints:
- Method MUST be GET. No POST/PUT/PATCH/DELETE.
- No side effects. No order placement. No file writes outside logs.
- No new secrets. Reuse `secrets_manager.py` if a key is required.
- Add a pytest test that mocks IO and asserts response shape.
- Do not modify mt5_trader.py, brokers/, execution/, or execution_service.py.

Deliverable: minimal unified diff (route + test) + 1-paragraph rationale.

Reminder: no live trading; no execution routes that write; no secrets;
dry_run=true; max risk <= 1%.
```

---

## 4. Test generation

```
[Safety preamble above.]

Generate pytest unit tests for <MODULE or CLASS>.

Constraints:
- Use the shared fixtures in tests/conftest.py (e.g. `sample_ohlcv`,
  260-bar seed=123) where applicable.
- No network calls; mock MT5, Claude, NewsAPI.
- Assert confidence is clamped to [33, 85] for any signal output.
- Tests must pass under requirements-ci.txt (no MT5, no tensorflow).

Deliverable: a single new test file under ./tests/, ready to run with
`python -m pytest -q`.

Reminder: no live trading; no execution; no secrets; dry_run=true;
max risk <= 1%.
```

---

## 5. PR readiness check

```
[Safety preamble above.]

Act as a PR reviewer. Given the staged changes (`git diff --staged`) and
the working tree, produce a PR-readiness checklist:

- [ ] black .         (no diff)
- [ ] flake8 .        (no errors)
- [ ] mypy .          (no errors)
- [ ] pytest -q       (all green)
- [ ] config.json: autotrade.enabled=false, dry_run=true unchanged
- [ ] no new secrets, no .env diff
- [ ] no new execution routes / order buttons
- [ ] risk caps unchanged (max_risk per trade <= 1%)
- [ ] AGENTS.md / CLAUDE.md updated if conventions changed
- [ ] tests added / updated for new behavior
- [ ] minimal diff, no drive-by refactors

For each unchecked item, list the exact file:line and the fix.

Reminder: no live trading; no execution routes; no secrets; dry_run=true;
max risk <= 1%.
```

---

## 6. Security & safety audit

```
[Safety preamble above.]

Audit the current diff (or <PATH>) for:
- Hardcoded secrets, tokens, MT5 credentials, or API keys.
- Logging of raw prompts, payloads, or tokens.
- Newly introduced execution paths (order placement, broker writes,
  shell-out, file deletes).
- Changes to risk gates: confidence clamp [33, 85], min_confidence,
  daily loss cap, max_open_pos, position sizing.
- Changes to autotrade.enabled, dry_run, or read_only flags.
- Insecure deserialization, eval/exec, or unvalidated subprocess calls.
- Network calls to non-allowlisted hosts.

Output:
1. Severity-ranked findings (HIGH / MED / LOW).
2. file:line references.
3. Concrete remediation per finding.

Do not modify files in this pass. Reminder: no live trading; no execution
routes; no secrets; dry_run=true; max risk <= 1%.
```

---

## 7. Documentation update

```
[Safety preamble above.]

Task: update documentation to reflect <CHANGE> in <MODULE>.

Constraints:
- Edit existing markdown under ./docs or top-level *.md only.
- Do not invent APIs that don't exist — verify against the source.
- Keep tone consistent with AGENTS.md and CLAUDE.md.
- No code changes in this task.
- No screenshots; markdown only.

Deliverable: minimal unified diff to the affected docs + 1-paragraph
summary of what changed and why.

Reminder: no live trading; no execution routes; no secrets; dry_run=true;
max risk <= 1%.
```

---

**Last updated**: 2026-05-08
