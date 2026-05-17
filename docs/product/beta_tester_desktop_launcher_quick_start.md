# Beta Tester Desktop Launcher Quick Start

> Local read-only demo. Advisory output only. Human review required.

---

## What this is

- A local demo launcher for the MellyTrade terminal.
- Starts the local backend and frontend helper scripts.
- Opens the MellyTrade terminal UI in your browser.
- Advisory / demo output only — no execution, no orders, no live broker connection.

---

## What this is NOT

- **Not** a live trading application.
- **Not** broker execution.
- **Not** investment advice.
- **Not** a final installer.
- **Not** code-signed yet.
- **Not** auto-updating.

---

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No broker credentials are required. No live orders are placed. All output is advisory.

---

## Prerequisites

1. **Python 3.11** installed — [python.org](https://python.org)
2. **Node.js 18+** installed — [nodejs.org](https://nodejs.org)
3. EXE built locally (see below) **or** run from source.

---

## Run from EXE

If `dist/MellyTradeLauncher.exe` exists:

```powershell
.\dist\MellyTradeLauncher.exe
```

The launcher will:

1. Print the safety banner.
2. Start the backend helper.
3. Start the frontend helper.
4. Wait for both to be ready.
5. Open `http://127.0.0.1:5173/terminal` in your default browser.

---

## Run in no-browser mode

```powershell
.\dist\MellyTradeLauncher.exe --no-browser
```

Starts backend and frontend without opening the browser.
Navigate manually to `http://127.0.0.1:5173/terminal`.

---

## Create a Desktop shortcut

```powershell
.\scripts\create_desktop_shortcut.ps1
```

Creates `MellyTrade Terminal.lnk` on your Windows Desktop.
Double-click the shortcut to launch MellyTrade.

No-browser shortcut:

```powershell
.\scripts\create_desktop_shortcut.ps1 -NoBrowser
```

> **Note:** The `.lnk` file is a local file only — do not commit it to git.

---

## Build the EXE

If `dist/MellyTradeLauncher.exe` is missing, build it locally:

```powershell
.\scripts\build_desktop_launcher.ps1 -Build
```

Requires PyInstaller. Install if needed:

```powershell
py -3.11 -m pip install pyinstaller
```

> **Note:** `dist/`, `build/`, and `*.spec` are local-only — do not commit them.

---

## Troubleshooting

| Symptom | Action |
|---|---|
| EXE not found | Run `.\scripts\build_desktop_launcher.ps1 -Build` |
| Port already in use | Close other local dev processes using ports 8001 / 5173 |
| Safety banner missing | Stop and report — do not continue |
| Broker credential prompt appears | Stop immediately and report |
| Live trading or order button appears | Stop immediately and report |
| Backend not ready after 60s | Check backend logs; ensure Python dependencies are installed |
| Frontend not ready after 90s | Check frontend logs; ensure `npm install` was run in `frontend/` |

---

## Safety confirmation

Before using the launcher, confirm:

- [ ] Safety banner is visible at startup
- [ ] `autotrade=false` is shown
- [ ] `dry_run=true` is shown
- [ ] `read_only=true` is shown
- [ ] `live_orders_blocked=true` is shown
- [ ] No Buy / Sell / Execute buttons are visible in the UI
- [ ] No broker credentials were requested

---

*MellyTrade Closed Beta — Desktop Launcher Quick Start — local-only, read-only, advisory.*
