# Broker-Sim Screenshot Evidence 001

SOURCE STATUS: Public-safe, docs/images-only evidence. No secrets, no
credentials, no account IDs. These screenshots show the **read-only, simulated /
demo** broker UI after the label polish. They do not show, imply, or enable any
live broker execution.

> **This is not live trading.** The screenshots show read-only / demo UI only.
> No real broker connection, no live trading, no order placement, no credentials.

## 1. Purpose

Provide a small, public-safe screenshot pack capturing the safe read-only
simulated broker preview after the paper-sim UI label polish (#306), to support
the demo walkthrough ([broker_sim_walkthrough_001.md](broker_sim_walkthrough_001.md)).

## 2. Baseline

- main / origin/main SHA: `c4f3fdf3d8a33e2683ab567ca471d29630aea7f6`
- Captured against this checkout running locally: backend GET-only API on
  `127.0.0.1:8001`, frontend dev server on `127.0.0.1:5173`. Backend was in safe
  degraded/fallback mode (MT5/IBKR not connected) — the expected demo state.
- Safety validator: `python scripts/validate_safety_config.py` → **OVERALL: PASS**
- Date: 2026-06-15

## 3. Screenshot inventory

All under `docs/assets/screenshots/broker-sim/`:

| File | Route | Shows |
|---|---|---|
| `broker-sim-terminal-safety.png` | `/terminal` | Global safety chips (READ ONLY · DRY RUN · AUTO TRADE OFF · LIVE ORDERS BLOCKED · HUMAN REVIEW REQUIRED) and the **DEMO DATA** degraded/fallback banner |
| `broker-sim-brokers-readonly-card.png` | `/brokers` | IBKR Paper read-only card: `read_only=true`, `execution_enabled=false`, permissions (Orders **denied**, Live execution **denied**), and the polished caption *"Paper / simulated — read-only preview. No live execution, no credentials, not live trading."* |
| `broker-sim-paper-run-preview.png` | `/terminal/paper-run-preview` | Paper Run Preview: GET-ONLY · DISPLAY-ONLY, chips READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · HUMAN REVIEW REQUIRED · EXECUTION OFF, and a GET-only `Load Preview` (no order placement, no persistence) |

### /terminal — safety posture

![Terminal header safety chips and DEMO DATA / read-only / dry-run / live-orders-blocked banner](../assets/screenshots/broker-sim/broker-sim-terminal-safety.png)

### /brokers — read-only broker card

![IBKR Paper read-only card: read_only=true, execution_enabled=false, orders and live execution denied, with the paper / simulated read-only caption](../assets/screenshots/broker-sim/broker-sim-brokers-readonly-card.png)

### /terminal/paper-run-preview — read-only paper run preview

![Paper Run Preview: GET-only / display-only with read-only, dry-run, live-orders-blocked, human-review, execution-off chips](../assets/screenshots/broker-sim/broker-sim-paper-run-preview.png)

## 4. Public-safety review

Each screenshot was reviewed before inclusion. Confirmed **none** of the images
show: personal data, emails, phone numbers, tokens, API keys, account IDs, real
broker data, private browser tabs, notifications, Buy/Sell/Order/Execute
controls, credential UI, or connect-live UI. All values are demo / fallback /
synthetic. The `/terminal` shot was deliberately cropped to the top of the page
so the unrelated "backtest equity preview" sample widget is **not** included.

## 5. Demo route coverage

Covers the recommended demo path from the walkthrough:

1. `/terminal` — lead with the safety posture.
2. `/brokers` — read-only broker status + the simulated/read-only caption.
3. `/terminal/paper-run-preview` — read-only / dry-run paper run preview chips.

## 6. What the screenshots prove

- The safety posture is **visible in the UI**: read-only, dry-run, auto-trade
  off, live orders blocked, human review required, max risk ≤ 1%.
- The broker surface is clearly labelled **paper / simulated / read-only**, with
  order and live-execution permissions shown as **denied**.
- The paper run preview is **GET-only / display-only** with no order placement.

## 7. What the screenshots do not prove

- They do **not** prove any live broker connectivity (there is none).
- They do **not** show real balances, real positions, or real orders.
- They are **not** performance evidence — no profit, ROI, or win-rate is claimed.
- They reflect a local demo run in safe degraded/fallback mode at a point in
  time, not a production deployment.

## 8. Safety posture

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

## 9. What not to claim

- Not live trading, not a live trading bot.
- Not connected to a real broker; no credentials.
- No order placement / execution.
- No profit, ROI, win-rate, or returns.
- Not financial advice; not production trading-ready.

## 10. Next steps

- **BROKER-SIM-SCREENSHOT-EVIDENCE-001-PUBLISH** — push this evidence pack and
  open a Draft PR.
- Optional: **DEAD-CODE-DASHBOARD-ROUTING-AUDIT-001** — decide on the unrouted
  `DashboardPage` / `BrokerCard` (separate scoped task).

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
