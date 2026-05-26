# DEMO-010 — Portfolio / LinkedIn Copy Pack

## Purpose

Ready-to-use copy blocks for the MellyTrade Paper Run Preview + iPad PWA milestone.

Use these blocks as-is or adapt lightly for your profile and platform.

Read the [Do not claim](#10-do-not-claim) section before publishing anything externally.

---

## Milestone covered

- Paper Run Preview panel (frontend + backend)
- `GET /paper/decision/preview` and `GET /paper/run/preview` endpoints
- Risk-gated paper service layer
- iPad Safari PWA install smoke test (Add to Home Screen, standalone launch)
- iOS input/select zoom fix
- Safety posture: `autotrade=false` · `dry_run=true` · `live_orders_blocked=true`

---

## 1. LinkedIn Post — Polish

Zbudowałem/am panel Paper Run Preview dla MellyTrade — read-only podgląd paper tradingu działający jako PWA na iPadzie.

Backend (FastAPI) udostępnia wyłącznie endpointy GET. Brak mutacji, brak połączenia z brokerem, brak wykonywania zleceń. Frontend (React + TypeScript) wyświetla wynik w izolowanym panelu z chipami stanu bezpieczeństwa.

Terminal przeszedł smoke test na iPadzie: Add to Home Screen działa, standalone PWA uruchamia się bez przeglądarki, zoom iOS na inputach i selectach jest zablokowany.

Postura bezpieczeństwa: `autotrade=false`, `dry_run=true`, brak live tradingu.

Stack: Python · FastAPI · React · TypeScript · Vite · PWA.

---

## 2. LinkedIn Post — English

Built the Paper Run Preview panel for MellyTrade — a read-only paper trading preview installable as a PWA on iPad, smoke-tested end to end.

The FastAPI backend exposes GET-only endpoints. No broker mutations, no order execution, no live trading surface. The React/TypeScript frontend renders the result in an isolated panel with safety state chips.

iPad smoke test passed: Add to Home Screen works, standalone PWA launches without browser chrome, iOS input/select zoom is suppressed.

Safety posture: `autotrade=false` · `dry_run=true` · no live orders.

Stack: Python · FastAPI · React · TypeScript · Vite · PWA.

---

## 3. Short CV/Portfolio Bullet — Polish

Zbudowałem/am read-only Paper Run Preview panel dla MellyTrade: FastAPI, React/TypeScript, GET-only endpointy, risk-gated service layer, smoke test iPad PWA (Add to Home Screen, standalone launch), postura bezpieczeństwa: dry-run, brak wykonania zleceń brokera.

---

## 4. Short CV/Portfolio Bullet — English

Built a read-only Paper Run Preview panel for MellyTrade: FastAPI backend, React/TypeScript frontend, GET-only endpoints, risk-gated service layer, iPad PWA smoke-tested (Add to Home Screen and standalone launch), safety posture: dry-run, no broker execution.

---

## 5. Project Summary — Polish (3–5 sentences)

MellyTrade Paper Run Preview to read-only panel podglądu paper tradingu zintegrowany z safety-first terminalem webowym. Backend (FastAPI) udostępnia wyłącznie endpointy GET — `/paper/decision/preview` i `/paper/run/preview` — bez mutacji danych brokerskich i bez wykonywania zleceń. Frontend (React/TypeScript) wyświetla wynik w izolowanym panelu z widocznymi chipami stanu: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `HUMAN REVIEW REQUIRED`, `EXECUTION OFF`. Panel przeszedł smoke test na iPadzie jako zainstalowana PWA — Add to Home Screen działa, tryb standalone uruchamia się bez chrome przeglądarki, a zoom iOS na polach tekstowych i selectach jest zablokowany przez wymuszenie font-size ≥ 16 px. Projekt stanowi portfolio prototyp demonstrujący safety-first podejście do projektowania API i frontendu, a nie system live tradingowy.

---

## 6. Project Summary — English (3–5 sentences)

MellyTrade Paper Run Preview is a read-only paper trading panel integrated into a safety-first web terminal. The FastAPI backend exposes GET-only endpoints — `/paper/decision/preview` and `/paper/run/preview` — with no broker data mutations and no order execution. The React/TypeScript frontend renders results in an isolated panel with visible safety state chips: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `HUMAN REVIEW REQUIRED`, `EXECUTION OFF`. The terminal passed an iPad smoke test as an installed PWA: Add to Home Screen works, standalone launch opens without browser chrome, and iOS input/select zoom is suppressed by enforcing font-size ≥ 16 px. The project is a portfolio prototype demonstrating safety-first API and frontend design, not a live trading system.

---

## 7. GitHub README Mini-Blurb — Polish

**Paper Run Preview (iPad PWA)**

Read-only panel podglądu paper tradingu. Backend udostępnia wyłącznie endpointy GET — brak wykonania zleceń, brak dostępu do danych brokerskich. Przeszedł smoke test na iPadzie: Add to Home Screen działa, tryb standalone uruchamia się bez chrome przeglądarki. Postura bezpieczeństwa: `autotrade=false` · `dry_run=true` · `live_orders_blocked=true`.

---

## 8. GitHub README Mini-Blurb — English

**Paper Run Preview (iPad PWA)**

Read-only paper trading preview panel. Backend exposes GET-only endpoints — no order execution, no broker data access. iPad PWA smoke-tested: Add to Home Screen and standalone launch work. Safety posture: `autotrade=false` · `dry_run=true` · `live_orders_blocked=true`.

---

## 9. Recruiter-Safe Explanation

### What the feature does

The Paper Run Preview panel fetches a simulated paper trading run result from the backend and displays it in a read-only panel inside the MellyTrade terminal. The user can load or refresh the preview. There are no order placement, broker execution, or connect-live controls anywhere in the panel.

### What technologies it demonstrates

| Area | Detail |
|---|---|
| FastAPI | GET-only API endpoints with typed Pydantic response schemas |
| React + TypeScript | Panel component, local state, typed props and API responses |
| Vite | Frontend build, dev server configuration, proxy setup |
| PWA | Web App Manifest, `apple-mobile-web-app-title`, status bar meta, icon set |
| iOS UX | `font-size: 16px` enforcement to prevent iOS Safari input zoom on tap |
| Safety-first design | Risk-gated service layer, safety chip UI, read-only API surface |
| Local tooling | `scripts/validate_safety_config.py` safety posture validator |

### Why it is safe

- The backend only responds to `GET` requests — no `POST`, `PUT`, `PATCH`, or `DELETE` routes are exposed for trading operations
- No broker credentials are read or transmitted during the preview
- No MT5 or IBKR account data is accessed
- The safety configuration (`autotrade=false`, `dry_run=true`) is enforced and verified by `scripts/validate_safety_config.py`
- The iPad smoke test ran on a local LAN only — the backend remained on `127.0.0.1` loopback at all times and was never exposed to the public internet

### What it does NOT claim

- Does not claim live trading capability
- Does not claim broker connectivity or order placement
- Does not claim real execution of any kind
- Does not claim profitability or alpha generation
- Does not claim App Store or TestFlight release
- Does not claim production trading readiness
- Does not claim any real money is involved
- Does not claim investment or financial advice

---

## 10. Do Not Claim

The following claims are **false and must not appear** in any public or portfolio communication about this feature:

| Forbidden claim | Why it is false |
|---|---|
| "Live trading" | No live orders are placed; dry-run only |
| "Broker execution" | No broker API calls that submit orders |
| "Guaranteed profit" | No trading algorithm runs in production |
| "Production trading readiness" | This is a paper/demo prototype only |
| "App Store release" | Not submitted to or available on the App Store |
| "TestFlight release" | Not available on TestFlight |
| "Real money trading" | No real money is involved; paper mode only |
| "Investment advice" | This is a technical portfolio project, not advisory content |
| "Financial advice" | Same — engineering showcase only, not regulated advice |
| "Public backend" | Backend remained loopback-only during testing |

Safe substitute phrases:

| Instead of | Use |
|---|---|
| "live trading" | "paper trading preview" or "read-only simulation" |
| "broker execution" | "GET-only endpoint" or "no-execution surface" |
| "production ready" | "portfolio prototype" or "local workstation" |
| "App Store app" | "PWA installable via Add to Home Screen on Safari" |
| "real returns" | do not mention at all |

---

## 11. Hashtags

### Polish LinkedIn hashtags

```
#programowanie #python #fastapi #react #typescript #pwa #fintech #portfolio #bezpieczenstwo #webdev
```

### English LinkedIn hashtags

```
#python #fastapi #react #typescript #pwa #fintech #portfolio #safetyfirst #webdev #tradingtech
```

---

## Safety Posture Reference

This copy pack describes a feature operating under the following safety constraints:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
max risk <=1%
```

These constraints are verified by `scripts/validate_safety_config.py`.

---

## Related Documents

- [iPad PWA Paper Run Preview Showcase](../showcase/ipad_pwa_paper_run_preview.md)
- [DEMO-009 smoke evidence](demo_009_ipad_pwa_smoke_evidence.md)
- [DEMO-009 screenshot checklist](demo_009_ipad_pwa_screenshot_checklist.md)
- [iPad PWA smoke test guide](../devices/ipad_pwa_smoke_test.md)
