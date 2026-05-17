# MellyTrade Closed Beta — Quick Start Guide

> **Advisory only.** MellyTrade is a read-only AI research terminal.
> It does not place orders, route trades, or provide investment advice.
> All outputs are educational and observational.

---

## What you are accessing

MellyTrade Closed Beta v0.1 is a local read-only trading research terminal.
It shows AI signal previews, market overviews, risk posture, and audit events —
all in dry-run / advisory mode.

**Safety posture (enforced at all times):**

```
autotrade    = false
dry_run      = true
read_only    = true
live_orders_blocked = true
max risk     <= 1%
```

---

## System requirements

| Item | Minimum |
|---|---|
| OS | Windows 10/11, macOS 12+, Ubuntu 22+ |
| Node | 18 LTS or newer |
| Python | 3.11 or 3.12 |
| Browser | Chrome / Firefox / Edge (latest) |
| RAM | 4 GB free |
| Disk | 500 MB free |

No MetaTrader5 or live broker account is required for the demo.

---

## Step 1 — Get the code

You will receive a private repository invitation.
Accept it and clone:

```bash
git clone https://github.com/Melly-999/alpha_data_scraper_ai.git
cd alpha_data_scraper_ai
```

---

## Step 2 — Start the backend

```bash
# Install Python dependencies (CI-safe set, no MT5/TF required)
pip install -r requirements-ci.txt

# Start the FastAPI backend
python main.py
```

Expected output on a healthy start:

```
INFO  backend_started        — MellyTrade Phase 1 backend started
INFO  dry_run_active         — dry_run=true, all execution paths blocked
INFO  read_only_mode_confirmed — operating in read-only observability mode
INFO  autotrade_disabled     — autotrade.enabled=false
INFO  live_orders_blocked    — supports_live_orders=false
```

The backend will run on `http://localhost:8000` by default.

---

## Step 3 — Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Step 4 — Verify safety status

When the terminal loads you should see:

- **DRY RUN** safety banner at the top
- **ADVISORY ONLY — NO EXECUTION** labels on all scanner cards
- Broker status showing **IBKR Paper — read-only** or **degraded (safe)**
- No order, cancel, or modify buttons anywhere in the UI

If any of those are missing, do not proceed — report it as a bug using the
template at `docs/product/closed_beta_bug_report_template.md`.

---

## Step 5 — Explore the terminal

| Panel | What to look at |
|---|---|
| **Market Overview** | Signal chips (HOLD / WATCH), confidence bars |
| **AI Scanner Workspace** | Scanner preview cards with action labels and confidence |
| **Risk Manager** | Risk posture (read-only, all gates locked) |
| **Audit / Event Rail** | Live audit events, safety confirmations |
| **Broker Status** | IBKR Paper read-only connector status |

All data shown is demo / fallback data unless your local backend is connected
to a live paper data source. No live quotes are required.

---

## Step 6 — Submit feedback

Use the feedback guide at `docs/beta/beta_tester_feedback_guide.md`.

Report bugs using the template at
`docs/product/closed_beta_bug_report_template.md`.

---

## Known limitations

See `docs/product/closed_beta_limitations.md` for the full list.

Key points:

- No live broker connection in the demo (safe fallback data only)
- No production auth/login screen yet
- No mobile layout (desktop browser required)
- Scanner results are advisory labels only — no execution surface exists

---

## Disclaimer

MellyTrade is an experimental research tool.
It does not constitute financial or investment advice.
Past performance is not indicative of future results.
All outputs are for educational and observational purposes only.

See `docs/product/closed_beta_disclaimer.md` for the full disclaimer.

---

*MellyTrade Closed Beta v0.1 — Read-only advisory terminal*
