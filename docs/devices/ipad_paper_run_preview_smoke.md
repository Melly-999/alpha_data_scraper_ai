# iPad / PWA Smoke Checklist - Paper Run Preview Route

Use this checklist to manually verify the Paper Run Preview route on:

- iPad Safari
- iPad installed PWA / Add to Home Screen mode
- LAN access from a Windows dev PC
- Optional Tailscale access if already configured

This is a read-only preview check only. It must stay within the safety posture:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk `<= 1%`
- human review required

No live orders, no broker execution, no MT5 execution, no IBKR execution, no order routing, no secrets, and no account IDs.

## Scope

The Paper Run Preview route is:

- `/terminal/paper-run-preview`

The expected UI entry points are:

- Terminal left sidebar shortcut: `Paper Run Preview`
- AI Workspace command launcher: `Open Preview`

The preview client is GET-only and targets:

- `GET /api/paper/run/preview`

## Before You Start

Confirm the merged feature is on `main`:

- Main SHA after merge: `cf993c8`

Confirm the app is only being tested on a trusted local network or Tailscale connection. Do not expose the dev server or backend publicly.

## 1. Start the backend safely

Use the existing local backend command documented in the repo:

```powershell
.\scripts\start_backend_local.ps1
```

Expected:

- Backend binds to `127.0.0.1:8001`
- Backend remains loopback-only
- No public exposure
- No live trading
- No broker account connection

Confirm health locally from the Windows dev PC:

```text
http://127.0.0.1:8001/health
```

If the repo documents a different health endpoint in your environment, use that documented endpoint, but keep the backend on loopback only.

## 2. Start the frontend for LAN testing

Use the safe LAN helper:

```powershell
.\scripts\devices\start_frontend_lan.ps1
```

This starts Vite with `--host 0.0.0.0` so an iPad on the same LAN can reach it.

Important:

- Use `0.0.0.0` only for trusted home or lab LAN testing
- Do not commit `.env` values
- Do not hardcode API keys or secrets
- Do not expose the backend publicly

Expected local URLs:

- `http://127.0.0.1:5173`
- `http://<WINDOWS_LAN_IP>:5173`
- `http://<WINDOWS_LAN_IP>:5173/terminal/paper-run-preview`

## 3. Find the Windows LAN IP

On the Windows dev PC, run:

```powershell
ipconfig
```

Or filter to the primary IPv4 address:

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown" } |
  Select-Object IPAddress, InterfaceAlias |
  Format-Table -AutoSize
```

Use the IPv4 address for the iPad URL, for example:

```text
http://192.168.x.x:5173/terminal/paper-run-preview
```

If Tailscale is already configured, you may use the `100.x.x.x` Tailscale address instead of the LAN address.

## 4. iPad Safari smoke

Open Safari on the iPad and navigate to:

```text
http://<WINDOWS_LAN_IP>:5173/terminal/paper-run-preview
```

Confirm:

- The page loads
- The Paper Run Preview panel is visible
- The route stays on `/terminal/paper-run-preview`
- The page remains usable in portrait and landscape
- There is no horizontal overflow

Verify the safety chips and safety copy are visible:

- `READ ONLY`
- `DRY RUN`
- `LIVE ORDERS BLOCKED`
- `HUMAN REVIEW REQUIRED`
- `EXECUTION OFF`

Tap `Load Preview` or `Refresh Preview`.

Confirm:

- The panel refreshes without errors
- The request is GET-only if you can observe logs or dev tools
- No `POST`, `PUT`, `PATCH`, or `DELETE` requests are sent
- No `Buy`, `Sell`, `Execute`, `Place Order`, `Submit Order`, `Live Trade`, or `Auto Trade` controls exist
- No broker credential prompts appear
- No account IDs are shown

## 5. iPad PWA smoke

In Safari, add the site to the home screen:

1. Tap Share
2. Choose `Add to Home Screen`
3. Confirm the app name and icon
4. Launch the installed app from the iPad home screen

Confirm:

- The app opens in standalone / installed mode
- The route `/terminal/paper-run-preview` loads correctly
- The same safety chips and read-only copy are visible
- `Back to Terminal` works if present in the route UI
- Refreshing the route does not break the shell
- There is no horizontal overflow

## 6. Optional Tailscale smoke

Only use this if Tailscale is already configured in your environment.

Confirm:

- The same route loads through the Tailscale IP
- The same safety checks pass
- No new public exposure is introduced

Do not publish API keys, secrets, broker credentials, or backend endpoints publicly.

## 7. Evidence checklist

Capture screenshots outside the repository unless explicitly requested otherwise:

- Desktop route screenshot
- iPad Safari portrait screenshot
- iPad Safari landscape screenshot
- Installed PWA screenshot

Record in your notes:

- Date
- Time
- Device model
- iPadOS version
- Browser
- URL tested

Keep screenshots and local notes out of the repo unless you are explicitly asked to commit them.

## 8. Troubleshooting

### iPad cannot connect to the LAN URL

- Confirm the Windows PC and iPad are on the same trusted LAN or Tailscale network
- Confirm you used the Windows IPv4 address, not `localhost`
- Confirm Vite was started with `--host 0.0.0.0`

### Windows Firewall blocks Vite

Allow TCP 5173 on private networks only:

```powershell
New-NetFirewallRule `
  -DisplayName "Vite LAN dev server (5173)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 5173 `
  -Profile Private `
  -Action Allow
```

Remove it after testing:

```powershell
Remove-NetFirewallRule -DisplayName "Vite LAN dev server (5173)"
```

### Backend is not running on `127.0.0.1:8001`

- Start the backend again with the documented local command
- Confirm the backend stays loopback-only
- Confirm the frontend proxy is still pointing to the local backend

### Vite route returns 404 after refresh

- Confirm the app is opened through the SPA route `/terminal/paper-run-preview`
- Confirm the Vite dev server is still running
- Confirm the frontend route exists in the current `main` branch

### API returns a degraded or error state

- This is acceptable if the UI still stays read-only and safe
- Confirm the preview remains GET-only
- Confirm no mutation or order-routing controls appear
- Confirm the shell still renders the safety posture and the panel

### Mobile horizontal overflow

- Rotate the iPad to portrait and landscape
- Recheck the route at both orientations
- If necessary, re-open the page after rotating to force a layout recalculation

### iOS Safari zoom or input issues

- Tap each input and confirm the page does not unexpectedly zoom
- Use the installed PWA mode if Safari chrome makes the page feel cramped
- If an input appears too small, verify the current viewport and zoom state before changing the app

## Safety reminders

- Read-only preview only
- No live orders
- No broker execution
- No MT5 execution
- No IBKR execution
- No order routing
- Human review required
- Max risk remains `<= 1%`
- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`

## Related files

- `scripts/devices/start_frontend_lan.ps1`
- `scripts/start_backend_local.ps1`
- `scripts/validate_safety_config.py`
- `frontend/src/pages/PaperRunPreviewPage.tsx`
- `frontend/src/components/terminal/PaperRunPreviewPanel.tsx`
- `frontend/src/lib/paperRunPreviewApi.ts`
