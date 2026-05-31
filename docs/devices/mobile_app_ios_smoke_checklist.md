# Mobile App iPad/iPhone Smoke Checklist

## Purpose

This checklist verifies the `/mobile` read-only PWA shell on iPad/iPhone Safari,
and optionally as a PWA / Home Screen app. It is a manual device-smoke aid; it
does not enable any trading and does not require broker credentials.

## Preconditions

- `main` includes PR #245 (the `/mobile` route + mobile shell).
- The backend is **not required** for the static shell smoke (the `/mobile` page
  makes no API calls). Backend/API checks are only added later if a task
  explicitly requires them.
- The frontend can run locally with Vite.
- The device and PC are on the same LAN or Tailscale network.
- No live trading.
- No broker credentials.
- No order controls.

## Local PC Setup

```bash
cd frontend
npm ci          # only if node_modules is missing
npm run dev -- --host 0.0.0.0
```

The backend should remain loopback-only unless a later task explicitly requires
hosted/backend smoke. The mobile shell itself is static and does not call the
backend.

## Device URLs

- `http://<LAN-IP>:5173/mobile`
- `http://<TAILSCALE-IP>:5173/mobile`

## Checklist A — Page Load

- [ ] `/mobile` loads
- [ ] no blank screen
- [ ] no console-visible crash (if inspect is available)
- [ ] title visible: **MellyTrade Mobile**
- [ ] subtitle visible: **Read-only command center**

## Checklist B — Layout

- [ ] no horizontal overflow
- [ ] text readable
- [ ] tap targets comfortable
- [ ] header not clipped
- [ ] cards stack correctly on iPhone
- [ ] grid adapts on iPad

## Checklist C — Safety

- [ ] `READ ONLY` visible
- [ ] `DRY RUN` visible
- [ ] `LIVE ORDERS BLOCKED` visible
- [ ] `HUMAN REVIEW REQUIRED` visible
- [ ] no Buy / Sell / Execute / Place Order controls
- [ ] no "live trading enabled" copy
- [ ] no "guaranteed profit" copy

## Checklist D — Melly Pet

- [ ] Melly Pet visible (or fallback visible)
- [ ] display-only
- [ ] no action buttons implying execution

## Checklist E — Navigation

- [ ] quick links do not break
- [ ] route `/terminal` works if linked
- [ ] `/mobile` can be refreshed directly
- [ ] browser back/forward works

## Checklist F — PWA / Home Screen

- [ ] Add to Home Screen works (if desired)
- [ ] standalone launch opens correctly
- [ ] icon / manifest works (if available)
- [ ] no auth / secrets required

## Pass/Fail Rules

Do **not** mark pass unless tested on a real device. If the checklist has not
been executed on hardware, record it as **TEMPLATE / NOT EXECUTED** in the
result template.
