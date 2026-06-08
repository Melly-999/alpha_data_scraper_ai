<#
.SYNOPSIS
    MellyTrade desktop (Tauri v2) thin-shell build wrapper.

.DESCRIPTION
    Builds the Windows desktop thin shell:
      * bundled static Vite frontend
      * hosted Render backend API (no backend bundled in the app)
      * no secrets, no broker execution, no order/buy/sell/execute controls

    The script injects the PUBLIC hosted backend URL into the frontend build
    environment, then invokes the Tauri build. The URL is public, not a secret.

    Safety posture preserved (read-only, paper-only, no live trading).

    Generated build output (frontend/src-tauri/target, frontend/dist) is
    git-ignored and must NOT be committed.

.PARAMETER NoBundle
    Compile the desktop binary without producing an installer (proof-of-build).
    This is the EXE-DESKTOP-002 default. Installer packaging is EXE-DESKTOP-003.

.PARAMETER ApiBase
    Override the hosted backend API base. Defaults to the public Render URL.

.EXAMPLE
    .\scripts\build_desktop_tauri.ps1 -NoBundle
    .\scripts\build_desktop_tauri.ps1
#>

[CmdletBinding()]
param(
    [switch]$NoBundle,
    [string]$ApiBase = "https://alpha-data-scraper-ai.onrender.com/api"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $repoRoot "frontend"

if (-not (Test-Path (Join-Path $frontend "src-tauri\tauri.conf.json"))) {
    throw "Tauri project not found at frontend/src-tauri. Run from the repo root."
}

# Ensure the Rust toolchain is on PATH (rustup default install location).
$cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
if (Test-Path $cargoBin) {
    $env:Path = "$cargoBin;$env:Path"
}

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    throw "cargo not found. Install the Rust toolchain (rustup) before building."
}

# Inject the PUBLIC hosted backend URL into the frontend build (no secrets).
$env:VITE_API_BASE_URL = $ApiBase
Write-Host "[INFO] VITE_API_BASE_URL = $ApiBase" -ForegroundColor Cyan

Push-Location $frontend
try {
    if ($NoBundle) {
        Write-Host "[INFO] Building desktop binary (no installer)..." -ForegroundColor Cyan
        npm run tauri:build -- --no-bundle
    }
    else {
        Write-Host "[INFO] Building desktop app + installer..." -ForegroundColor Cyan
        npm run tauri:build
    }
}
finally {
    Pop-Location
}

Write-Host "[OK] Desktop build complete." -ForegroundColor Green
Write-Host "[REMINDER] Do not commit frontend/src-tauri/target or frontend/dist." -ForegroundColor Yellow
