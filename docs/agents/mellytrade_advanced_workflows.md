# MellyTrade Advanced Claude Code Workflows

Adapt the 12 advanced Claude Code workflow patterns to MellyTrade with a strict
read-only / dry-run safety contract. These workflows are for **inspection,
analysis, planning, and documentation** — not for enabling trading or mutating
runtime behavior.

## Global Safety Contract (applies to every workflow)

**Preserve:**

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk `<= 1%`

**Never add:**

- broker execution
- order placement
- live trading UX
- buy/sell/execute action controls
- credentials
- account IDs
- real API keys

Each workflow below restates this contract in its **Safety checks** section.

---

## 1. Generate PR Reviews

- **Purpose:** Produce a senior-level review of a PR.
- **When to use:** Before merging any PR.
- **Prompt:** "Review this PR like a senior engineer. Focus on bugs, security,
  edge cases, maintainability, CI, and whether it violates MellyTrade read-only
  constraints. Do not edit files. Produce a merge recommendation and safety
  checklist."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes; `config.json`, `requirements*`, workflows.
- **Safety checks:** Preserve `autotrade=false`/`dry_run=true`/`read_only=true`/
  `live_orders_blocked=true`/`execution_enabled=false`/risk ≤1%. Never add broker
  execution, order placement, live-trading UX, buy/sell/execute controls,
  credentials, account IDs, or real API keys.
- **Output format:** findings list + merge recommendation + safety checklist.

## 2. Understand Large Codebases Fast

- **Purpose:** Map architecture and risk areas quickly.
- **When to use:** Onboarding or before a large change.
- **Prompt:** "Explain this repository architecture. Create a dependency map.
  Identify main entry points, safety-critical paths, frontend/backend
  boundaries, degraded states, and risk areas."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** architecture summary + dependency map + risk list.

## 3. Create Migration Plans

- **Purpose:** Plan a migration (framework, schema, dependency) safely.
- **When to use:** Before any structural change.
- **Prompt:** "Produce a step-by-step migration plan with rollback steps,
  blast-radius analysis, and safety gates. Do not edit files. Flag anything that
  could affect the read-only/dry-run posture."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes; safety config/runtime files.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** ordered plan + rollback + risk gates.

## 4. Generate Tests for Existing Code

- **Purpose:** Propose tests (including negative/safety tests).
- **When to use:** Coverage gaps on safety-critical paths.
- **Prompt:** "Propose pytest tests for this module, including negative tests
  that assert no order/execute routes exist and that safety flags stay safe. Do
  not edit files; output test code in the response only."
- **Allowed files:** read any; propose test files only (no auto-write).
- **Forbidden files:** runtime app code edits; `config.json`; workflows.
- **Safety checks:** Preserve the safety invariants above; tests must assert the
  read-only posture, never enable execution, orders, or live trading.
- **Output format:** proposed test code + rationale.

## 5. Find Dead Code

- **Purpose:** Identify unused code/exports.
- **When to use:** Tech-debt cleanup.
- **Prompt:** "Identify likely dead code, unused exports, and unreachable
  branches. Do not delete anything; produce a candidate list with confidence
  levels and verification steps."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** candidate table + verification steps.

## 6. Security Audit

- **Purpose:** Find vulnerabilities and unsafe defaults.
- **When to use:** Before releases and after dependency changes.
- **Prompt:** "Review this code for security vulnerabilities, secret leakage,
  unsafe defaults, dependency risks, and trading-safety violations. Do not
  modify files."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; flag (never
  introduce) execution, orders, live-trading UX, credentials, account IDs, or
  real API keys.
- **Output format:** findings by severity + remediation suggestions.

## 7. Refactor Large Features

- **Purpose:** Plan a safe refactor of a large feature.
- **When to use:** Before touching a complex module.
- **Prompt:** "Propose a refactor plan that preserves behavior and the
  read-only/dry-run posture. Identify seams, tests to add first, and a staged
  sequence. Do not edit files."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes during planning.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** staged refactor plan + test-first list.

## 8. Debug Faster

- **Purpose:** Localize a bug from symptoms.
- **When to use:** Active incident or failing test.
- **Prompt:** "Given this error/log, propose the most likely root causes,
  ranked, with the minimal read-only checks to confirm each. Do not edit files."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** ranked hypotheses + confirmation steps.

## 9. Generate Documentation Automatically

- **Purpose:** Draft docs from code.
- **When to use:** Undocumented modules.
- **Prompt:** "Generate documentation for this module: purpose, public API,
  inputs/outputs, and safety notes. Output markdown in the response; do not
  write files unless explicitly approved."
- **Allowed files:** read any; write only explicitly approved docs.
- **Forbidden files:** runtime app code; `config.json`; workflows.
- **Safety checks:** Preserve the safety invariants above; docs must not imply
  execution, orders, live trading, or contain credentials/keys.
- **Output format:** markdown doc draft.

## 10. Create System Design Diagrams

- **Purpose:** Produce architecture/sequence diagrams.
- **When to use:** Communicating design.
- **Prompt:** "Produce a Mermaid diagram of this system's components and data
  flow, marking safety-critical and read-only boundaries. Do not edit files."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; diagrams must show
  read-only boundaries and never imply live execution.
- **Output format:** Mermaid diagram + legend.

## 11. Analyze Technical Debt

- **Purpose:** Quantify and prioritize debt.
- **When to use:** Planning a hardening milestone (e.g. TYPE-HARDEN-001).
- **Prompt:** "Inventory technical debt (typing suppressions, TODOs, fragile
  paths). Rank by risk and effort. Do not edit files."
- **Allowed files:** read any; write none.
- **Forbidden files:** all writes.
- **Safety checks:** Preserve the safety invariants above; never add execution,
  orders, live-trading UX, credentials, account IDs, or real API keys.
- **Output format:** debt table ranked by risk × effort.

## 12. Create Feature Specifications

- **Purpose:** Write a spec before building.
- **When to use:** Before any new feature.
- **Prompt:** "Write a feature spec: problem, scope, non-goals, API/UI sketch,
  test plan, and explicit safety constraints (read-only, no execution). Do not
  edit files."
- **Allowed files:** read any; write only explicitly approved spec docs.
- **Forbidden files:** runtime app code; `config.json`; workflows.
- **Safety checks:** Preserve the safety invariants above; spec must include a
  non-goals section forbidding execution, orders, and live trading.
- **Output format:** structured spec with non-goals + test plan.
