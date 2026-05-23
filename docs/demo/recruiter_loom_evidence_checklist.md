# Recruiter Loom Evidence Checklist

Recording goal: create a public-safe 3-5 minute Loom that helps a recruiter understand MellyTrade as a portfolio project: a read-only, dry-run AI-assisted fintech workstation with visible safety posture, auditability, and supervised engineering workflow.

Target length: 3-5 minutes.

Recording date: TODO

Loom URL: TODO

Suggested title: `MellyTrade Recruiter Demo - Read-Only AI-Assisted FinTech Workstation`

Suggested description:

```text
Short recruiter walkthrough of MellyTrade / Alpha AI, a portfolio project demonstrating Python/FastAPI, React/TypeScript, read-only fintech UI, risk guardrails, audit/event UX, and supervised AI-assisted engineering. This is dry-run/read-only only: no live trading, no broker execution, no order routes, no order buttons, and no connect-live UX.
```

## Pre-Recording Checklist

- Start from a clean browser profile or hide bookmarks, extensions, notifications, and personal tabs.
- Use the public-safe local demo only; do not connect to real broker accounts.
- Confirm the app is in read-only/dry-run mode before recording.
- Confirm safety badges are visible: READ ONLY, DRY RUN, AUTO TRADE OFF, LIVE ORDERS BLOCKED.
- Keep the outside-repo screenshots folder available only as reference: `C:\AI\MellyTrade_Workspace\screenshots\recruiter-demo-pack\20260523-183134`.
- Open `docs/demo/recruiter_loom_demo_script.md` on a second screen or printed note, not in the recorded window if it contains local paths.
- Close private CV files, email, messaging apps, terminals with secrets, broker apps, password managers, and unrelated browser tabs.
- Disable desktop notifications before recording.

## Route Walkthrough Order

| Step | Route/page | What to show | Recruiter value |
|---:|---|---|---|
| 1 | `README.md` / repo overview | `For Recruiters` section, stack, 3-minute review path, safety posture | Shows documentation quality and how to review the project quickly. |
| 2 | `/terminal` | Terminal shell, safety banner, degraded/fallback posture, execution-denied sidebar | Shows product polish and safety-first UX. |
| 3 | `/workspace` | AI Workspace, advisory-only framing, human review language | Shows supervised AI-assisted workflow without autonomous execution claims. |
| 4 | `/signals` | Signal thesis/evidence, confidence/risk context, no execution controls | Shows explainable signal review and decision-support framing. |
| 5 | `/risk` | Risk guardrails, max risk <=1%, autotrade false, dry_run/read_only posture | Shows fintech safety discipline. |
| 6 | `/brokers` | Broker read-only/degraded state, orders denied, execution disabled | Shows safe broker-status design without live broker execution. |
| 7 | `/audit` | Safety events, timestamps, status changes, audit feed | Shows observability and audit-first UX. |
| 8 | `/portfolio` | Paper/read-only portfolio view with no order controls | Shows read-only portfolio state without execution affordances. |

## What To Show

- Safety badges and safety posture before any feature walkthrough.
- The project as a portfolio/demo workstation, not a production trading product.
- Read-only broker/status surfaces and degraded/fallback states.
- Risk guardrails and audit/event visibility.
- Human review and supervised AI-assisted engineering workflow.
- The validation command: `py -3.11 scripts/validate_safety_config.py`.
- The screenshot inventory and evidence notes if useful:
  - `docs/demo/recruiter_screenshot_inventory.md`
  - `docs/demo/recruiter_demo_evidence_notes.md`

## What Not To Show

- Private email, phone number, home address, or private CV files.
- Secrets, tokens, API keys, passwords, private keys, `.env` files, or credential managers.
- Broker account IDs, private broker dashboards, real balances, account values, or transaction history.
- Desktop notifications, browser bookmarks with personal information, private chats, or personal tabs.
- Any UX implying live trading, broker execution, order placement, or connect-live flows.
- Any statement that MellyTrade is a commercial fintech product or production client deployment.
- Any claim that AI wrote the code.
- Any claim of autonomous execution, guaranteed trading results, or financial advice.

## Privacy Redaction Checklist

- Browser bookmarks hidden or clean profile used.
- Notification banners disabled.
- No private local filesystem path shown unless intentionally public-safe and already documented.
- No private CV or career notes visible.
- No private contact details visible.
- No secrets, tokens, API keys, or environment variables visible.
- No broker account ID or real account data visible.
- No real balances or account values visible.
- No signed-in private GitHub/account UI visible unless reviewed as public-safe.

## Safety Checklist

- `autotrade=false` is stated or visible.
- `dry_run=true` is stated or visible.
- `read_only=true` is stated or visible.
- `live_orders_blocked=true` is stated or visible.
- Max risk <=1% is stated or visible.
- No order buttons are shown.
- No order routes are shown.
- No broker execution is used.
- No connect-live UX is shown.
- Human review is mentioned for AI-assisted workflows.

## Final Self-Review Checklist

- The recording is 3-5 minutes or close enough to remain recruiter-friendly.
- The first 30 seconds make clear this is a portfolio project, read-only, and dry-run.
- The recording does not expose private contact data, secrets, broker data, or private CV files.
- The recording does not imply live trading, autonomous execution, financial advice, or profit guarantees.
- The recording says AI tools were used as supervised engineering assistants, not that AI wrote the code.
- The recording shows the strongest evidence: terminal overview, AI Workspace, signals, risk, brokers, audit, portfolio, README/docs.
- The video file is stored outside the repository.
- Only a public-safe Loom link may be added to repo docs later after manual review.

## Evidence Status

- Loom recording: TODO
- Public-safe Loom link added to repo: TODO
- Manual privacy review completed: TODO
- Manual safety review completed: TODO
- Reviewer/date: TODO
