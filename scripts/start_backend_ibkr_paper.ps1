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

Write-Host "Repo root: $repoRoot"
Write-Host "Python: $PythonPath"
Write-Host "SAFETY: DRY RUN ONLY"
Write-Host "SAFETY: IBKR Paper Adapter"
Write-Host "SAFETY: live orders blocked"
Write-Host "Starting backend on http://127.0.0.1:8001 ..."

& $PythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --log-level debug
