$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    throw "frontend/package.json not found. Expected repo root at: $repoRoot"
}

Set-Location $frontendRoot

Write-Host "Repo root: $repoRoot"
Write-Host "Frontend root: $frontendRoot"
Write-Host "Installing frontend dependencies if needed ..."
npm install

Write-Host "Starting frontend dev server ..."
npm run dev

