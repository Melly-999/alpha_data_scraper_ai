param(
    [string]$Port = "8001",
    [string]$PythonPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$LocalPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Test-PythonModule {
    param(
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string]$Module
    )
    if (-not (Test-Path $Python)) { return $false }
    try {
        & $Python -c "import $Module" *> $null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

Set-Location $RepoRoot

$PyArgs = @()

if (-not $PythonPath) {
    if (Test-PythonModule -Python $LocalPython -Module "uvicorn") {
        $PythonPath = $LocalPython
    } else {
        $PythonPath = "py"
        $PyArgs = @("-3.11")
    }
}

if ($PythonPath -ne "py" -and -not (Test-PythonModule -Python $PythonPath -Module "uvicorn")) {
    throw "No usable Python with uvicorn found. Pass -PythonPath or repair .venv."
}

# Hard safety: never bind to 0.0.0.0 -- loopback only
$BindHost = "127.0.0.1"
$BackendUrl = "http://$($BindHost):$Port"

Write-Host ""
Write-Host "======================================================"
Write-Host "  MellyTrade Local Backend -- READ-ONLY / DRY-RUN"
Write-Host "======================================================"
Write-Host "  SAFETY: autotrade=false   dry_run=true"
Write-Host "  SAFETY: live orders blocked   read_only=true"
Write-Host "  SAFETY: max_risk_per_trade <= 1%"
Write-Host "  SAFETY: no broker connection required"
Write-Host "  Host:   $($BindHost):$Port (loopback only)"
Write-Host "  URL:    $BackendUrl"
Write-Host "  Docs:   $BackendUrl/docs"
Write-Host "======================================================"
Write-Host ""

$uvicornArgs = @("-m", "uvicorn", "app.main:app", "--host", $BindHost, "--port", $Port, "--log-level", "info")

if ($PythonPath -eq "py") {
    & $PythonPath @PyArgs @uvicornArgs
} else {
    & $PythonPath @uvicornArgs
}
