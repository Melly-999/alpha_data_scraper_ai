# Backend Demo Deploy Guide — Railway / Render + PWA Demo Path

## 1. Purpose

This guide documents the safest path to make MellyTrade usable as a hosted portfolio and PWA demo.

It is a planning and safety reference — **not a live trading deployment guide**.

Nothing in this document authorises live trading, broker execution, or exposure of private credentials. The safety posture documented in `config.json` and enforced by `scripts/validate_safety_config.py` must remain unchanged before, during, and after any hosted demo deployment.

---

## 2. Recommended Path

| Step | Action | Status |
|---|---|---|
| 1 | Backend demo deploy on Railway or Render | planned (this guide) |
| 2 | PWA demo from existing React / Vite frontend | ready (see §7) |
| 3 | iPad / mobile demo via browser + Add to Home Screen | ready (see §7) |
| 4 | React Native / Expo | explicitly postponed (see §8) |

The sequence matters. A stable hosted backend URL is required before a hosted PWA demo can point to it. The current LAN / Tailscale path remains a working fallback until step 1 is complete.

---

## 3. Why Backend Deploy Matters

A hosted backend gives:

- a stable API URL that does not change when the development machine sleeps or changes IP
- easier iPad testing without LAN / Tailscale configuration
- an easier recruiter / portfolio demo path — share one URL, not a setup guide
- a step toward a production-like architecture that can be validated safely

A hosted backend demo is **not**:

- production trading infrastructure
- a live execution environment
- a broker-connected trading system
- authorisation to enable live orders

The safety posture (`autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`) must be confirmed before deployment and verified again after deployment via the health / smoke endpoints.

---

## 4. Railway Checklist

> Before starting: run `py -3.11 scripts/validate_safety_config.py` and confirm OVERALL: PASS.

### 4.1 Account and project

- [ ] Create a Railway account at railway.app (free tier is sufficient for a demo backend).
- [ ] Create a new project.
- [ ] Connect the GitHub repository (`alpha_data_scraper_ai`).

### 4.2 Service configuration

- [ ] Select the repository root as the service directory (the FastAPI backend lives at the repo root under `app/`).
- [ ] Set the Python runtime. Railway auto-detects Python from `requirements.txt` or `runtime.txt`.
  `runtime.txt` is now committed at the repository root (added in DEPLOY-003A) with `python-3.11`.
  No manual runtime configuration should be required — Railway will pick it up automatically.
- [ ] Set the start command to:

  ```text
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

  Verify this against the existing local scripts (`scripts/start_backend.ps1`, `scripts/smoke-test.sh`) before deploying. Railway injects `$PORT` automatically.

- [ ] Do **not** use `--reload` in a hosted environment.
- [ ] **Dockerfile (optional):** If Railway is configured to build from a Dockerfile rather than a
  start command, use `Dockerfile.api` (added in DEPLOY-003B). Do **not** use the existing `Dockerfile`
  or `Dockerfile.prod` — those target the scheduler/bot CLI. No image has been pushed and no deploy
  has been performed as part of DEPLOY-003B.

### 4.3 Environment variables

- [ ] Add all required environment variables through the **Railway dashboard** only — never commit secrets to the repository.
- [ ] Required variables for a read-only demo (set only what the app requires to start; omit broker credentials entirely):
  - `CLAUDE_API_KEY` — only if Claude AI validation is enabled for the demo; omit if not needed.
  - `NEWSAPI_KEY` — only if news sentiment is enabled for the demo; omit if not needed.
  - Do **not** add `MT5_LOGIN`, `MT5_PASSWORD`, or `MT5_SERVER` — the demo must not connect to a broker account.
- [ ] Confirm that `autotrade.enabled` resolves to `false` in the deployed environment (the app reads from `config.json` by default; Railway does not override this automatically).

### 4.4 Health and smoke

- [ ] After deployment, call the health endpoint:

  ```text
  GET https://<railway-url>/health
  ```

  Confirm the response shows `status: ok` or equivalent.

- [ ] Call the safety endpoint if available:

  ```text
  GET https://<railway-url>/api/safety/config
  ```

  Confirm `read_only: true`, `dry_run: true`, `autotrade_enabled: false`.

- [ ] Confirm no `Buy` / `Sell` / `Execute` / `Place Order` routes appear in the OpenAPI schema:

  ```text
  GET https://<railway-url>/openapi.json
  ```

  Scan for `POST /orders`, `POST /execute`, `POST /trade` — none should be present in a read-only demo deploy.

### 4.5 What not to do on Railway

- Do not commit secrets, tokens, or API keys to the repository.
- Do not enable a `POST /orders` or execution-shaped route in the deployed config.
- Do not set `autotrade.enabled = true` in any deployed config file.
- Do not expose admin or broker-management endpoints publicly.
- Do not store `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` in Railway environment variables for a portfolio demo — broker connections are not needed for the read-only paper run preview.

---

## 5. Render Checklist

> Before starting: run `py -3.11 scripts/validate_safety_config.py` and confirm OVERALL: PASS.

### 5.1 Account and web service

- [ ] Create a Render account at render.com (free tier is sufficient for a demo backend).
- [ ] Create a new **Web Service**.
- [ ] Connect the GitHub repository (`alpha_data_scraper_ai`).

### 5.2 Service configuration

- [ ] Root directory: leave as repository root (or confirm based on existing backend run docs).
- [ ] Python version: `runtime.txt` is committed at the repository root with `python-3.11` (added in
  DEPLOY-003A). Render detects this automatically; no manual runtime selection should be required.
- [ ] Build command:

  ```text
  pip install -r requirements.txt
  ```

  If the full `requirements.txt` includes heavy ML / MT5 dependencies that do not install cleanly on Render's Linux runners, consider creating a `requirements-demo.txt` that mirrors `requirements-ci.txt` plus `uvicorn` and `fastapi`. **Do not modify backend runtime files for this task — verify the existing requirements first (DEPLOY-002).**

- [ ] Start command:

  ```text
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

  Render injects `$PORT` automatically.

- [ ] **Dockerfile (optional):** If Render is configured to build from a Dockerfile rather than a
  start command, use `Dockerfile.api` (added in DEPLOY-003B). Do **not** use the existing `Dockerfile`
  or `Dockerfile.prod`. No image has been pushed and no deploy has been performed as part of DEPLOY-003B.

### 5.3 Environment variables

- [ ] Add all required environment variables through the **Render dashboard** only — never commit secrets to the repository.
- [ ] Same variable rules as Railway (§4.3): omit broker credentials for a read-only demo.

### 5.4 Health and smoke

- [ ] After deployment, call the health endpoint:

  ```text
  GET https://<render-url>/health
  ```

- [ ] Call the safety endpoint if available:

  ```text
  GET https://<render-url>/api/safety/config
  ```

  Confirm `read_only: true`, `dry_run: true`, `autotrade_enabled: false`.

- [ ] Check the OpenAPI schema for forbidden execution routes (same as §4.4).

### 5.5 What not to do on Render

Same rules as Railway (§4.5). No secrets in git. No broker credentials in env vars for a demo. No execution routes.

---

## 6. Required Safety Checks Before Any Hosted Demo

Run these locally before deploying to any host:

```powershell
# Must return OVERALL: PASS
py -3.11 scripts/validate_safety_config.py

# Must all pass
py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py tests/app/test_safety_invariants.py -q
```

Also confirm manually:

- [ ] `autotrade.enabled` is `false` in `config.json`
- [ ] `autotrade.dry_run` is `true` in `config.json`
- [ ] No `execution_enabled=true` override exists in any deployed config file
- [ ] No broker credentials (`MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`) are present in the repository
- [ ] No account IDs or broker order IDs are committed to the repository
- [ ] No order execution routes or order buttons exist in the deployed frontend
- [ ] The backend health / safety endpoint confirms the read-only / dry-run posture after deploy
- [ ] The OpenAPI schema does not expose a live trading or order execution endpoint

---

## 7. PWA Demo Path

The current React / Vite frontend is the best mobile release path for portfolio and recruiter demos now.

### 7.1 Why PWA now

- The frontend already works as a PWA — Safari Add to Home Screen and standalone launch were verified in the DEMO-009 iPad smoke test.
- No App Store submission required.
- No Google Play submission required.
- No TestFlight required.
- Faster than React Native / Expo for an MVP portfolio demo.
- iPad and mobile viewports are covered by 54 Playwright e2e tests across three viewport sizes.

### 7.2 With a hosted backend

Once the backend is deployed to Railway or Render (§4 / §5):

1. Update the frontend `VITE_API_BASE_URL` environment variable to point to the hosted backend URL.
2. Run `npm run build` in `frontend/` to produce a production build.
3. Serve the `frontend/dist/` directory from a static host (Vercel, Netlify, Render static site, GitHub Pages, or any CDN).
4. The PWA manifest and service worker already exist in the frontend build.
5. Open the hosted frontend URL in Safari on iPad → Add to Home Screen → confirm standalone PWA launch.

> **Note:** Do not set `VITE_API_BASE_URL` to a live trading backend or expose broker execution endpoints. The hosted demo backend must remain in read-only / dry-run mode (§4, §5, §6).

### 7.3 LAN / Tailscale fallback

If a hosted backend is not yet deployed:

- Use the existing LAN / Tailscale path documented in `docs/demo/demo_009_ipad_pwa_smoke_evidence.md`.
- Start the backend locally: `py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
- Start the frontend locally: `npm run dev` (from `frontend/`)
- Access `http://<PC-LAN-IP>:5173` on the iPad.

This path does not require a cloud account or public URL.

### 7.4 What the PWA demo shows

The PWA demo is a read-only paper trading preview. It shows:

- red-black institutional terminal UI
- AI Workspace
- Paper Run Preview panel
- safety chips: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `HUMAN REVIEW REQUIRED`, `EXECUTION OFF`
- no `Buy` / `Sell` / `Execute` / `Place Order` controls

It does not show:

- live trading
- broker execution
- real money operations
- guaranteed profit or performance claims

---

## 8. React Native / Expo — Explicitly Postponed

React Native / Expo is a valid mobile path for a future phase but is **not the current priority**.

React Native / Expo becomes useful only if MellyTrade needs:

- App Store (Apple) or Google Play distribution
- native push notifications
- deeper phone hardware integration (biometrics, background processes)
- a separate mobile product with its own release lifecycle

None of those requirements exist for the current portfolio / recruiter demo phase. The PWA path (§7) is faster, cheaper, and already smoke-tested. React Native / Expo would add a separate build toolchain, a separate release pipeline, and App Store / TestFlight compliance overhead that is not justified until the PWA demo is stable and the need for a native app is proven.

**Decision:** postpone React Native / Expo until the hosted PWA demo is stable and a concrete native-only requirement is identified.

---

## 9. Do Not Do List

The following must not be done in connection with any deployment derived from this guide:

| Forbidden action | Reason |
|---|---|
| Enable live trading or `autotrade.enabled = true` | Safety posture — live trading is intentionally disabled |
| Set `dry_run = false` | Safety posture — dry-run must stay enabled |
| Add broker execution routes or order buttons | Out of scope; would require full risk and compliance review |
| Commit secrets, tokens, passwords, or API keys to the repository | Security — use platform dashboard environment variable management |
| Add `MT5_LOGIN`, `MT5_PASSWORD`, or `MT5_SERVER` to any deployed environment for a demo | No broker account connection is needed or permitted for a read-only demo |
| Expose a public `/orders`, `/execute`, or `/trade` POST endpoint | Safety posture — no execution routes in a demo deploy |
| Add IBKR execution, MT5 execution, or any broker-connected execution | Out of scope for this guide |
| Make production trading claims or financial advice claims | This is a paper trading / portfolio demo only |
| Claim guaranteed profit or past performance | This is a paper trading / portfolio demo only |
| Submit to the App Store, TestFlight, or Google Play | PWA path is sufficient; native distribution is postponed |

---

## 10. Suggested Future Task Split

| Task ID | Scope |
|---|---|
| DEPLOY-002 | Verify backend entrypoint, health endpoints, and requirements for hosted deploy |
| DEPLOY-003 | Add safe deployment config (`Procfile`, `railway.toml`, or `render.yaml`) if needed — docs review first |
| DEPLOY-004 | Hosted backend smoke checklist after first successful Railway / Render deploy |
| PWA-DEMO-002 | Hosted PWA smoke checklist — confirm PWA works against hosted backend URL |
| DEMO-013 | Recruiter hosted demo walkthrough — full evidence pack for hosted demo |

---

## Cross-references

- [DEPLOY-002 Backend Entrypoint and Health Audit](backend_entrypoint_health_audit.md)
- [DEPLOY-004 Hosted Backend Smoke Checklist](hosted_backend_smoke_checklist.md)
- [DEPLOY-005 Platform Choice + Manual Deploy Plan](platform_choice_manual_deploy_plan.md)
- [iPad PWA Paper Run Preview Showcase](../showcase/ipad_pwa_paper_run_preview.md)
- [DEMO-009 — iPad PWA smoke evidence](../demo/demo_009_ipad_pwa_smoke_evidence.md)
- [DEMO-010 — Portfolio / LinkedIn copy pack](../demo/demo_010_portfolio_linkedin_copy_pack.md)
- [Local demo smoke checklist](../demo/local_readonly_demo_smoke.md)
- [iPad PWA smoke test guide](../devices/ipad_pwa_smoke_test.md)
- [Safety validation script](../../scripts/validate_safety_config.py)
