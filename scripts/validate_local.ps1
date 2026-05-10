Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [scriptblock] $Command
    )

    Write-Host ""
    Write-Host "==> $Name"
    $global:LASTEXITCODE = 0

    try {
        & $Command
        if ($global:LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $global:LASTEXITCODE"
        }
    }
    catch {
        Write-Host ""
        Write-Host "VALIDATION FAILED: $Name"
        Write-Host $_
        exit 1
    }
}

function Test-FrontendChanged {
    $global:LASTEXITCODE = 0
    git rev-parse --verify origin/main *> $null
    if ($global:LASTEXITCODE -ne 0) {
        Write-Warning "origin/main is unavailable; skipping frontend change detection and frontend build."
        return $false
    }

    $global:LASTEXITCODE = 0
    $changedFiles = @(git diff --name-only origin/main...HEAD -- frontend)
    if ($global:LASTEXITCODE -ne 0) {
        Write-Warning "Could not compare frontend changes against origin/main; skipping frontend build."
        return $false
    }

    return $changedFiles.Count -gt 0
}

Write-Host "MellyTrade local validation"
Write-Host "Repo: $RepoRoot"

Invoke-Step "Safety configuration validation" {
    py -3.11 scripts/validate_safety_config.py
}

Invoke-Step "App pytest suite" {
    py -3.11 -m pytest tests/app/ -q
}

if (Test-FrontendChanged) {
    Invoke-Step "Frontend build" {
        Push-Location frontend
        try {
            npm run build
        }
        finally {
            Pop-Location
        }
    }
}
else {
    Write-Host ""
    Write-Host "Skipping frontend build: no frontend files changed."
}

Write-Host ""
Write-Host "VALIDATION PASSED"
