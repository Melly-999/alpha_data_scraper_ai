# IBKR Paper Adapter (v1)

A **paper / dry-run first** Interactive Brokers adapter that plugs into
the safe broker-adapter architecture. The existing MetaTrader5 path is
unchanged, all safety defaults are preserved, and live trading remains
explicitly blocked.

## What this adapter does

* Imports cleanly even when `ib_insync` is **not installed** (CI default).
* Defaults to the **paper TWS port `7497`** on `127.0.0.1` with `clientId=1`.
* Reads non-secret configuration from environment variables / `.env`.
* Exposes a typed surface for the FastAPI app:
  * `health()` -> `BrokerHealth`
  * `account_snapshot()` -> `BrokerAccountSnapshot`
  * `submit_dry_run_report(decision)` -> `BrokerExecutionReport`
* Refuses to connect to a live TWS / IB Gateway port unless an explicit
  override is set (still a no-op for live order placement in v1).
* Handles `ib_insync` missing, TWS not running, wrong port, stale
  connection and accidentally-selected live ports - none of these crash
  the FastAPI app.

## What this adapter does not do

* It does **not** place real orders. `supports_live_orders()` always
  returns `False`.
* It does **not** read or store credentials. Log into PaperTrader
  manually inside TWS or IB Gateway.
* It does **not** replace the MT5 path. Existing `mt5_trader.py` /
  `mt5_fetcher.py` keep working untouched.
* It does **not** weaken any risk gate, cooldown, drawdown guard,
  duplicate-signal guard, max-open-position limit, or SL/TP requirement.

## Optional dependency

```powershell
pip install ib_insync==0.9.86
```

`ib_insync` is already pinned in `requirements.txt`. CI uses
`requirements-ci.txt` which intentionally does **not** install it - the
adapter must keep returning a typed `missing_dependency` health on CI.

If installation is risky in a particular environment, leave it out and
the adapter will report:

```json
{ "connected": false, "status": "missing_dependency", "last_error": "missing_dependency: ib_insync not installed" }
```

## TWS Paper setup checklist

1. Download and install IB Trader Workstation (TWS).
2. Log in with **PaperTrader** credentials (not the live account).
3. `Edit -> Global Configuration -> API -> Settings`:
   * Enable **ActiveX and Socket Clients**.
   * Verify socket port is **`7497`**.
   * Trusted IP: `127.0.0.1`.
   * **Read-Only API** = on for v1.
4. Restart TWS so the API listener picks up the change.
5. Verify connection from this app via `GET /api/broker/health`.

### IB Gateway alternative

* Same flow, port **`4002`** for paper.
* Live ports `7496` (TWS) and `4001` (Gateway) remain blocked.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `BROKER_ADAPTER` | `mt5_demo` | Active adapter for the safe paper-broker factory |
| `IBKR_ENABLED` | `false` | Master switch for the IBKR adapter |
| `IBKR_MODE` | `paper` | Must stay `paper` in v1 |
| `IBKR_HOST` | `127.0.0.1` | TWS / Gateway host |
| `IBKR_PORT` | `7497` | Paper TWS port |
| `IBKR_CLIENT_ID` | `1` | API client id |
| `IBKR_ACCOUNT` | (empty) | Optional paper account label |
| `IBKR_READ_ONLY` | `true` | Must stay true in v1 |
| `IBKR_ALLOW_PAPER_ORDERS` | `false` | Future-work gate, not used in v1 |
| `IBKR_ALLOW_LIVE_ORDERS` | `false` | Hard gate, ignored by v1 (live remains blocked) |
| `IBKR_MAX_ORDER_VALUE` | `100` | Future safety cap |
| `IBKR_MAX_POSITION_VALUE` | `100` | Future safety cap |

Never store credentials, account numbers, usernames or passwords in
`.env` or in this repo - the adapter never reads them.

## Backend run commands

```powershell
# Run the FastAPI app (works without ib_insync / without TWS)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# Smoke-test the safe broker surface
curl http://127.0.0.1:8001/api/broker/health
curl http://127.0.0.1:8001/api/broker/account
curl -X POST http://127.0.0.1:8001/api/broker/dry-run-report `
     -H "Content-Type: application/json" `
     -d "{ \"decision_id\": \"demo-001\", \"symbol\": \"AAPL\", \"direction\": \"BUY\", \"confidence\": 72 }"
```

To switch the adapter to IBKR paper:

```powershell
$env:BROKER_ADAPTER = "ibkr-paper"
$env:IBKR_ENABLED   = "true"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

The example runner can also exercise the path without TWS:

```powershell
python example_runner.py --broker ibkr-paper --symbols AAPL MSFT
```

## What remains blocked before live

* Live order placement (`supports_live_orders()` returns `False`).
* Live ports `7496` (TWS) and `4001` (Gateway) are refused unless
  `IBKR_ALLOW_LIVE_ORDERS=true`, and even then the v1 adapter still
  short-circuits to a typed block reason.
* `autotrade.enabled` stays `false` and `dry_run` stays `true` in
  `config.json`.
* The risk state machine, duplicate-signal guard, cooldown, drawdown
  guard and max-open-position limit are unchanged.

## Future live checklist (not implemented in v1)

Before any future live patch is merged the following must be true:

- [ ] At least 2 weeks of continuous paper running with stable health.
- [ ] Reconnect / disconnect behaviour exercised under TWS restarts.
- [ ] Audit-grade structured logs for every order submission.
- [ ] Manual approval mode (per-decision human ack) is added.
- [ ] Position sizing capped at the configured `IBKR_MAX_POSITION_VALUE`.
- [ ] An explicit, reviewed live-trading patch toggles
      `supports_live_orders()` and unblocks live ports.
- [ ] Legal / tax / risk review signed off by the operator.

The optional `place_paper_bracket_order()` helper currently always
returns a refusal and is documented as future work.
