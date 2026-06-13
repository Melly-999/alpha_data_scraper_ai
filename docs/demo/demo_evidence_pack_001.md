# MellyTrade Demo Evidence Pack 001

## 1. Evidence pack status

- **Status:** ✅ Captured — all documented public surfaces verified safe and live
- **Type:** demo / portfolio evidence record (text evidence; no binaries committed)
- Companion: [demo_evidence_pack_001_checklist.md](demo_evidence_pack_001_checklist.md) ·
  freeze checkpoint: [demo_freeze_001.md](demo_freeze_001.md)

## 2. Baseline

- **Main SHA at capture:** `ff5a889fea66c6c5aa537ac310aa9be2d14c1047` (post-#296)
- **Safety validator:** `python scripts/validate_safety_config.py` → OVERALL: PASS

## 3. Date / time of checks

- **2026-06-13 ~15:25 (UTC+02:00)** — public GET-only smoke and availability checks

## 4. Source docs checked

- [demo_freeze_001.md](demo_freeze_001.md), [demo_freeze_001_checklist.md](demo_freeze_001_checklist.md),
  [demo_freeze_001_recruiter_script.md](demo_freeze_001_recruiter_script.md)
- [../deployment/render_current_status.md](../deployment/render_current_status.md)
- [../roadmap/current_status_after_neon_cleanup.md](../roadmap/current_status_after_neon_cleanup.md)
- `README.md`

Every evidence claim in those docs (hosted backend current, three safe
endpoints, CORS, degraded-by-design Neon) was re-verified below.

## 5. Public endpoint smoke (GET-only)

Backend: `https://alpha-data-scraper-ai.onrender.com`

| Endpoint | HTTP | JSON | Key flags observed | Degraded? | Secrets? | Result |
| --- | --- | --- | --- | --- | --- | --- |
| `/api/health` | 200 | yes | `safety.dry_run=true`, `auto_trade=false`, `max_risk_per_trade=1.0`, `emergency_pause=false` | `fallback_mode=true` (expected — optional keys unset) | none | **PASS** |
| `/api/safety/status` | 200 | yes | `dry_run=true · read_only=true · live_orders_blocked=true · auto_trade=false · max_risk_per_trade_pct=1.0`; 5 pillars | no | none | **PASS** |
| `/api/neon-memory/status` | 200 | yes | `paper_only · dry_run · read_only · live_orders_blocked = true`, `execution_enabled=false`, `requires_human_review=true`, `autotrade=false` | `availability="degraded"`, `source="unconfigured"` | none (placeholder ids `example-project`) | **PASS** |

CORS: `Access-Control-Allow-Origin` echoed the Vercel frontend origin on all
three. No secret-shaped substrings were found in any response body.

## 6. Safety flags observed (live, on production)

| Flag | Observed | Required | OK |
| --- | --- | --- | --- |
| `autotrade` / `auto_trade` | false | false | ✅ |
| `dry_run` | true | true | ✅ |
| `read_only` | true | true | ✅ |
| `live_orders_blocked` | true | true | ✅ |
| `execution_enabled` | false | false | ✅ |
| `requires_human_review` | true | true | ✅ |
| max risk per trade | 1.0% | ≤ 1% | ✅ |

No unsafe flag was observed on any surface.

## 7. Frontend / README / GitHub evidence

| Item | Check | Result |
| --- | --- | --- |
| Hosted frontend `/` | `https://alpha-data-scraper-ai.vercel.app/` → HTTP 200, `text/html` | ✅ |
| Frontend `/terminal` deep link | HTTP 200 (SPA route serves directly) | ✅ |
| `README.md` portfolio positioning | present on main (banner, Product Snapshot, safety contract) | ✅ |
| Demo freeze docs on main | all three `demo_freeze_001*` present | ✅ |
| Render current-status doc on main | `docs/deployment/render_current_status.md` present | ✅ |
| Roadmap status doc on main | `docs/roadmap/current_status_after_neon_cleanup.md` present | ✅ |
| Active order/execution controls | none surfaced via the public API contract (routes are GET-only; safety endpoints report execution disabled) | ✅ |

No dashboards, env-var pages, or secrets pages were opened during capture.

## 8. Screenshot artifact policy

Screenshots were **not committed**. Binaries are kept out of the repo by
policy; the verifiable, reproducible evidence is the text record above (the
endpoints can be re-checked at any time with a plain `GET`). If visual
artifacts are wanted for a recruiter pack, capture them into a local,
repo-external evidence folder (e.g. `99_Evidence/...`) and redact any secrets,
env vars, account IDs, or emails first — never commit them here without
explicit approval.

## 9. Evidence artifacts captured or skipped

- **Captured (text):** endpoint smoke table, live safety flags, frontend HTTP
  status, docs-present-on-main verification — all in this file.
- **Skipped (binary):** screenshots — skipped for repo-cleanliness/privacy;
  text evidence recorded instead and is independently reproducible.

## 10. Known caveats

- The Neon memory route is intentionally degraded (`DATABASE_URL` unset on
  Render). This is the designed safe behavior, not a failure.
- Several integrations run in fallback mode because optional API keys are
  deliberately not configured (`fallback_mode=true`).
- Render free tier may cold-start; the first request after idle can be slow.
- This is a portfolio/demo system, not a regulated trading platform.
- Evidence reflects the state at the capture timestamp; re-run the smoke
  before any live walkthrough.

## 11. What this evidence proves

- The hosted backend is **live and serving current main** (Neon routes
  present, build ≥ #286/#293).
- The safety posture is **enforced and observable on production**:
  read-only, dry-run, live orders blocked, autotrade off, risk capped at 1%.
- The system **degrades safely** when an optional dependency is absent.
- The public frontend is reachable, including SPA deep links.
- The documentation trail (README, freeze docs, status docs) exists on main
  and matches the live behavior.
- **No secrets are required or exposed** anywhere in the demo path.

## 12. What this evidence does NOT prove

- It does **not** prove or claim live trading, broker execution, or order
  placement — those are intentionally absent.
- It does **not** prove production-trading readiness or a regulated product.
- It does **not** prove Neon is fully configured (it is intentionally
  degraded).
- It does **not** assert profit, ROI, win-rate, returns, or real user
  adoption — none are claimed.

## 13. Next recommended task

`RECRUITER-PORTFOLIO-PACK-001` — assemble the recruiter-facing pack using this
verified evidence plus the freeze docs and recruiter script.
