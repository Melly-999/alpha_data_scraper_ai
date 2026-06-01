# Hosted Mobile Demo Smoke Checklist

> Manual checklist for the hosted Render + Vercel demo. Do **not** claim pass
> unless actually executed. Screenshots/evidence are stored **outside** the repo.

## Scope

End-to-end smoke of the hosted read-only demo: Render backend + Vercel frontend +
`/mobile` shell + iPad/iPhone + CORS. No live trading, no broker execution.

## Render Backend Smoke

- [ ] service is up
- [ ] `/health` (or `/api/health`) returns 200
- [ ] safety status confirms read-only / dry-run / live orders blocked
- [ ] no broker credentials configured

## Vercel Frontend Smoke

- [ ] build deployed
- [ ] `/` and `/terminal` load
- [ ] `VITE_` env points at the Render backend
- [ ] no secrets in frontend env

## /mobile Smoke

- [ ] `/mobile` loads on the hosted frontend
- [ ] safety badges visible
- [ ] Melly Pet visible
- [ ] no order / buy / sell / execute controls
- [ ] no horizontal overflow

## iPad / iPhone Smoke

- [ ] Safari loads `/mobile`
- [ ] layout clean on iPhone and iPad
- [ ] Add to Home Screen works (optional)
- [ ] see `docs/devices/mobile_app_ios_smoke_checklist.md` for device detail

## CORS Smoke

- [ ] frontend can call backend health/read endpoints from the Vercel origin
- [ ] no wildcard CORS in the production demo (or documented as temporary)

## Evidence

- Screenshots / recordings stored **outside** the repository.
- Do not commit screenshots or videos.

## Results

| Area | Result (PASS/FAIL/NA) | Notes |
|---|---|---|
| Render backend | | |
| Vercel frontend | | |
| /mobile | | |
| iPad/iPhone | | |
| CORS | | |

## Final Status

- `PASS` / `FAIL` / `BLOCKED` / **NOT EXECUTED**
