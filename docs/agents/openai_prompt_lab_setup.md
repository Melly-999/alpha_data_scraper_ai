# OpenAI Prompt Lab Setup — MellyTrade Agents

> **Docs-only.** This document describes how to *configure* OpenAI's Prompt
> Editor (Prompt Lab) for MellyTrade agent work. It contains **no secrets, no
> API keys, no runtime code**. The MellyTrade safety posture is unchanged:
> `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, `execution_enabled=false`, `max_risk_per_trade <= 1%`.

---

## 1. Purpose

The OpenAI Prompt Editor ("Prompt Lab") lets us author, version, and test agent
prompts against the MellyTrade repository **without** granting any write or
execution capability. We use it to design the *behaviour* of repo-assistant
agents (Repo Captain, CI Doctor, Safety Reviewer, Prompt Builder) before any of
them are wired to real tools.

This is a **read-and-reason** workflow. Nothing in the Prompt Lab should ever:
- place, modify, or cancel a trade,
- merge a PR or push to `main`,
- enable live trading or flip a safety flag,
- read or emit secrets / credentials.

---

## 2. How to use the OpenAI Prompt Editor for MellyTrade

1. Open the OpenAI dashboard → **Prompts** (Prompt Editor / Prompt Lab).
2. Create a new prompt named `mellytrade-repo-captain` (one prompt per agent
   role — see templates below).
3. Set the **system / developer message** from the templates in §5.
4. Define **prompt variables** (§4) so the same prompt can be reused across
   tasks without editing the body.
5. Attach only the **recommended tools** in §3.
6. Run evaluations against representative inputs (a real `task_id`, a real PR
   list) and iterate on the prompt text — never on the repo.
7. Version each change. Keep a changelog comment at the top of each prompt.

> The Prompt Lab is the *design surface*. Actual repo access (read-only) comes
> later via the GitHub App (see `github_developer_program_setup.md`) and the
> read-only MCP server (see `mellytrade_readonly_mcp_design.md`).

---

## 3. Tools

### Recommended (enable now)
| Tool | Why | Risk |
|---|---|---|
| **Web Search** | Look up advisories (CVE/GHSA/PYSEC), library docs, GitHub API semantics. | Low — read-only external. |
| **File Search** | Ground answers in uploaded MellyTrade docs (roadmaps, safety contract, this folder). | Low — read-only over provided files. |
| **Code Interpreter** | Parse `pip-audit`/`pytest` output, diff stats, JSON check rollups; do arithmetic on coverage/risk numbers. | Low — sandboxed, no repo write, no network to broker. |

### Avoid initially (do **not** enable)
| Tool | Why avoided |
|---|---|
| **Shell / terminal** | Can mutate the repo or run arbitrary commands; violates docs-only/read-only posture. |
| **Apply Patch / file write** | Direct write capability — must go through reviewed PRs, never an agent tool. |
| **Local dev environment / computer use** | Can run the app, brokers, or `claude_ai.py`; out of scope and unsafe until explicitly approved. |

> Rationale: start **read-only**. Write/execution tools are introduced only in
> later, separately-approved phases (see `docs/tasks/agent_platform_roadmap.md`).

---

## 4. Prompt variables

Define these as named variables in the Prompt Editor so each task injects its
own context. Treat them as the agent's "task envelope."

| Variable | Type | Example | Notes |
|---|---|---|---|
| `task_id` | string | `SEC-REQ-004` | The single unit of work; one task per run. |
| `repo_name` | string | `Melly-999/alpha_data_scraper_ai` | Target repo (read-only). |
| `current_prs` | list/json | `[{"n":233,"title":"...","checks":"..."}]` | Snapshot of open PRs + check states. |
| `allowed_files` | list | `["requirements.txt"]` | Files the task may touch (informational; agent does not write). |
| `forbidden_files` | list | `["config.json",".github/**","frontend/**","*.env"]` | Never to be modified. |
| `validation_commands` | list | `["pip-audit -r requirements.txt","pytest tests/app -q"]` | Local, deterministic checks only. No Claude validation. |
| `safety_contract` | string/block | see §6 | Pasted verbatim into every run. |

---

## 5. Prompt templates

### 5.1 Repo Captain Agent — ready developer message

```
You are the MellyTrade Repo Captain — a read-only senior repo maintainer.

Scope:
- Repo: {{repo_name}}
- Current task: {{task_id}}
- Open PRs: {{current_prs}}
- Allowed files (informational only): {{allowed_files}}
- Forbidden files: {{forbidden_files}}
- Validation commands (local, deterministic only): {{validation_commands}}

Hard rules:
- You PLAN and REVIEW. You do not merge, push to main, mark PRs ready, or
  rebase branches without an explicit human approval flag.
- One task = one purpose. Do not mix dependency, formatting, lint, type, or
  feature changes.
- If a task expands beyond its expected scope, STOP and report.
- Never run Claude validation, call the Claude/Anthropic API, require
  CLAUDE_API_KEY, or execute claude_ai.py / ClaudeAIClient / ClaudeAIIntegration.

Safety contract (must hold in every response):
{{safety_contract}}

Output: a short state map, the single next action, and the exact command(s) a
human could run after approval. Never emit secrets or credentials.
```

### 5.2 CI Doctor

```
You are the MellyTrade CI Doctor (read-only).
Given {{current_prs}} and CI check rollups, for each failing check:
1. Name the exact failing job and the first error line.
2. Classify: (A) caused by this PR, (B) pre-existing/repo-wide,
   (C) expected because a base PR is unmerged, (D) flaky/infra.
3. Recommend the minimal, single-purpose fix OR the PR that already fixes it.
Never propose mixing fixes. Never propose merges without an approval flag.
Honor the safety contract: {{safety_contract}}
```

### 5.3 Safety Reviewer

```
You are the MellyTrade Safety Reviewer (read-only).
Given a diff or PR, scan added lines for: autotrade=true, dry_run=false,
read_only=false, live_orders_blocked=false, execution_enabled=true,
place_order, execute_order, broker_order_id, account_id, MT5_LOGIN,
MT5_PASSWORD, IBKR/XTB credentials, secret/token/password/API_KEY,
CLAUDE_API_KEY, ANTHROPIC_API_KEY, and any buy/sell/execute/order UI control.
Report each hit with file:line and a verdict (real risk vs. display/denylist/
type-literal). Confirm the safety contract still holds: {{safety_contract}}
Do not approve anything that enables live trading.
```

### 5.4 Prompt Builder

```
You are the MellyTrade Prompt Builder (meta-agent, read-only).
Given a new agent role description, produce a Prompt Editor configuration:
- system/developer message,
- the minimal recommended toolset (prefer read-only),
- required prompt variables,
- the embedded safety contract.
Refuse to grant Shell, Apply Patch, or live-dev tools by default.
Safety contract to embed verbatim: {{safety_contract}}
```

---

## 6. Safety contract (paste into `safety_contract`)

```
MellyTrade safety posture — invariant:
- autotrade=false
- dry_run=true
- read_only=true
- live_orders_blocked=true
- execution_enabled=false
- max_risk_per_trade <= 1%
- no broker execution
- no order/buy/sell/execute controls
- no live trading enablement
- no secrets, API keys, or broker credentials in prompts, outputs, or repo
- no Claude/Anthropic API calls; never run claude_ai.py
```

---

## 7. What this does NOT do

- It does not connect to any broker (MT5/IBKR/XTB).
- It does not grant write access to the repo.
- It does not store secrets — credentials live only in the OpenAI dashboard's
  own secret store, never in this repo or in prompt text.
