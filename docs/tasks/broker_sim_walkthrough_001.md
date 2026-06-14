# Broker-Sim Walkthrough 001

SOURCE STATUS: Public-safe, docs-only walkthrough. No secrets, no credentials,
no account IDs. This document explains how to run and present the **read-only
simulated broker preview**. It does not implement, enable, or recommend any live
broker execution.

> **This is not live trading.** Nothing here connects to a real broker, places
> orders, executes trades, or requires credentials. Everything shown is
> read-only, dry-run, paper/demo data only.

## 1. Purpose

Give a presenter (you) a clear, repeatable way to demo the simulated broker
preview to a recruiter, client, or reviewer — and to do it safely, without ever
implying live trading. It ties together the work already merged:

- [broker_sim_readiness_audit_001.md](broker_sim_readiness_audit_001.md) — readiness classification **B**.
- [broker_sim_readonly_smoke_001.md](broker_sim_readonly_smoke_001.md) — the GET-only smoke + evidence.

## 2. What this demo is

- A **read-only** view of broker / account / position / order *preview* surfaces,
  served from local / demo / fallback data.
- A **GET-only smoke** that proves the surface is safe: safety flags hold, every
  read-only endpoint responds, and no sensitive fields leak.
- A portfolio artifact showing disciplined, safety-first engineering.

## 3. What this demo is not

- **Not** live trading, and **not** a live trading bot.
- **Not** connected to a real broker; uses **no** credentials and **no** broker auth.
- **Not** placing, submitting, or cancelling orders; **no** trade execution.
- **Not** production trading-ready; **not** financial advice.
- **No** Buy / Sell / Order / Execute controls exist anywhere in the UI.

## 4. Safety posture

The surface preserves, and the smoke asserts:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
max_risk_per_trade <= 1%
no broker execution
no live trading UX
```

These appear in the UI as visible chips: **READ ONLY**, **DRY RUN**,
**LIVE ORDERS BLOCKED**, **EXECUTION OFF**.

## 5. Before you start

- A local backend (and, for the UI portion, the frontend) — see
  `scripts/start_backend_local.ps1` / `scripts/start_frontend_local.ps1`.
- PowerShell 7+ for the smoke script.
- No credentials, no `.env`, no broker account needed. If you have none of that,
  the demo still works — that is the point.
- You do **not** need a live backend to talk about safety: the smoke exits
  cleanly (SKIP) when offline, and this doc plus the merged evidence already
  document a green run.

## 6. How to run the read-only smoke

```powershell
# Local backend (default base URL http://127.0.0.1:8001)
.\scripts\broker_sim_readonly_smoke.ps1

# Custom / hosted backend, GET-only
.\scripts\broker_sim_readonly_smoke.ps1 -BaseUrl https://your-backend.example.com -TimeoutSec 15
```

Parameters: `-BaseUrl <url>` (default local), `-TimeoutSec <int>` (default 8).
Exit codes: `0` = read-only surface safe **or** backend offline (degraded SKIP);
`1` = a hard safety failure (an unsafe flag value, or a forbidden field in a
response). The script is **GET-only** — it never issues POST/PUT/PATCH/DELETE.

## 7. How to open the UI

Start the frontend, then open (in order):

1. `/terminal` — the safety banner + terminal summary.
2. `/brokers` — read-only broker status (e.g. `safe-disconnected`, `ibkr-paper`).
3. `/terminal/paper-run-preview` — paper run preview (read-only / dry-run).

If a route is not present in your build, skip it and narrate from the smoke
output instead — the safety story does not depend on any single screen.

## 8. Recommended demo path

1. **Lead with safety.** Point at the READ ONLY / DRY RUN / LIVE ORDERS BLOCKED /
   max-risk≤1% chips before anything else.
2. **Run the smoke:** `scripts/broker_sim_readonly_smoke.ps1`.
3. **Show the result:** safety status, broker adapters, account / position / order
   *preview* surfaces, "no forbidden fields", "no order execution".
4. **Open the UI:** `/terminal`, then `/brokers`, then `/terminal/paper-run-preview`.
5. **Explain:** read-only broker-sim preview; no credentials; no broker auth; no
   live execution; no Buy/Sell/Execute controls; paper/demo data only.

## 9. What to show first

The **safety posture**. Open `/terminal` and let the chips speak:
READ ONLY, DRY RUN, LIVE ORDERS BLOCKED, max risk ≤ 1%. Then run the smoke and
show the top lines:

```text
[PASS] GET /api/safety/status -> HTTP 200
[PASS] safety.dry_run=True
[PASS] safety.auto_trade=False
[PASS] safety.read_only=True
[PASS] safety.live_orders_blocked=True
[PASS] safety.max_risk_per_trade_pct<=1.0  (1)
```

## 10. What to show second

The **read-only surface breadth** — broker adapters and the account / position /
order preview endpoints all returning HTTP 200 with no sensitive fields:

```text
[PASS] GET /api/brokers -> HTTP 200
[PASS] GET /api/brokers/ibkr-paper/account -> HTTP 200
[PASS] GET /api/brokers/safe-disconnected/status -> HTTP 200
[PASS] GET /api/positions/open -> HTTP 200
[PASS] GET /api/orders -> HTTP 200
...
  PASS: 47   SAFETY-FAIL: 0   WARN: 0   SKIP: 0
  RESULT: PASS -- read-only surface safe
```

Then the matching UI: `/brokers` (read-only status) and
`/terminal/paper-run-preview` (paper, dry-run).

## 11. What to avoid

- Do not click anything that looks like an action button as if it executed a
  trade — there are no Buy/Sell/Execute controls, so do not imply there are.
- Do not type real credentials or point the smoke at a real brokerage.
- Do not describe demo balances/positions as real money.
- Do not promise returns, profit, or performance.

## 12. Expected safe outcomes

- Safety flags: `dry_run=true`, `auto_trade=false`, `read_only=true`,
  `live_orders_blocked=true`, `max_risk_per_trade_pct<=1.0`.
- Every read-only endpoint returns HTTP 200 (or is absent → SKIP).
- No forbidden / sensitive fields (`account_id`, `broker_account_id`,
  `broker_order_id`, `execution_id`, `secret`, `token`, `api_key`,
  `private_key`) in any response.
- Reference run: **47 PASS / 0 SAFETY-FAIL / 0 WARN / 0 SKIP**, exit 0; adapters
  `ibkr-paper` and `safe-disconnected`.

## 13. Troubleshooting

- **"backend not reachable" / SKIPPED:** the backend is not running. Start it
  (`scripts/start_backend_local.ps1`) and re-run, or present from the recorded
  evidence — offline is a documented degraded state, not a failure.
- **A route returns 404 / SKIP:** that route is not in this build; narrate from
  the smoke output and the other screens.
- **A `[FAIL]` line appears:** stop and treat it as a real safety finding — the
  script only fails on an unsafe flag value or a forbidden field. Do not demo
  past it.
- **Script will not run:** ensure PowerShell 7+; the script is GET-only and needs
  no special permissions.

## 14. One-minute demo script

> "This is MellyTrade's broker-sim preview. Before anything else — notice it's
> **read-only** and **dry-run**, live orders are **blocked**, and per-trade risk
> is capped at **1%**. I'll run a GET-only safety smoke. It checks the safety
> flags, the broker and account preview endpoints, and scans every response for
> sensitive fields — and it passes with no order execution anywhere. Everything
> you see is **paper/demo data**. There are **no Buy/Sell/Execute controls**, no
> credentials, and no real broker connection. It's a portfolio piece about doing
> this **safely**, not a live trading system."

## 15. Three-minute demo script

> "MellyTrade is a read-only, dry-run portfolio project. Let me show how I keep
> it safe by design.
>
> First, the **safety posture**. On `/terminal` you can see the chips: READ ONLY,
> DRY RUN, LIVE ORDERS BLOCKED, max risk ≤ 1%. Those aren't decoration — they're
> enforced in config and asserted by tests.
>
> Now I'll run the **read-only smoke**: `broker_sim_readonly_smoke.ps1`. It's
> GET-only — it never sends a POST, PUT, PATCH, or DELETE. It confirms
> `dry_run=true`, `auto_trade=false`, `read_only=true`, `live_orders_blocked=true`,
> and max risk ≤ 1%. Then it walks the read-only surface — broker adapters like
> `safe-disconnected` and `ibkr-paper`, account/position/order **previews** — and
> scans every response body for things that must never appear, like account IDs,
> order IDs, secrets, or API keys. Here it's **47 checks, all passing, zero
> safety failures**.
>
> In the UI, `/brokers` shows read-only broker status, and
> `/terminal/paper-run-preview` shows a paper, dry-run preview. None of this
> places an order — there are no Buy/Sell/Execute controls, and it doesn't
> connect to a real broker or use any credentials.
>
> To be clear about scope: this is **simulated/paper-only**. It doesn't trade,
> it doesn't make money, and it's not financial advice. The next steps are
> documented and deliberately gated — real broker integration would be a
> separate, explicitly-approved effort."

## 16. What not to claim

Never say (or imply) any of these:

- "this trades for me"
- "this is a live trading bot"
- "this places orders"
- "this connects to my real broker"
- "this makes profit"
- "this has ROI / win-rate"
- "this is financial advice"
- "this is production trading-ready"

## Next tasks

- **BROKER-SIM-WALKTHROUGH-DOC-001-PUBLISH** — push this doc and open a Draft PR.
- Optional: non-required CI wiring for `broker_sim_readonly_smoke.ps1` (GET-only,
  allowed to SKIP when no backend) as a lightweight demo-health signal.
- Real broker integration remains **out of scope** — a separate, explicitly
  approved, multi-task effort.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
