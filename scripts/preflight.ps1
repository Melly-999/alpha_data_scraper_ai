$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $repoRoot "app"
$frontendRoot = Join-Path $repoRoot "frontend"

Write-Host "Repo root: $repoRoot"

if (-not (Test-Path (Join-Path $appRoot "main.py"))) {
    throw "app/main.py not found. Run this script from the MellyTrade repo checkout."
}

if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    throw "frontend/package.json not found. Run this script from the MellyTrade repo checkout."
}

python -c "import app; from app.main import app as fastapi_app; print('BACKEND_IMPORT_OK')"
npm --version *> $null

Write-Host "Preflight OK"
Write-Host "Backend: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"
Write-Host "Frontend: cd frontend; npm install; npm run dev"
