param(
    [string]$BackendPort = "8001",
    [string]$FrontendPort = "5173"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FrontendRoot = Join-Path $RepoRoot "frontend"

if (-not (Test-Path (Join-Path $FrontendRoot "package.json"))) {
    throw "frontend/package.json not found. Expected repo root at: $RepoRoot"
}

# Wire the frontend to the local backend directly, bypassing the Vite proxy
# that targets port 8000 (which may be occupied by an unrelated process).
# VITE_MELLY_API_BASE_URL overrides the /melly-api proxy in vite.config.ts
# so mellyApi.ts calls go straight to the local backend at port $BackendPort.
$env:VITE_MELLY_API_BASE_URL = "http://127.0.0.1:$BackendPort"
$env:VITE_API_BASE_URL = "http://127.0.0.1:$BackendPort/api"

Set-Location $FrontendRoot

if (-not (Test-Path (Join-Path $FrontendRoot "node_modules"))) {
    Write-Host "Installing frontend dependencies ..."
    npm install
} else {
    Write-Host "Frontend dependencies already installed."
}

Write-Host ""
Write-Host "======================================================"
Write-Host "  MellyTrade Local Frontend -- READ-ONLY / DRY-RUN"
Write-Host "======================================================"
Write-Host "  SAFETY: no execution buttons   no order routes"
Write-Host "  VITE_MELLY_API_BASE_URL: $env:VITE_MELLY_API_BASE_URL"
Write-Host "  VITE_API_BASE_URL:       $env:VITE_API_BASE_URL"
Write-Host "  Frontend: http://127.0.0.1:$FrontendPort"
Write-Host "  Terminal: http://127.0.0.1:$FrontendPort/terminal"
Write-Host "======================================================"
Write-Host ""

npm run dev -- --host 127.0.0.1 --port $FrontendPort
