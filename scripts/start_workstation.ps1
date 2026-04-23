$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Running MellyTrade Phase 2 preflight ..."
& (Join-Path $PSScriptRoot "preflight.ps1")

Write-Host ""
Write-Host "Start backend in one PowerShell:"
Write-Host "  cd $repoRoot"
Write-Host "  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"
Write-Host ""
Write-Host "Start frontend in another PowerShell:"
Write-Host "  cd $repoRoot\\frontend"
Write-Host "  npm install"
Write-Host "  npm run dev"
