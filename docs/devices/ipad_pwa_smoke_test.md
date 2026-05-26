# iPad PWA Smoke Test — MellyTrade Terminal

Verify that the MellyTrade frontend installs correctly as a read-only
Progressive Web App on iPad via Safari, with the Paper Run Preview panel
functional over a local LAN or Tailscale connection.

> **Safety posture throughout this test:**
> `autotrade=false` · `dry_run=true` · `read_only=true`
> `live_orders_blocked=true` · `execution_enabled=false` · max risk ≤ 1 %
>
> No broker credentials, no live orders, no real money.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| PC and iPad on the **same LAN** *or* connected via **Tailscale** | Both must be reachable from each other |
| Node.js installed on PC | `node --version` ≥ 18 |
| Python 3.11 on PC | for backend |
| Backend dependencies installed | `pip install -r requirements-ci.txt` or full `requirements.txt` |
| Frontend dependencies installable | npm will install on first run |
| **No real broker credentials required** | paper/dry-run mode only |

---

## Step 1 — Find the PC LAN IP

Open **PowerShell** on the PC:

```powershell
# Option A: quick display
ipconfig

# Option B: filter to the primary LAN adapter
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown" } |
    Select-Object IPAddress, InterfaceAlias |
    Format-Table -AutoSize
```

Look for an address like `192.168.x.x` (LAN) or `100.x.x.x` (Tailscale).
Note it — you will open `http://<this-ip>:5173` on the iPad.

---

## Step 2 — Start the backend (loopback, safe)

The backend always binds to `127.0.0.1` (loopback only). It is **never
exposed directly** to the LAN. The Vite dev server proxies `/api` requests
server-side, so iPad requests reach the backend through Vite.

```powershell
# From repo root in a dedicated terminal window
.\scripts\start_backend_local.ps1
```

Expected output:

```
======================================================
  MellyTrade Local Backend -- READ-ONLY / DRY-RUN
======================================================
  SAFETY: autotrade=false   dry_run=true
  SAFETY: live orders blocked   read_only=true
  Host:   127.0.0.1:8001 (loopback only)
======================================================
```

Leave this terminal open.

---

## Step 3 — Start the frontend on LAN host

Open a **second PowerShell terminal** at the repo root:

```powershell
.\scripts\devices\start_frontend_lan.ps1
```

This runs `npm run dev -- --host 0.0.0.0 --port 5173`, which binds Vite to
all local network interfaces so the iPad can reach it.

> ⚠️ **LAN-only warning.**
> `--host 0.0.0.0` makes the dev server reachable by any device on your
> local network (or Tailscale peers). This is intentional for device testing.
> **Stop the server (`Ctrl+C`) when testing is complete.**
> Never run this on a public or untrusted network.

Expected output:

```
======================================================
  MellyTrade LAN Frontend -- READ-ONLY / DRY-RUN
======================================================
  SAFETY: autotrade=false   dry_run=true
  SAFETY: live_orders_blocked=true   read_only=true
  SAFETY: no execution buttons   no order routes
  SAFETY: local LAN / Tailscale only -- not public

  Local (PC):  http://127.0.0.1:5173
  LAN (iPad):  http://192.168.x.x:5173  <-- open on iPad
  Terminal:    http://192.168.x.x:5173/terminal
======================================================
```

> **Note:** `VITE_MELLY_API_BASE_URL` is intentionally **not set** in this
> script. Setting it to `http://127.0.0.1:8001` would break iPad access
> because `127.0.0.1` in the iPad's browser refers to the iPad itself, not
> the PC. The Vite proxy (`/api → 127.0.0.1:8001`) runs server-side on the
> PC and handles all API routing correctly without that env var.

---

## Step 4 — Open on iPad Safari

1. Open **Safari** on the iPad.
2. Tap the address bar and enter:
   ```
   http://192.168.x.x:5173
   ```
   (replace with your PC's actual LAN or Tailscale IP from Step 1)
3. The MellyTrade terminal should load.

---

## Step 5 — Navigate to the terminal

If you are not already on the terminal view:

- Tap the **Terminal** link / sidebar navigation.
- URL should read: `http://192.168.x.x:5173/terminal`

---

## Step 6 — Open the Paper Run Preview panel

1. Within the terminal, locate **Paper Run Preview** in the left sidebar or
   workspace grid.
2. Tap to open the panel.
3. Confirm the panel renders: form fields, safety chips, and action buttons
   are visible.

---

## Step 7 — Input and touch-target checks

Tap each form input in the Paper Run Preview panel and confirm:

| Check | Expected |
|---|---|
| Tapping an input field | **No iOS zoom** (font-size ≥ 16 px is enforced) |
| Button tap targets | Comfortable to tap — min-height 44 px |
| Form layout at 834 px wide | Single column or comfortable two-column |
| Action row at 768 px wide | Buttons wrap cleanly, no overflow |

---

## Step 8 — Safety chip visibility

Confirm all five safety chips are visible in the panel:

- `READ ONLY`
- `DRY RUN`
- `LIVE ORDERS BLOCKED`
- `HUMAN REVIEW REQUIRED`
- `EXECUTION OFF`

---

## Step 9 — Load Preview (GET only)

Tap **Load Preview** or **Refresh Preview**.

Expected: the panel either:
- Shows a paper run preview result fetched via `GET /paper/run/preview`, or
- Shows a graceful "backend unavailable" empty state (if backend is not running).

Confirm: no `POST`/`PUT`/`PATCH`/`DELETE` requests are sent.
Confirm: no broker credential prompts appear.
Confirm: no `Buy` / `Sell` / `Execute` / `Place Order` buttons appear.

---

## Step 10 — PWA install (Add to Home Screen)

1. In Safari, tap the **Share** icon (box with arrow, bottom toolbar).
2. Scroll down and tap **Add to Home Screen**.
3. Confirm the suggested name is **MellyTrade** (from `apple-mobile-web-app-title`).
4. Tap **Add**.

Expected home screen entry:

| Field | Expected value |
|---|---|
| App icon | Dark terminal icon with amber "MT" letterforms |
| App name | MellyTrade |

---

## Step 11 — Launch from home screen

1. Tap the MellyTrade icon on the iPad home screen.
2. Confirm the app opens **without the Safari browser chrome** (standalone mode).
3. Confirm the **status bar is dark** (`black-translucent` style).
4. Confirm the terminal loads and the same safety posture applies.

---

## Expected results summary

| Item | Pass condition |
|---|---|
| PWA manifest served | Safari reads name/icon/display from `/manifest.webmanifest` |
| Add to Home Screen | Works without HTTPS error (HTTP is allowed on LAN for PWA install on iOS 16.4+) |
| App icon | Amber-on-dark terminal icon, 192 px |
| Standalone mode | No Safari URL bar in launched app |
| Status bar | Dark / translucent |
| Panel renders | Form, chips, and buttons visible |
| No iOS zoom | No font-size jump when tapping inputs |
| Touch targets | 44 px min — no accidental mis-taps |
| GET preview | Returns data or clean offline state |
| No execution surface | No Buy/Sell/Execute/Place Order buttons |
| No broker prompts | No credential dialogs |

---

## Troubleshooting

### iPad cannot reach the frontend

**Check Windows Firewall.** By default Windows blocks inbound connections
on port 5173.

Allow the port (private networks only):

```powershell
# Run as Administrator
New-NetFirewallRule `
  -DisplayName "Vite LAN dev server (5173)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 5173 `
  -Profile Private `
  -Action Allow
```

Remove after testing:

```powershell
Remove-NetFirewallRule -DisplayName "Vite LAN dev server (5173)"
```

---

### Frontend shows "ERR_CONNECTION_REFUSED" on iPad

- Confirm Vite started with `--host 0.0.0.0` (not `127.0.0.1`).
  The `start_frontend_lan.ps1` helper sets this automatically.
- Confirm you used the PC's **LAN IP** in Safari, not `localhost`.
- If using Tailscale: use the `100.x.x.x` address, not the LAN IP.

---

### API calls fail / Paper Run Preview shows error

The Vite proxy (`/api → 127.0.0.1:8001`) runs on the PC side and forwards
iPad requests to the backend. If the backend is not running, the proxy
returns a connection error.

- Start the backend: `.\scripts\start_backend_local.ps1`
- Confirm it is listening: `http://127.0.0.1:8001/docs`
- The panel should fall back to a clean empty state when backend is offline.

---

### CORS errors in Safari DevTools

Vite's proxy sets `changeOrigin: true`, which rewrites the `Origin` header
so the backend sees requests from `127.0.0.1`. CORS headers from the
backend should pass through correctly.

If you see a CORS error, confirm the backend CORS policy allows all origins
in development (it should for paper/local mode).

---

### PWA "Add to Home Screen" is greyed out or missing

- iOS 16.3 and earlier restrict PWA install to HTTPS. iOS 16.4+ lifted
  this for LAN addresses. Ensure the iPad is on iOS 16.4+.
- If still blocked, consider setting up a local self-signed HTTPS certificate
  or use Tailscale's HTTPS certificates (`tailscale cert`).

---

### Tailscale: cannot reach the PC

- Confirm both PC and iPad are logged in to the same Tailscale account.
- On PC: run `tailscale status` to confirm the iPad is listed.
- Use the Tailscale IP (`100.x.x.x`) in Safari, not the LAN IP.
- Tailscale uses port `5173` without firewall changes (traffic is tunnelled).

---

### Wrong IP in the helper script output

The script uses `Get-NetIPAddress` to detect the primary LAN IP. If it
shows the wrong adapter, run `ipconfig` manually and use that IP in Safari.

---

## Safety reminders

| Rule | Detail |
|---|---|
| Local LAN / Tailscale only | Never expose port 5173 on a public interface or cloud VM |
| Stop when done | `Ctrl+C` in the Vite terminal; remove firewall rule if added |
| No real broker credentials | Paper / dry-run mode only — no MT5/IBKR account data |
| `dry_run=true` stays on | Config enforced by `validate_safety_config.py`; never disable |
| `autotrade=false` stays off | No autonomous order submission |
| Backend on loopback | `127.0.0.1:8001` is never exposed to LAN directly |

---

## Related files

| Path | Purpose |
|---|---|
| `scripts/devices/start_frontend_lan.ps1` | LAN-accessible Vite dev server helper |
| `scripts/start_backend_local.ps1` | Loopback backend (safe, always loopback) |
| `scripts/start_frontend_local.ps1` | Localhost-only frontend (not LAN-accessible) |
| `scripts/validate_safety_config.py` | Safety posture validator |
| `frontend/public/manifest.webmanifest` | PWA manifest (name, icons, display) |
| `frontend/public/icons/icon-192.png` | iPad home screen icon |
| `frontend/index.html` | Apple PWA meta tags |
