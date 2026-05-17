# Desktop Launcher Build Validation

## Purpose

Validate local PyInstaller packaging for the MellyTrade launcher.

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

No live trading. No broker execution. Advisory output only.

---

## Build command

```powershell
.\scripts\build_desktop_launcher.ps1 -Build
```

---

## Expected local artifacts

```text
dist/MellyTradeLauncher.exe
build/
MellyTradeLauncher.spec
```

---

## Commit policy

The following must not be committed:

```text
dist/
build/
*.spec
*.exe
```

These are covered by `.gitignore` and must remain local-only.

---

## Validation checklist

- [ ] PyInstaller installed locally
- [ ] build script exits successfully
- [ ] `dist/MellyTradeLauncher.exe` exists
- [ ] executable size is greater than 0
- [ ] generated artifacts are not staged
- [ ] generated artifacts are ignored or kept local-only
- [ ] safety validator still passes
- [ ] static launcher tests still pass

---

## Runtime smoke

Run local executable manually:

```powershell
.\dist\MellyTradeLauncher.exe --no-browser
```

Expected:

- [ ] safety banner appears
- [ ] backend helper starts or is skipped only if requested
- [ ] frontend helper starts or is skipped only if requested
- [ ] no broker credentials requested
- [ ] no live trading enabled
- [ ] no order/execution controls added

Do not commit runtime screenshots or generated binaries in this PR.

---

*MellyTrade DESKTOP-001B — PyInstaller Build Validation — local-only, read-only, advisory.*
