# DEMO-009 — iPad / PWA Smoke Evidence Pack

## Purpose

This document records the successful iPad / PWA smoke test for the MellyTrade read-only terminal after PR #210.

It is documentation-only evidence for QA and demo review. It does not describe live trading, broker execution, or financial performance.

## Smoke Summary

| Item | Value |
|---|---|
| Date | `2026-05-26` |
| Environment | `iPad Safari` and `installed standalone PWA` |
| Route used | `LAN` or `Tailscale` direct access to the frontend |
| Frontend URL pattern | `http://<PC-LAN-IP>:5173/terminal/paper-run-preview` |
| Backend access model | `127.0.0.1:8001` loopback only |
| Frontend access model | `0.0.0.0:5173` for local LAN / Tailscale testing only |
| Backend exposure | Not exposed directly to the LAN |

## PASS Checklist

- [x] Page loads on iPad
- [x] Terminal / workspace opens
- [x] Paper Run Preview panel renders
- [x] All text / number inputs do not zoom
- [x] Side select does not zoom
- [x] Load / Refresh Preview works
- [x] Safety chips visible:
  - `READ ONLY`
  - `DRY RUN`
  - `LIVE ORDERS BLOCKED`
  - `HUMAN REVIEW REQUIRED`
  - `EXECUTION OFF`
- [x] No broker prompts
- [x] No `Buy` / `Sell` / `Execute` / `Place Order` controls
- [x] Add to Home Screen works
- [x] Standalone PWA launch works

## Safety Statement

This smoke test stayed within the read-only safety posture:

- no live execution
- no broker credentials
- no MT5 account data
- no IBKR account data
- dry-run only
- read-only only
- backend remained on `127.0.0.1` loopback only
- no public exposure

The test is evidence of UI behavior only. It is not a claim of trading capability, profitability, or execution readiness.

## Screenshot Evidence Notes

No binary screenshots are stored in this repository for this task.

If a future review attaches image assets, the following capture points are the intended evidence set:

- iPad Safari URL loaded
- Paper Run Preview panel
- safety chips
- no zoom proof / input focus
- Side select open / focused
- Add to Home Screen flow
- standalone PWA home screen icon
- standalone PWA launched
- optional allowed preview result
- optional blocked preview result

## Portfolio / README Usage Note

This evidence pack may be cited as a safe read-only PWA demo artifact.

Do not use it to imply live trading, broker execution, guaranteed profit, or any public exposure of sensitive account data.

## Review Notes

- The backend stayed loopback-only.
- The frontend was reachable over LAN / Tailscale for the iPad smoke test.
- This document is intentionally text-only and repository-safe.
