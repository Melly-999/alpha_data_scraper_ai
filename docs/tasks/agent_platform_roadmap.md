# Agent Platform Roadmap — MellyTrade

> **Docs-only.** Sequencing plan for the MellyTrade agent platform. Each phase
> is gated; write/execution capability is introduced late and only with
> explicit approval. Safety posture unchanged throughout: `autotrade=false`,
> `dry_run=true`, `read_only=true`, `live_orders_blocked=true`,
> `execution_enabled=false`, `max_risk_per_trade <= 1%`.

---

## Guiding principles

1. **Read-only first.** Every phase before Phase 5 is observe-and-reason only.
2. **One capability per phase.** No mixing new tools with new write powers.
3. **Human approval gates** for anything beyond reading.
4. **No secrets in repo**, no broker execution, no Claude/Anthropic API calls
   from repo code at any phase.

---

## Phase 1 — Prompt Lab
- Author agent prompts in the OpenAI Prompt Editor (`openai_prompt_lab_setup.md`).
- Roles: Repo Captain, CI Doctor, Safety Reviewer, Prompt Builder.
- Tools: Web Search, File Search, Code Interpreter only.
- **Exit criteria:** stable prompts + embedded safety contract; no repo access yet.

## Phase 2 — GitHub App (read-only)
- Register read-only GitHub App via Developer Program
  (`github_developer_program_setup.md`).
- Scopes: Contents/Pull requests/Checks/Metadata = **Read**; Workflows/Secrets/
  Administration = **No access**.
- Webhook secret + signature verification; private key in secret manager.
- **Exit criteria:** App installed read-only; agents can observe PRs/checks via
  the App; zero write scopes.

## Phase 3 — MCP (read-only)
- Implement `mellytrade-readonly-mcp` (`mellytrade_readonly_mcp_design.md`).
- Tools: `get_open_prs`, `get_pr_checks`, `get_pr_diff_summary`,
  `get_safety_status`, `get_current_milestones`, `get_next_task`.
- Forbidden tools denylisted + CI-scanned.
- **Exit criteria:** agents query repo/safety state through MCP; still no writes.

## Phase 4 — Dashboard integration
- Surface read-only agent insights (PR queue, CI health, safety posture,
  milestones) in the existing read-only MellyTrade dashboard.
- Display-only; no action controls; reuses existing GET endpoints.
- **Exit criteria:** dashboard cards render agent/CI/safety state; no new
  mutation routes; safety badges visible.

## Phase 5 — Controlled write tools
- Introduce **gated** write tools only: `create_pr_comment`, `create_issue`,
  `update_docs_task_board` (docs-only path allowlist, via reviewed PR).
- Each behind an explicit human approval flag + audit trail.
- Still: no merge, no push-to-main, no trading, no secrets.
- **Exit criteria:** approved write tools live with gates + audit logging.

## Phase 6 — Evals & observability
- Build eval suites for each agent role (precision of CI triage, safety-scan
  recall, no-unsafe-suggestion guarantees).
- Add observability: tool-call logging (no secrets), latency/cost, refusal
  rates, false-positive/negative tracking.
- **Exit criteria:** regression evals gate prompt/tool changes; dashboards for
  agent quality and safety adherence.

---

## Out of scope for all phases (hard limits)
- Enabling live trading or flipping any safety flag.
- Placing/modifying/cancelling broker orders (MT5/IBKR/XTB).
- Merging PRs or pushing to `main` from an agent surface.
- Reading or writing secrets / credentials.
- Calling the Claude/Anthropic API from repo code or running `claude_ai.py`.

## Dependencies
Phase 1 → 2 → 3 → 4 are sequential. Phase 5 requires Phases 2–3 complete and a
separate approval. Phase 6 runs alongside Phases 3–5 as capabilities land.
