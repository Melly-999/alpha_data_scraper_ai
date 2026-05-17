# DESKTOP-001E - Windows Desktop Distribution Plan

> Planning document only. Does not implement any installer, package, or
> distribution artifact. Does not change runtime behaviour or safety posture.

---

## Goal

Define a distribution path for the MellyTrade Windows desktop launcher so that
beta testers can install the launcher without manual repo cloning or CLI steps.

---

## Context

DESKTOP-001D delivered a local shortcut helper (`create_desktop_shortcut.ps1`)
that assumes the tester has already cloned the repo and built the EXE via
PyInstaller. This is friction for non-technical beta testers.

DESKTOP-001E plans the next distribution step: a standalone distributable that
a tester can download and run without a repo checkout.

---

## Required safety posture (enforced by launcher)

```text
autotrade           = false
dry_run             = true
read_only           = true
live_orders_blocked = true
max risk            <= 1%
```

All distribution artifacts must launch the application with these defaults
active. No distribution artifact may expose controls that change these values.

---

## Distribution options considered

### Option A - Simple ZIP archive (recommended for v0.2 beta)

Pack the following into a ZIP:

```text
MellyTrade-beta-v0.2-win64.zip
  dist/MellyTradeLauncher.exe
  scripts/create_desktop_shortcut.ps1
  docs/product/beta_tester_desktop_launcher_quick_start.md
  README_BETA.txt
```

**Pros:**
- No installer required
- No admin required
- Transparent - tester can inspect all files
- Tester extracts, runs `create_desktop_shortcut.ps1`, clicks shortcut

**Cons:**
- Tester must extract ZIP manually
- No auto-update
- No Start Menu entry without manual shortcut creation

**Recommended for:** v0.2 closed beta (non-technical testers, small cohort)

---

### Option B - NSIS or Inno Setup installer (future)

A traditional Windows installer (`.msi` or `.exe` setup) that:
- Copies the EXE to `%LOCALAPPDATA%\MellyTrade\`
- Creates a Start Menu entry
- Creates a Desktop shortcut
- Does NOT require admin (NSIS/Inno support user-level installs)

**Not planned for v0.2.** Tracked for v0.3 or later.

---

### Option C - Winget / Microsoft Store (future)

Package for the Windows Package Manager (`winget`) or Microsoft Store
distribution. Requires code signing and Microsoft review.

**Not planned for v0.2.** Tracked for post-launch.

---

### Option D - Tauri / Electron wrapper (future)

Replace the Python + PyInstaller approach with a Tauri or Electron app shell
that bundles its own updater and installer.

**Not planned for v0.2.** Tracked in DESKTOP-001 plan as Phase 2.

---

## Recommended v0.2 distribution path (Option A)

### Step 1 - Build EXE

```powershell
.\scripts\build_desktop_launcher.ps1 -Build
```

Output: `dist\MellyTradeLauncher.exe`

### Step 2 - Pack ZIP

```powershell
$Version = "beta-v0.2"
$ZipName = "MellyTrade-$Version-win64.zip"
Compress-Archive -Path @(
    "dist\MellyTradeLauncher.exe",
    "scripts\create_desktop_shortcut.ps1",
    "docs\product\beta_tester_desktop_launcher_quick_start.md"
) -DestinationPath "dist\$ZipName"
```

### Step 3 - Verify ZIP contents

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("dist\$ZipName")
$zip.Entries | Select-Object FullName, Length
$zip.Dispose()
```

Expected entries:
- `MellyTradeLauncher.exe`
- `create_desktop_shortcut.ps1`
- `beta_tester_desktop_launcher_quick_start.md`

### Step 4 - Distribute

Upload the ZIP to the closed beta distribution channel (e.g. private Google
Drive, Notion attachment, or private GitHub release asset). Share the download
link with beta testers via the tester onboarding email.

### Step 5 - Tester workflow

1. Download `MellyTrade-beta-v0.2-win64.zip`
2. Extract to a local folder (e.g. `C:\MellyTrade\`)
3. Right-click `create_desktop_shortcut.ps1` - Run with PowerShell
4. Confirm safety banner printed - all 4 flags `true`
5. Double-click `MellyTrade Terminal.lnk` on Desktop
6. Browser opens to `http://localhost:5173/terminal`

---

## Safety constraints

The distribution ZIP must NOT contain:

- `.env` files or secrets
- Broker credentials
- `autotrade=true` config
- `dry_run=false` config
- Any file that enables live trading
- Any file that exposes order buttons or account IDs
- Code-signed executables presented as official Anthropic/MellyTrade signed
  builds (signing is not implemented for v0.2)

---

## Artifact policy

The following are local-only and must NOT be committed to the repository:

```text
dist/
build/
*.spec
*.exe
*.zip
*.msi
```

The ZIP is distributed out-of-band (not via git). Verify with:

```powershell
git status --short dist build
git status --short *.zip *.msi
```

---

## Code signing note

The v0.2 beta EXE is NOT code-signed. Testers will see a Windows SmartScreen
warning ("Windows protected your PC"). Workaround:

1. Click "More info"
2. Click "Run anyway"

This is expected for a closed beta. Code signing is tracked for v0.3+.

---

## Acceptance criteria for v0.2 distribution

- [ ] `dist/MellyTradeLauncher.exe` built without errors
- [ ] ZIP packs correctly - all 3 expected files present
- [ ] Tester can extract ZIP and run `create_desktop_shortcut.ps1` without admin
- [ ] Shortcut created on tester Desktop points to correct EXE
- [ ] Launcher starts backend and frontend on localhost
- [ ] Safety validator passes after startup (`py -3.11 scripts/validate_safety_config.py`)
- [ ] No secrets bundled in ZIP
- [ ] No mutation controls introduced
- [ ] SmartScreen workaround documented in tester quick start

---

## What this document does NOT do

This is a planning document only. It does not:

- Build the EXE
- Create the ZIP
- Upload any artifact
- Change any config
- Enable live trading
- Add order execution

Implementation is tracked as DESKTOP-001E. Actual distribution is an out-of-band
operational step, not a code change.

---

## Related docs

- `docs/tasks/desktop_launcher_exe_plan.md` - full DESKTOP-001 plan and status
- `docs/qa/desktop_distribution_smoke_checklist.md` - distribution smoke checklist
- `docs/product/beta_tester_desktop_distribution_notes.md` - tester-facing notes
- `docs/product/beta_tester_desktop_launcher_quick_start.md` - launcher quick start
- `docs/qa/desktop_launcher_shortcut_smoke_checklist.md` - shortcut smoke checklist
- `scripts/build_desktop_launcher.ps1` - PyInstaller build script
- `scripts/create_desktop_shortcut.ps1` - shortcut creator script

---

*MellyTrade DESKTOP-001E - Windows Desktop Distribution Plan - planning only.*
