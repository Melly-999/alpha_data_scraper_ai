# docs/assets/screenshots — MellyTrade Demo Screenshots

This directory holds portfolio- and showcase-ready screenshots of the
MellyTrade Read-Only AI Operations Layer (MERGE #100).

Every screenshot in this directory must satisfy the safety contract below
before it is committed. Files not yet captured are listed as **planned**.

---

## Safety contract (must pass before commit)

- [ ] No secrets, API keys, or tokens visible
- [ ] No Supabase service-role key values visible
- [ ] No account IDs, broker account numbers, or real credentials
- [ ] No order IDs or execution IDs
- [ ] No personal data (names, emails, account numbers)
- [ ] Safety banner visible and reads: `DRY RUN · READ-ONLY MODE · LIVE ORDERS BLOCKED · MAX RISK ≤ 1%`
- [ ] No `LIVE` indicator anywhere on the page
- [ ] No text claiming an order was placed or executed
- [ ] Browser DevTools closed (unless the shot specifically shows network panel)

---

## Naming convention

```
NN-description-of-subject.png
```

- `NN` — zero-padded two-digit sequence number (01, 02, …)
- `description-of-subject` — lowercase, hyphen-separated noun phrase
- Extension: `.png` (lossless, preferred) or `.webp` (acceptable for web)

Do **not** use underscores, spaces, or uppercase in filenames.

---

## Viewport and capture settings

| Setting | Value |
|---|---|
| Browser | Chrome or Edge (Chromium) |
| Window width | 1440 px (minimum) — 1600 px preferred |
| Window height | 900–1000 px |
| Browser zoom | 90–100% |
| DevTools | Closed |
| Theme | Default dark |
| Hard refresh before capture | Yes (Ctrl+Shift+R) |
| Format | PNG, lossless |

---

## Screenshot inventory

| File | Subject | Route | Status |
|---|---|---|---|
| `01-terminal-ai-workspace.png` | Full dashboard: safety banner, system status, equity curve, activity feed | `/dashboard` | planned |
| `02-signal-decision-history-filters.png` | Decision History card with 1H quick-range chip active, freshness label, filter controls | `/signals` | planned |
| `03-signal-reasoning-panel.png` | AI Reasoning panel open in drawer — all four safety badges, confidence breakdown, risk gates | `/signals` (drawer) | planned |
| `04-audit-feed-safety-events.png` | Audit feed with `stale_data_warning`, `scanner_evaluated`, `risk_blocked` rows visible | `/audit` | planned |
| `05-supabase-status-and-stale-indicators.png` | Decision History freshness label in stale state, `seed data` or `live data` badge | `/signals` | planned |
| `06-broker-readonly-guardrails.png` | Risk manager or broker card showing `dry_run=true`, `auto_trade=false`, guardrail values | `/risk` or `/dashboard` | planned |
| `07-demo-overview.png` | Full Signals page: Signal Review + Decision History + Lifecycle stacked (overview shot) | `/signals` | planned |

Full capture requirements per screenshot are in
[`../demo/demo_screenshot_checklist.md`](../demo/demo_screenshot_checklist.md).

Full capture runbook is in
[`../demo/demo_002_capture_runbook.md`](../demo/demo_002_capture_runbook.md).

---

## Captioning template

Use this caption whenever a screenshot is published externally (GitHub,
LinkedIn, OpenAI Showcase, portfolio):

> *MellyTrade Read-Only AI Ops Layer — `[page name]`. Display-only:
> `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, max risk ≤ 1%. No live trading. No live
> broker execution.*

---

## What this directory is NOT for

- Live trading screenshots (the system cannot produce them)
- Screenshots containing real broker credentials
- Altered or composited images
- Screenshots from a non-read-only configuration
