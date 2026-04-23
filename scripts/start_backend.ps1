$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Repo root: $repoRoot"
Write-Host "Starting backend on http://127.0.0.1:8001 ..."

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

