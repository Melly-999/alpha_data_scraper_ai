# Graphify Agent Context Notes

## Purpose

Graphify is the local architecture and context layer for AI agents working in MellyTrade.
It helps Claude Code, Codex, OpenCode, Cursor, and Copilot understand repository structure,
relationships, and safety boundaries without changing runtime behavior.

## How To Regenerate

```bash
graphify .
```

## Generated Output

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`
- `graphify-out/graph.json`

`graphify-out/` is generated local output and must remain uncommitted unless explicitly requested.

## Recommended Future Agent Preamble

Before editing files, read `CLAUDE.md`, `graphify-out/GRAPH_REPORT.md`, and relevant docs/tasks files. Use Graphify context first. Do not guess architecture. Preserve MellyTrade safety posture: autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max risk <=1%. No execution routes, no order buttons, no broker execution, no secrets/account IDs.

## Suggested Graphify Questions

- Where are MellyTrade safety rules enforced?
- What files are related to signal scanner preview?
- How does the AI Workspace connect to scanner preview?
- What files are related to Supabase audit schema and Supabase client fallback?
- What broker registry and IBKR paper read-only files are important?
- What should an AI agent inspect before implementing SUPA-003 audit writer service?

## Query Notes

Graphify query mode was available in this install and the answers below were summarized from the graph.

### Where are MellyTrade safety rules enforced?

- Safety rules are documented in the repo guidance files `AGENTS.md` and `CLAUDE.md`.
- The graph also links safety-related terminal UI and config surfaces such as `frontend/src/lib/terminalApi.ts`.
- The graph indicates the safety posture is reinforced across project overview, configuration, secrets, and safety sections.

### What files are related to signal scanner preview?

- `app/schemas/signal_scanner.py`
- `frontend/src/lib/terminalApi.ts`
- `frontend/src/components/terminal/AIWorkspacePanel.tsx`
- `frontend/src/lib/scannerPreviewApi.ts`
- `app/services/scanner_audit.py`
- `tests/app/test_scanner_audit.py`

### How does the AI Workspace connect to scanner preview?

- The graph links `frontend/src/components/terminal/AIWorkspacePanel.tsx` to `frontend/src/lib/scannerPreviewApi.ts`.
- Scanner preview also touches `app/services/scanner_audit.py` and the scanner schema in `app/schemas/signal_scanner.py`.
- The connection is read-only and audit-oriented, not an execution path.

### What files are related to Supabase audit schema and Supabase client fallback?

- `app/schemas/audit_event.py`
- `app/services/audit_writer.py`
- `app/services/startup_audit.py`
- `app/services/signal_decision_audit.py`
- `app/services/signal_decision_persistence.py`
- `tests/app/test_audit_writer.py`

### What broker registry and IBKR paper read-only files are important?

- `brokers/broker_interface.py`
- `brokers/ibkr_config.py`
- `brokers/ibkr_readonly_client.py`
- `brokers/ibkr_paper_readonly.py`
- `brokers/xtb_broker.py`
- `tests/app/test_ibkr_readonly_client.py`
- `tests/app/test_ibkr_registry_readonly_client.py`

### What should an AI agent inspect before implementing SUPA-003 audit writer service?

- `app/services/audit_writer.py`
- `app/schemas/audit_event.py`
- `app/services/scanner_audit.py`
- `app/services/signal_decision_audit.py`
- `app/services/startup_audit.py`
- `tests/app/test_audit_writer.py`
- Existing audit event and persistence patterns before adding new writers

## Graphify Output Notes

- `graphify-out/GRAPH_REPORT.md` was generated successfully.
- `graphify-out/graph.json` was generated successfully.
- `graphify-out/graph.html` was skipped by Graphify because the graph exceeded the HTML visualization node limit.
- `graphify-out/` stays ignored and uncommitted by policy unless explicitly requested.
