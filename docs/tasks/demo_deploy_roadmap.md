# Demo Deploy Roadmap

| Task | Title | Status | Risk | Scope |
|---|---|---|---|---|
| DEMO-DEPLOY-001 | Render backend read-only runbook | Planned | Low | Docs |
| DEMO-DEPLOY-002 | Vercel frontend read-only runbook | Planned | Low | Docs |
| DEMO-DEPLOY-003 | Render backend smoke checklist | Planned | Low-Med | Docs/script |
| DEMO-DEPLOY-004 | Vercel frontend smoke checklist | Planned | Low | Docs/script |
| DEMO-DEPLOY-005 | Hosted E2E demo evidence pack | Planned | Low | Docs |
| DEMO-DEPLOY-006 | iPad/mobile hosted smoke | Planned | Low | Docs |
| DEMO-DEPLOY-007 | Public demo copy cleanup | Planned | Low | README/docs |
| DEMO-DEPLOY-008 | Optional Sevalla backup target | Later | Low-Med | Deploy docs/config |

## Tasks

### DEMO-DEPLOY-001 — Render backend read-only runbook

- **Goal:** Document deploying the FastAPI backend to Render in read-only/dry-run mode.
- **Allowed files:** `docs/deployment/render_backend_runbook.md`
- **Forbidden files:** `app/*`, `config.json`, `requirements*`, `.github/workflows/*`, `Dockerfile*`, `.env*`, secrets.
- **Validation:** `py -3.11 scripts/validate_safety_config.py`; static scan.
- **Exit criteria:** Docs-only PR; env vars described as dashboard-only; no secrets.

### DEMO-DEPLOY-002 — Vercel frontend read-only runbook

- **Goal:** Document deploying the React/Vite frontend to Vercel pointing at the Render backend.
- **Allowed files:** `docs/deployment/vercel_frontend_runbook.md`
- **Forbidden files:** `frontend/src/*`, secrets, `.env*`.
- **Validation:** static scan; confirm only public `VITE_` vars described.
- **Exit criteria:** Docs-only PR; no secrets in frontend env.

### DEMO-DEPLOY-003 — Render backend smoke checklist

- **Goal:** A read-only smoke checklist/script for the hosted backend.
- **Allowed files:** `docs/deployment/render_backend_smoke.md`, optional `scripts/dev/render_backend_smoke.ps1`
- **Forbidden files:** runtime app code; secrets; workflows.
- **Validation:** confirm GET-only health checks; static scan.
- **Exit criteria:** Docs/script PR; no mutating calls.

### DEMO-DEPLOY-004 — Vercel frontend smoke checklist

- **Goal:** A smoke checklist for the hosted frontend.
- **Allowed files:** `docs/deployment/vercel_frontend_smoke.md`, optional script.
- **Forbidden files:** `frontend/src/*`; secrets.
- **Validation:** static scan; read-only checks only.
- **Exit criteria:** Docs/script PR.

### DEMO-DEPLOY-005 — Hosted E2E demo evidence pack

- **Goal:** Capture an evidence pack (screenshots/notes) of the hosted demo.
- **Allowed files:** `docs/demo/hosted_demo_evidence_pack.md`
- **Forbidden files:** generated binary assets unless approved; secrets.
- **Validation:** static scan.
- **Exit criteria:** Docs-only PR.

### DEMO-DEPLOY-006 — iPad/mobile hosted smoke

- **Goal:** Document iPad/mobile smoke for the hosted demo.
- **Allowed files:** `docs/demo/hosted_ipad_mobile_smoke.md`
- **Forbidden files:** runtime app code; secrets.
- **Validation:** static scan.
- **Exit criteria:** Docs-only PR.

### DEMO-DEPLOY-007 — Public demo copy cleanup

- **Goal:** Ensure README and demo docs read as a product/engineering project.
- **Allowed files:** `README.md`, `docs/demo/*` copy docs.
- **Forbidden files:** runtime app code; secrets; workflows.
- **Validation:** static scan for recruiter/CV terms and unsafe trading claims.
- **Exit criteria:** Docs/README PR; product-oriented copy; safety disclaimers preserved.

### DEMO-DEPLOY-008 — Optional Sevalla backup target

- **Goal:** Optionally salvage the Sevalla deploy bundle as a small backup-target PR.
- **Allowed files:** `Dockerfile.sevalla`, `docs/deployment/sevalla_readonly_demo.md`, `frontend/.env.sevalla.example`, `scripts/sevalla_demo_local_smoke.ps1`
- **Forbidden files:** secrets; live broker config; workflow changes.
- **Validation:** `validate_safety_config.py`; static scan; confirm placeholders only.
- **Exit criteria:** Small additive deploy PR; read-only/dry-run enforced.
