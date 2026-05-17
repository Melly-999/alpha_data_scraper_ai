<#
.SYNOPSIS
    MellyTrade Desktop Launcher - create a Windows shortcut helper.

.DESCRIPTION
    Creates a local Windows .lnk shortcut pointing to the MellyTrade launcher EXE.

    This script:
      - Runs locally only.
      - Does not require admin.
      - Does not modify repo config.
      - Does not modify backend/frontend files.
      - Does not install dependencies.
      - Does not start the app.
      - Does not run the EXE.
      - Does not make network calls.
      - Does not include secrets or broker credentials.
      - Does not enable live trading.
      - Does not create order/execution controls.

    The generated .lnk file is a local Desktop shortcut only.
    Do NOT commit .lnk files to the repository.

    Safety posture (enforced by the launcher this shortcut targets):
      autotrade=false
      dry_run=true
      read_only=true
      live_orders_blocked=true
      max risk 1% max

.PARAMETER ShortcutPath
    Full path for the .lnk file to create.
    Default: <user Desktop>\MellyTrade Terminal.lnk

.PARAMETER TargetPath
    Path to the EXE the shortcut points to.
    Default: <repo root>\dist\MellyTradeLauncher.exe

.PARAMETER WorkingDirectory
    Working directory set in the shortcut.
    Default: <repo root>

.PARAMETER Arguments
    Arguments passed to the EXE.
    Default: empty string.
    Overridden by -NoBrowser if that switch is also present.

.PARAMETER NoBrowser
    If present, sets shortcut arguments to --no-browser.

.PARAMETER WhatIfOnly
    If present, prints what would be created and exits without writing the shortcut.

.EXAMPLE
    .\scripts\create_desktop_shortcut.ps1 -WhatIfOnly
    .\scripts\create_desktop_shortcut.ps1
    .\scripts\create_desktop_shortcut.ps1 -NoBrowser
    .\scripts\create_desktop_shortcut.ps1 -ShortcutPath "C:\Users\me\Desktop\MellyTrade.lnk"

#>

[CmdletBinding()]
param(
    [string]$ShortcutPath    = "",
    [string]$TargetPath      = "",
    [string]$WorkingDirectory = "",
    [string]$Arguments       = "",
    [switch]$NoBrowser,
    [switch]$WhatIfOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve repo root from script location
# ---------------------------------------------------------------------------

$ScriptDir = $PSScriptRoot
$RepoRoot  = Resolve-Path (Join-Path $ScriptDir "..")

# ---------------------------------------------------------------------------
# Apply defaults
# ---------------------------------------------------------------------------

if (-not $ShortcutPath) {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "MellyTrade Terminal.lnk"
}

if (-not $TargetPath) {
    $DistDir    = Join-Path $RepoRoot "dist"
    $TargetPath = Join-Path $DistDir "MellyTradeLauncher.exe"
}

if (-not $WorkingDirectory) {
    $WorkingDirectory = $RepoRoot
}

if ($NoBrowser) {
    $Arguments = "--no-browser"
}

# ---------------------------------------------------------------------------
# Safety banner
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "======================================================"
Write-Host "  MellyTrade Desktop Launcher - Shortcut Creator"
Write-Host "======================================================"
Write-Host "  SAFETY: autotrade=false"
Write-Host "  SAFETY: dry_run=true"
Write-Host "  SAFETY: read_only=true"
Write-Host "  SAFETY: live_orders_blocked=true"
Write-Host '  SAFETY: max risk <=1%'
Write-Host "  No broker credentials."
Write-Host "  No live trading."
Write-Host "  No order execution."
Write-Host "======================================================"
Write-Host ""

# ---------------------------------------------------------------------------
# WhatIf mode - print what would be created and exit
# ---------------------------------------------------------------------------

if ($WhatIfOnly) {
    Write-Host "[WHATIF] Would create shortcut with:"
    Write-Host "  Shortcut path:    $ShortcutPath"
    Write-Host "  Target EXE:       $TargetPath"
    Write-Host "  Working dir:      $WorkingDirectory"
    if ($Arguments) {
        Write-Host "  Arguments:        $Arguments"
    } else {
        Write-Host "  Arguments:        (none)"
    }
    Write-Host ""
    Write-Host "[WHATIF] No .lnk file was created."
    Write-Host "[WHATIF] No app was started."
    Write-Host "[WHATIF] No repo files were modified."
    Write-Host ""
    exit 0
}

# ---------------------------------------------------------------------------
# Verify target EXE exists
# ---------------------------------------------------------------------------

Write-Host "[CHECK] Target EXE: $TargetPath"
if (-not (Test-Path $TargetPath)) {
    Write-Host ""
    Write-Host "[ERROR] MellyTradeLauncher.exe not found at:"
    Write-Host "        $TargetPath"
    Write-Host ""
    Write-Host "  Build it first with:"
    Write-Host "    .\scripts\build_desktop_launcher.ps1 -Build"
    Write-Host ""
    Write-Host "  Then re-run:"
    Write-Host "    .\scripts\create_desktop_shortcut.ps1"
    Write-Host ""
    exit 1
}
Write-Host "  [PASS] EXE found."
Write-Host ""

# ---------------------------------------------------------------------------
# Create .lnk via WScript.Shell
# ---------------------------------------------------------------------------

Write-Host "[CREATE] Creating shortcut..."
Write-Host "  Shortcut path: $ShortcutPath"
Write-Host "  Target EXE:    $TargetPath"
Write-Host "  Working dir:   $WorkingDirectory"
if ($Arguments) {
    Write-Host "  Arguments:     $Arguments"
}
Write-Host ""

$WshShell   = New-Object -ComObject WScript.Shell
$Shortcut   = $WshShell.CreateShortcut($ShortcutPath)

$Shortcut.TargetPath       = $TargetPath
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.Arguments        = $Arguments
$Shortcut.WindowStyle      = 1   # Normal window
$Shortcut.Description      = "MellyTrade Local Launcher - read-only / dry-run demo"

$Shortcut.Save()

# ---------------------------------------------------------------------------
# Confirm and remind
# ---------------------------------------------------------------------------

if (Test-Path $ShortcutPath) {
    Write-Host "[PASS] Shortcut created:"
    Write-Host "  $ShortcutPath"
    Write-Host ""
    Write-Host "  Double-click the shortcut to launch MellyTrade locally."
    Write-Host "  The launcher will start backend + frontend and open the terminal UI."
    Write-Host ""
    Write-Host "======================================================"
    Write-Host "  REMINDER: Do NOT commit .lnk files to git."
    Write-Host "  The shortcut is a local file only."
    Write-Host "======================================================"
    Write-Host ""
    Write-Host "  SAFETY: autotrade=false"
    Write-Host "  SAFETY: dry_run=true"
    Write-Host "  SAFETY: read_only=true"
    Write-Host "  SAFETY: live_orders_blocked=true"
    Write-Host '  SAFETY: max risk <=1%'
    Write-Host "  No broker credentials."
    Write-Host "  No live trading."
    Write-Host "  No order execution."
    Write-Host "======================================================"
    Write-Host ""
} else {
    Write-Host "[ERROR] Shortcut not found after Save() - unexpected failure."
    Write-Host "        Path: $ShortcutPath"
    exit 1
}
