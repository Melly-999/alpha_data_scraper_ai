$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

try {
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        & $venvPython -m pytest @args
        exit $LASTEXITCODE
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source -m pytest @args
        exit $LASTEXITCODE
    }

    Write-Host "Nie znaleziono interpretera Python. Uruchom najpierw .\setup_windows.ps1" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}
