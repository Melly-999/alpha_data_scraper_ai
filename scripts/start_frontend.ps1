$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    throw "frontend/package.json not found. Expected repo root at: $repoRoot"
}

Set-Location $frontendRoot

Write-Host "Repo root: $repoRoot"
Write-Host "Frontend root: $frontendRoot"

if (-not $env:VITE_API_BASE_URL) {
    $env:VITE_API_BASE_URL = "http://127.0.0.1:8001/api"
}

Write-Host "Using VITE_API_BASE_URL=$env:VITE_API_BASE_URL"

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
    Write-Host "Installing frontend dependencies ..."
    npm install
} else {
    Write-Host "Frontend dependencies already installed."
}

Write-Host "Starting frontend dev server ..."
npm run dev

