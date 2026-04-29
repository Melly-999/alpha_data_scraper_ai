$ErrorActionPreference = "Continue"

$repoRoot = Split-Path -Parent $PSScriptRoot
$localPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$fallbackPython = "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\.venv\Scripts\python.exe"

function Test-Module {
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

Write-Host "Repo root: $repoRoot"
Write-Host "Branch: $(git rev-parse --abbrev-ref HEAD)"
Write-Host "HEAD: $(git rev-parse --short HEAD)"

Write-Host ""
Write-Host "Python launcher versions:"
if (Get-Command py -ErrorAction SilentlyContinue) {
    py -0p
} else {
    Write-Host "py launcher not found"
}

Write-Host ""
Write-Host "Local .venv exists: $(Test-Path (Join-Path $repoRoot '.venv'))"
Write-Host "Local .venv python: $(Test-Path $localPython)"
Write-Host "Local .venv pip: $(Test-Module -Python $localPython -Module 'pip')"
Write-Host "Local .venv uvicorn: $(Test-Module -Python $localPython -Module 'uvicorn')"
Write-Host "Fallback venv exists: $(Test-Path $fallbackPython)"
Write-Host "Fallback venv uvicorn: $(Test-Module -Python $fallbackPython -Module 'uvicorn')"

Write-Host ""
Write-Host "IBKR route file: $(Test-Path (Join-Path $repoRoot 'app\api\routes\broker.py'))"
Write-Host "IBKR adapter file: $(Test-Path (Join-Path $repoRoot 'brokers\ibkr_paper.py'))"
Write-Host "IBKR docs: $(Test-Path (Join-Path $repoRoot 'docs\IBKR_PAPER_ADAPTER.md'))"
Write-Host ".env exists: $(Test-Path (Join-Path $repoRoot '.env'))"
Write-Host ".env.example exists: $(Test-Path (Join-Path $repoRoot '.env.example'))"

if (-not (Test-Module -Python $localPython -Module "pip") -or -not (Test-Module -Python $localPython -Module "uvicorn")) {
    Write-Host ""
    Write-Host "WARN: local .venv is missing pip or uvicorn."
    Write-Host "Recommendation for today: use scripts\start_backend_ibkr_paper.ps1 fallback venv."
}
