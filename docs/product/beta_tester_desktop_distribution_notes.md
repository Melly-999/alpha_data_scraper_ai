# Beta Tester Desktop Distribution Notes

Local read-only demo. Advisory output only. Human review required.

---

## What you are installing

A local Windows demo of MellyTrade Terminal. This installs nothing to your
system. It is a portable launcher that runs entirely on your machine.

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No broker credentials. No live trading. No order execution.

---

## What this is NOT

- NOT live trading
- NOT broker execution
- NOT investment advice
- NOT a final production installer
- NOT code-signed (SmartScreen warning is expected - see below)
- NOT auto-updating

---

## What you need

- Windows 10 or Windows 11 (64-bit)
- No admin rights required
- No Python installation required
- No Node.js installation required
- No repo checkout required

---

## Download

You will receive a download link via the tester onboarding email.

File: `MellyTrade-beta-v0.2-win64.zip`

---

## Install steps

### 1. Extract the ZIP

Right-click `MellyTrade-beta-v0.2-win64.zip` and choose "Extract All".

Extract to a folder such as `C:\MellyTrade\`.

### 2. Create Desktop shortcut

Right-click `create_desktop_shortcut.ps1` and choose "Run with PowerShell".

You will see a safety banner:

```
SAFETY: autotrade=false
SAFETY: dry_run=true
SAFETY: read_only=true
SAFETY: live_orders_blocked=true
```

A shortcut named "MellyTrade Terminal" will appear on your Desktop.

### 3. Launch

Double-click "MellyTrade Terminal" on your Desktop.

A command window will open briefly. Your browser will open automatically to:

```
http://localhost:5173/terminal
```

If your browser does not open automatically, open it manually and navigate to
that address.

---

## SmartScreen warning

Because the EXE is not yet code-signed, Windows may show:

> "Windows protected your PC"

This is expected for a closed beta. To proceed:

1. Click "More info"
2. Click "Run anyway"

You will only need to do this once per machine.

---

## No-browser mode

If you prefer to open the browser yourself:

1. Right-click `create_desktop_shortcut.ps1`
2. Choose "Open with PowerShell"
3. Type: `.\create_desktop_shortcut.ps1 -NoBrowser`

The shortcut will launch the terminal without opening a browser window.

---

## Stopping the launcher

Close the command window that opened when you launched the shortcut. This will
stop the backend and frontend processes.

Alternatively, press `Ctrl+C` in the command window.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| Browser shows "This site can't be reached" | Wait 10-15 seconds for startup, then refresh |
| SmartScreen blocks the EXE | Click "More info" then "Run anyway" |
| Shortcut not on Desktop | Re-run `create_desktop_shortcut.ps1` |
| PowerShell says "execution policy" error | Run PowerShell as administrator once, type: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Command window closes immediately | Check that `MellyTradeLauncher.exe` is in the same folder as the shortcut script |

---

## Artifact policy

The following files are local-only and must not be shared or committed to git:

```text
MellyTrade Terminal.lnk    (your Desktop shortcut)
MellyTrade-beta-v0.2-win64.zip    (the distribution archive)
```

Do not commit `.lnk` files to the repository.

---

## Related docs

- `beta_tester_desktop_launcher_quick_start.md` - quick start for the launcher itself
- `docs/qa/desktop_distribution_smoke_checklist.md` - operator validation checklist

---

*MellyTrade DESKTOP-001E - Beta Tester Desktop Distribution Notes - local-only, read-only, advisory.*
