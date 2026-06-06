# Hosted Demo Go-Live Runbook (web + mobile)

> Fastest safe path to a **public hosted demo** of the MellyTrade web terminal
> and the `/mobile` PWA (incl. the AI screenshot review). Read-only / dry-run /
> paper-only throughout. Deploy steps are **manual operator actions** in the
> Render and Vercel dashboards — nothing here changes runtime code.

This ties together the existing runbooks; follow them for detail:

- Backend: `docs/deployment/render_readonly_backend_runbook.md`
- Frontend: `docs/deployment/vercel_mobile_frontend_runbook.md`
- CORS / env audit: `docs/deployment/backend_entrypoint_health_audit.md`
- Smoke: `docs/deployment/hosted_mobile_demo_smoke_checklist.md`

---

## 0. Safety pre-flight (must stay true for a public demo)

- `config.json`: `autotrade.enabled=false`, `dry_run=true` (verify with
  `python scripts/validate_safety_config.py`).
- **Leave the real AI provider DISABLED** for the public demo: do **not** set
  `MOBILE_AI_PROVIDER_ENABLED` (or set it to `false`), and do **not** set an
  `ANTHROPIC_API_KEY` on the demo backend. The screenshot review then runs the
  deterministic **mock** — no provider key, no spend, no image sent off-box.
- No broker credentials, no MT5/IBKR/wallet secrets on the demo services.

---

## 1. Deploy backend (Render, read-only)

1. Follow `render_readonly_backend_runbook.md` to create the service.
2. Set backend env vars (dashboard only — never committed):

   | Env var | Value | Required |
   |---|---|---|
   | `MELLYTRADE_ALLOWED_ORIGINS` | `https://<your-vercel-domain>` | Yes (CORS) |
   | `MOBILE_AI_PROVIDER_ENABLED` | *(unset / `false`)* | Keep disabled for demo |
   | `ANTHROPIC_API_KEY` | *(unset)* | Keep unset for demo |
   | broker / MT5 / IBKR / wallet secrets | *(unset)* | Must stay unset |

3. Confirm `GET /api/health` → 200 and `GET /api/safety/status` shows
   read-only / dry-run / live-orders-blocked.

## 2. Deploy frontend (Vercel → backend)

1. Follow `vercel_mobile_frontend_runbook.md`.
2. Set `VITE_API_BASE_URL=https://<your-render-backend>/api` (public var only;
   no secrets in frontend env).
3. Redeploy so the build picks up the var.

## 3. Wire CORS

- Set `MELLYTRADE_ALLOWED_ORIGINS` on the backend to the exact Vercel origin
  (no trailing slash; no wildcard in the public demo).
- Redeploy backend; confirm the browser can call the backend from the Vercel
  origin without CORS errors.

## 4. Smoke (then you can demo)

Run `docs/deployment/hosted_mobile_demo_smoke_checklist.md` end-to-end,
including the **AI Screenshot Review** check (upload a synthetic PNG/JPEG/WebP →
paper-only preview; oversized/SVG/PDF rejected). Capture screenshots **outside**
the repo.

## 5. What to show in the demo

- **Web:** `/terminal` (read-only terminal), paper sandbox preview, audit rail,
  safety posture.
- **Mobile (`/mobile`):** AI Chart Review, Paper Game Plan, Safety Score,
  Watchlist, Setup Journal, FOMO Guard, Weekly Report, Monte Carlo snapshot,
  Melly Pet coach, and **AI Screenshot Review** (mock analysis preview).

## 6. Rollback / stop

- Pause or delete the Render/Vercel services from their dashboards.
- No data is persisted by the demo (no image storage, no order writes), so
  there is nothing to clean up beyond tearing down the services.

---

**Demo safety one-liner:** Analysis only. Not financial advice. Paper plan
only. No live orders. Human review required. No broker execution. No AI
provider keys in the frontend.
