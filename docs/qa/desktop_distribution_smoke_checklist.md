# Desktop Distribution Smoke Checklist

## Purpose

Validate the Windows desktop distribution ZIP before sharing with beta testers.

---

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No broker credentials. No live trading. No order execution. Advisory output only.

---

## Preconditions

- [ ] `main` is clean (`git status --short` shows no tracked changes)
- [ ] `dist/MellyTradeLauncher.exe` exists and was built from current `main`
- [ ] ZIP was packed from the correct source files
- [ ] No secrets are required
- [ ] No broker credentials are required
- [ ] Live trading is not enabled

---

## Step 1 - Verify EXE exists

```powershell
Test-Path dist\MellyTradeLauncher.exe
```

Expected: `True`

- [ ] EXE exists at `dist\MellyTradeLauncher.exe`

---

## Step 2 - Verify ZIP contents

```powershell
$zip = [System.IO.Compression.ZipFile]::OpenRead("dist\MellyTrade-beta-v0.2-win64.zip")
$zip.Entries | Select-Object FullName, Length
$zip.Dispose()
```

Expected entries:

- [ ] `MellyTradeLauncher.exe` present
- [ ] `create_desktop_shortcut.ps1` present
- [ ] `beta_tester_desktop_launcher_quick_start.md` present
- [ ] No `.env` files present
- [ ] No secrets or credential files present

---

## Step 3 - Verify no secrets bundled

Inspect the ZIP contents:

- [ ] No file named `.env`, `secrets.json`, `credentials.json`, or similar
- [ ] No `SUPABASE_SERVICE_ROLE_KEY` string in any bundled text file
- [ ] No `MT5_PASSWORD` string in any bundled text file
- [ ] No `api_key` or `account_id` in any bundled text file

---

## Step 4 - Extract and run shortcut creator

Extract ZIP to a temp folder:

```powershell
Expand-Archive dist\MellyTrade-beta-v0.2-win64.zip C:\Temp\MellyTrade-test\ -Force
cd C:\Temp\MellyTrade-test\
.\create_desktop_shortcut.ps1 -WhatIfOnly
```

Expected:

- [ ] Prints safety banner with `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`
- [ ] Prints target path pointing to `MellyTradeLauncher.exe`
- [ ] Does NOT create a `.lnk` file in WhatIf mode
- [ ] Does NOT run the EXE
- [ ] Does NOT start backend or frontend
- [ ] Exits with code 0

---

## Step 5 - Verify no `.lnk` committed

```powershell
git status --short *.lnk
git status --short dist build
```

Expected:

- [ ] No `.lnk` file staged or committed
- [ ] `dist/` and `build/` are gitignored (not tracked)

---

## Step 6 - Safety posture check

Run the safety validator:

```powershell
py -3.11 scripts\validate_safety_config.py
```

Expected:

- [ ] All checks pass
- [ ] `autotrade=false` confirmed
- [ ] `dry_run=true` confirmed
- [ ] `read_only=true` confirmed

---

## Red flags - stop and report if any of the following occur

- [ ] ZIP contains a `.env` file
- [ ] ZIP contains broker credentials
- [ ] ZIP contains a file that enables `autotrade=true`
- [ ] ZIP contains a file that sets `dry_run=false`
- [ ] EXE connects to a non-localhost address at startup
- [ ] Shortcut creator requires admin elevation
- [ ] Shortcut creator makes network calls
- [ ] Any artifact is staged for commit (`git status --short` shows `A` prefix)

---

## Local artifacts reminder

The following must not be committed:

```text
*.lnk
*.zip
*.msi
dist/
build/
*.spec
*.exe
```

These are local-only artifacts. Verify with:

```powershell
git status --short *.lnk *.zip *.msi
git status --short dist build
git status --short *.spec
```

---

## SmartScreen note

The v0.2 beta EXE is not code-signed. Testers will see a Windows SmartScreen
warning. This is expected. Workaround: click "More info" then "Run anyway".

Document this in the tester email alongside the download link.

---

*MellyTrade DESKTOP-001E - Distribution Smoke Checklist - local-only, read-only, advisory.*
