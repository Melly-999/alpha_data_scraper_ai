param(
    [string]$InstallRequirements = "true"
)

$ErrorActionPreference = "Stop"

$installDeps = $true
if ($InstallRequirements -match "^(false|0|no)$") {
    $installDeps = $false
}

function Get-UsablePython {
    $candidates = @(
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return "py -3.12"
    }

    return $null
}

$pythonCmd = Get-UsablePython
if (-not $pythonCmd) {
    Write-Host "Nie znaleziono dzialajacego interpretera Python 3.11/3.12." -ForegroundColor Red
    Write-Host "Zainstaluj 64-bitowy CPython, a potem uruchom ten skrypt ponownie." -ForegroundColor Yellow
    Write-Host "Przyklad: winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 1
}

Write-Host "Uzywany interpreter: $pythonCmd" -ForegroundColor Cyan

if ($pythonCmd -like "py *") {
    Invoke-Expression "$pythonCmd -m venv .venv"
} else {
    & $pythonCmd -m venv .venv
}

$venvPython = Join-Path $PWD ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Nie udalo sie utworzyc .venv" -ForegroundColor Red
    exit 1
}

& $venvPython -m pip install --upgrade pip

if ($installDeps) {
    & $venvPython -m pip install -r requirements.txt
}

Write-Host "Srodowisko gotowe." -ForegroundColor Green
Write-Host "Aktywacja: .\.venv\Scripts\Activate.ps1"
Write-Host "Uruchomienie: .\.venv\Scripts\python.exe main.py"
Write-Host "Testy: .\.venv\Scripts\python.exe -m pytest -q"