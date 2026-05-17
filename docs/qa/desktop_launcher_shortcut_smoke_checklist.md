# Desktop Launcher Shortcut Smoke Checklist

## Purpose

Validate the Windows shortcut helper for the local MellyTrade launcher
(`scripts/create_desktop_shortcut.ps1`).

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
- [ ] `dist/MellyTradeLauncher.exe` exists locally
- [ ] Generated artifacts are local-only and not committed (`dist/`, `build/`, `*.spec`, `*.exe`)
- [ ] No secrets are required
- [ ] No broker credentials are required
- [ ] Live trading is not enabled

---

## WhatIf check

```powershell
.\scripts\create_desktop_shortcut.ps1 -WhatIfOnly
```

**Expected:**

- [ ] Prints target path (`dist/MellyTradeLauncher.exe`)
- [ ] Prints shortcut path (`<Desktop>\MellyTrade Terminal.lnk`)
- [ ] Prints working directory (repo root)
- [ ] Does **not** create a `.lnk` file
- [ ] Does **not** run the EXE
- [ ] Does **not** start backend or frontend
- [ ] Exits with code 0 if EXE exists, or prints clear build instruction if EXE is missing

**Verify no `.lnk` created:**

```powershell
git status --short *.lnk
Test-Path "$env:USERPROFILE\Desktop\MellyTrade Terminal.lnk"
```

Expected: no `.lnk` file at Desktop path after `-WhatIfOnly`.

---

## Create shortcut manually

```powershell
.\scripts\create_desktop_shortcut.ps1
```

**Expected:**

- [ ] Creates `MellyTrade Terminal.lnk` on user Desktop
- [ ] Shortcut target points to `dist/MellyTradeLauncher.exe` (resolved absolute path)
- [ ] Working directory points to repo root
- [ ] Safety banner is printed at creation time
- [ ] No repo files are modified
- [ ] `.lnk` file is **not** staged for commit (`git status --short` shows it untracked or not listed)

**Verify:**

```powershell
Test-Path "$env:USERPROFILE\Desktop\MellyTrade Terminal.lnk"
git status --short
```

---

## Optional no-browser shortcut

```powershell
.\scripts\create_desktop_shortcut.ps1 -NoBrowser
```

**Expected:**

- [ ] Shortcut arguments include `--no-browser`
- [ ] All other creation checks apply

---

## Custom path shortcut

```powershell
.\scripts\create_desktop_shortcut.ps1 -ShortcutPath "C:\Temp\MellyTrade.lnk"
```

**Expected:**

- [ ] Creates `.lnk` at the specified path
- [ ] Does **not** write to user Desktop if a custom path is given

---

## Red flags — stop and report if any of the following occur

- [ ] Shortcut asks for broker credentials
- [ ] Shortcut asks for API keys
- [ ] Shortcut enables live trading (`autotrade=true`)
- [ ] Shortcut disables dry-run (`dry_run=false`)
- [ ] Shortcut changes config files
- [ ] Shortcut points to a URL outside localhost/repo unexpectedly
- [ ] Shortcut starts unrelated processes
- [ ] `.lnk` file is staged for commit (`git status --short` shows `A` prefix)
- [ ] Script produces network calls

---

## Local artifacts reminder

The following must not be committed:

```text
*.lnk
dist/
build/
*.spec
*.exe
```

These are local-only artifacts. Verify with:

```powershell
git status --short *.lnk
git status --short dist build
git status --short *.spec
```

---

*MellyTrade DESKTOP-001D — Shortcut Smoke Checklist — local-only, read-only, advisory.*
