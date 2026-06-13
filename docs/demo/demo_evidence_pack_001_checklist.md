# Demo Evidence Pack 001 — Capture Checklist

Reusable checklist for capturing safe demo evidence. Companion to
[demo_evidence_pack_001.md](demo_evidence_pack_001.md).

## 1. Before evidence capture

- [ ] Confirm `origin/main` is at or beyond the documented baseline SHA
- [ ] Run `python scripts/validate_safety_config.py` → expect PASS
- [ ] Record the capture date/time and the main SHA
- [ ] Have the documented public URLs ready (from README / deployment docs only)

## 2. Public endpoint checklist (GET-only)

- [ ] `GET /api/health` → 200, `safety.dry_run=true`, `auto_trade=false`, `max_risk_per_trade<=1.0`
- [ ] `GET /api/safety/status` → 200, `dry_run/read_only/live_orders_blocked=true`, `auto_trade=false`, max risk ≤ 1%, pillars present
- [ ] `GET /api/neon-memory/status` → 200, all safety flags correct, `availability="degraded"` / `mode="read-only"` acceptable
- [ ] No POST/PUT/PATCH/DELETE, no auth, no broker calls
- [ ] Scan each response body for secret-shaped substrings → expect none

## 3. Frontend checklist

- [ ] Hosted frontend `/` → HTTP 200
- [ ] Key SPA deep link (e.g. `/terminal`) → HTTP 200
- [ ] No active buy/sell/order/execute control presented as live
- [ ] No dashboards / env-var pages / secrets pages opened

## 4. Screenshot safety checklist (only if capturing images)

- [ ] No secrets visible
- [ ] No env vars visible
- [ ] No account IDs, broker IDs, or database URLs visible
- [ ] No email addresses visible
- [ ] No private dashboard content visible
- [ ] Save to a repo-external or git-ignored evidence folder
- [ ] Do not commit binaries without explicit approval

## 5. Redaction checklist

- [ ] Crop/black out any token, key, password, or connection string
- [ ] Remove personal identifiers (names, emails, account numbers)
- [ ] Verify placeholder identifiers only (e.g. `example-project`)

## 6. Recruiter-demo proof checklist

- [ ] Endpoint smoke table recorded with timestamps and PASS/FAIL
- [ ] Live safety flags recorded
- [ ] Frontend availability recorded
- [ ] Docs-present-on-main verified
- [ ] "What this proves / does not prove" stated honestly

## 7. Do-not-capture list

- ✋ `.env` files or any environment file
- ✋ Render/Vercel/GitHub dashboards or settings pages
- ✋ Secrets, tokens, API keys, broker credentials
- ✋ Account IDs, order IDs, database URLs, emails
- ✋ Any buy/sell/order/execute control interaction (do not click)

## 8. If evidence fails

- A safety flag is unsafe (`dry_run=false`, `live_orders_blocked=false`,
  `execution_enabled=true`, max risk > 1%) → **STOP**, report BLOCKED, do not
  publish evidence; open a safety-regression task
- An endpoint is down → note it, re-check after cold start, document calmly as
  degraded/unavailable rather than debugging live
- A secret appears in any response → STOP, report immediately, do not save

## 9. Next evidence tasks

- `RECRUITER-PORTFOLIO-PACK-001` — assemble recruiter-facing pack
- `MOBILE-PWA-EVIDENCE-REFRESH-001` — mobile/PWA evidence (M7)
- `DESKTOP-EXE-EVIDENCE-PACK-001` — desktop/Tauri evidence
