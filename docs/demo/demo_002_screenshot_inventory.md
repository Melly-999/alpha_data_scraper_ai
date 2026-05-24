# DEMO-002 Screenshot Inventory

Reviewer-facing inventory for the MellyTrade Terminal screenshot pack.
This is a checklist only. No image files are committed here.

| Screenshot ID | Route | Viewport | Purpose | Must show | Safety checks | Notes |
|---|---|---|---|---|---|---|
| `01_terminal_ai_workspace_1366x768.png` | `/terminal` | `1366x768` | Main Terminal / AI Workspace hero shot | red-black frame, AI Workspace, safety banner | no overflow, no order controls, no live trading UX | hero image |
| `02_terminal_paper_sandbox_preview_1366x768.png` | `/terminal` | `1366x768` | Preview the paper sandbox state | Paper Sandbox Preview, safe badges | GET-only, read-only, dry run | use only display state |
| `03_terminal_activity_audit_rail_1366x768.png` | `/terminal` | `1366x768` | Show activity / audit rail | Paper Sandbox Activity / Audit Rail, recent events | no broker execution, no order buttons | paired with preview shot |
| `04_signals_readonly_1366x768.png` | `/signals` | `1366x768` | Read-only signal overview | signal review, decision history, lifecycle | read-only labels, no live trading | suitable for README |
| `05_brokers_readonly_1366x768.png` | `/brokers` | `1366x768` | Broker posture snapshot | disconnected / safe broker state | no connect-live, no execute controls | avoid any credentials |
| `06_portfolio_readonly_1366x768.png` | `/portfolio` | `1366x768` | Portfolio presentation shot | portfolio summary / read-only cards | no account IDs, no order actions | good for recruiter view |

## Review checklist

- [ ] Screenshot uses the documented viewport
- [ ] Safety badges are visible
- [ ] No horizontal overflow
- [ ] No live trading UX
- [ ] No broker execution controls
- [ ] No order / buy / sell / execute buttons
- [ ] No secrets or account IDs
- [ ] Captured output matches the filename

## Publication notes

- Keep filenames lowercase and descriptive.
- Keep screenshots lossless if possible.
- Do not include browser DevTools in final shots unless the shot is
  intentionally about debugging.
- Do not publish any image showing `LIVE` or an executed order.

## DEMO-007 / POST-SIG-004B signal quality UI evidence

Evidence doc (in repo):
`docs/demo/demo_008_post_sig_004b_signal_quality_evidence.md`

Outside-repo evidence folder:
`C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui\`

Outside-repo manifest:
`C:\AI\MellyTrade_Workspace\screenshots\demo-007-post-sig-004b-signal-quality-ui\manifest.md`

Primary screenshots:

- `01_dashboard_post_sig_004b_1366x768.png`
- `02_workspace_signal_quality_card_1366x768.png`
- `03_terminal_signal_quality_card_1366x768.png`
- `04_signals_post_sig_004b_1366x768.png`
- `05_audit_post_sig_004b_1366x768.png`
- `06_brokers_post_sig_004b_1366x768.png`
- `07_portfolio_post_sig_004b_1366x768.png`

Supplementary screenshots:

- `01b_dashboard_fullpage.png`
- `02_signal_quality_card_visible_1366x768.png`
- `02b_workspace_fullpage.png`
- `02c_workspace_scrolled.png`
- `03_signal_quality_card_visible_1366x768.png`
- `03b_terminal_fullpage.png`
- `03c_terminal_scrolled.png`

These screenshot files are not committed to the repository. They remain outside the repository as local demo evidence.
