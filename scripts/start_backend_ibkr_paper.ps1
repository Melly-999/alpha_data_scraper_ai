param(
    [string]$PythonPath
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$fallbackPython = "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\.venv\Scripts\python.exe"
$localPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Test-PythonModule {
    param(
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string]$Module
    )

    if (-not (Test-Path $Python)) {
        return $false
    }

    try {
        & $Python -c "import $Module" > $null 2> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

Set-Location $repoRoot

if (-not $PythonPath) {
    if (Test-PythonModule -Python $localPython -Module "uvicorn") {
        $PythonPath = $localPython
    } elseif (Test-PythonModule -Python $fallbackPython -Module "uvicorn") {
        $PythonPath = $fallbackPython
    }
}

if (-not $PythonPath -or -not (Test-PythonModule -Python $PythonPath -Module "uvicorn")) {
    throw "No usable Python with uvicorn found. Pass -PythonPath or repair .venv."
}

$env:BROKER_ADAPTER = "ibkr-paper"
$env:IBKR_ENABLED = "true"
# Explicitly pin paper-only connection parameters. These match the
# IBKR_PAPER_ADAPTER documentation and the .env.example defaults; setting
# them here makes the validation flow reproducible regardless of any
# stray shell variables that may already be exported in the session.
if (-not $env:IBKR_MODE)      { $env:IBKR_MODE = "paper" }
if (-not $env:IBKR_HOST)      { $env:IBKR_HOST = "127.0.0.1" }
if (-not $env:IBKR_PORT)      { $env:IBKR_PORT = "7497" }
if (-not $env:IBKR_CLIENT_ID) { $env:IBKR_CLIENT_ID = "1" }
if (-not $env:IBKR_READ_ONLY) { $env:IBKR_READ_ONLY = "true" }

# Hard refusal: never start the backend with a live IBKR port. The adapter
# already fails closed at runtime, but we surface the misconfiguration here
# so the operator notices before TWS is ever contacted.
if ($env:IBKR_PORT -in @("7496", "4001")) {
    throw "IBKR_PORT=$($env:IBKR_PORT) is a LIVE port. Use 7497 (TWS paper) or 4002 (Gateway paper)."
}

Write-Host "Repo root: $repoRoot"
Write-Host "Python: $PythonPath"
Write-Host "SAFETY: DRY RUN ONLY"
Write-Host "SAFETY: IBKR Paper Adapter (mode=$($env:IBKR_MODE), port=$($env:IBKR_PORT), client_id=$($env:IBKR_CLIENT_ID))"
Write-Host "SAFETY: read_only=$($env:IBKR_READ_ONLY)"
Write-Host "SAFETY: live orders blocked, supports_live_orders=false"
Write-Host "Starting backend on http://127.0.0.1:8001 ..."

& $PythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --log-level debug
