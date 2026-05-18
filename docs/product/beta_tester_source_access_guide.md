# Beta Tester Source Access Guide

Local read-only demo. Advisory output only. Human review required.

---

## What you receive

As a source-only beta tester you receive:

- Read-only GitHub repository access
- Setup instructions
- Local launcher build instructions (PyInstaller, local-only)
- Desktop launcher quick start guide
- Shortcut helper instructions
- This guide

You do **not** receive a pre-built EXE, an installer, or a ZIP package at this stage.

---

## What you do not receive

- Final installer or setup wizard
- Public EXE release artifact
- Code-signed application
- Auto-updater
- Live trading access
- Broker execution access
- Investment advice
- Guaranteed profit claims

---

## Safety posture

Every session runs with:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

The safety banner is printed at every launch. If you do not see it, stop and report.

---

## Safe first run

Follow these steps in order:

### 1. Clone the repository

```powershell
git clone <repo-url>
cd alpha_data_scraper_ai
```

Use the read-only HTTPS URL provided to you. Do not use a write-access token.

### 2. Read the quick start

Open and read:

```text
docs/product/beta_tester_desktop_launcher_quick_start.md
```

### 3. Run safety validation

```powershell
py -3.11 scripts/validate_safety_config.py
```

Expected: OVERALL: PASS — if this fails, stop and report.

### 4. Build the local launcher

```powershell
.\scripts\build_desktop_launcher.ps1 -Build
```

This builds `dist\MellyTradeLauncher.exe` locally. The EXE is local-only and
must not be shared or committed.

### 5. Create Desktop shortcut

```powershell
.\scripts\create_desktop_shortcut.ps1
```

Confirm the safety banner is printed:

```
SAFETY: autotrade=false
SAFETY: dry_run=true
SAFETY: read_only=true
SAFETY: live_orders_blocked=true
```

If any flag is missing, stop and report.

### 6. Run the local launcher

Double-click "MellyTrade Terminal" on your Desktop.

Your browser will open to:

```
http://localhost:5173/terminal
```

### 7. Confirm safety banner

Verify in the terminal UI that:

- The interface shows advisory output only
- No order buttons are visible
- No live trading controls are visible
- No broker credential inputs are shown

### 8. Report issues

Use the feedback channel provided in your tester onboarding email.

---

## Do not enter

Under no circumstances should you enter the following into the application:

- Broker credentials (username, password, server)
- MT5 login details
- API keys of any kind
- Account IDs
- Supabase keys or service role tokens
- Any secret or credential

The application does not require any of these for the local demo.

---

## Stop and report

Stop immediately and report to the operator if any of the following occur:

- The safety banner is missing at launch
- Any flag in the safety banner shows a value other than `false`/`true` as expected
- Live trading appears to be enabled
- Dry-run mode appears disabled
- Read-only mode appears disabled
- Any order button, trade execution button, or broker connection control appears
- The application requests broker credentials
- The application makes investment-advice claims
- The application claims guaranteed profit
- The application connects to any address outside `localhost`

---

## Artifact policy

The following are local-only and must not be committed to the repository or
shared outside the tester cohort:

```text
dist\MellyTradeLauncher.exe    (your local build)
MellyTrade Terminal.lnk        (your Desktop shortcut)
build\                         (PyInstaller build directory)
*.spec                         (PyInstaller spec file)
```

Do not share these files. Do not commit them to git.

---

## Related docs

- `docs/product/beta_tester_desktop_launcher_quick_start.md` - launcher quick start
- `docs/product/beta_tester_desktop_distribution_notes.md` - distribution notes
- `docs/qa/source_only_beta_preflight_checklist.md` - operator preflight checklist
- `docs/qa/desktop_launcher_shortcut_smoke_checklist.md` - shortcut smoke checklist

---

*MellyTrade DESKTOP-001F - Beta Tester Source Access Guide - local-only, read-only, advisory.*
