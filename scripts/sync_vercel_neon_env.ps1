# Sync Neon DATABASE_URL to Vercel environments for branch `vercel-dev`.
# Requires: vercel CLI logged in, project linked (`vercel link`).
# Usage: pwsh scripts/sync_vercel_neon_env.ps1 [-ProjectName <org/team scope>]
# Note: `-ProjectName` maps to Vercel's `--scope` flag (team/org scope).

param(
    [string]$ProjectName = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repoRoot ".env"

if (-not (Test-Path $envFile)) {
    throw ".env not found. Copy .env.example and set DATABASE_URL_VERCEL_DEV first."
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

if (-not $env:DATABASE_URL_VERCEL_DEV) {
    throw "DATABASE_URL_VERCEL_DEV is missing from .env"
}

$vercelArgs = @("env", "add", "DATABASE_URL", "preview", "--force")
if ($ProjectName) {
    $vercelArgs += @("--scope", $ProjectName)
}

Write-Host "Setting Vercel preview DATABASE_URL from NEON vercel-dev branch..."
$env:DATABASE_URL_VERCEL_DEV | vercel @vercelArgs

$prodArgs = @("env", "add", "DATABASE_URL", "production", "--force")
if ($ProjectName) {
    $prodArgs += @("--scope", $ProjectName)
}

if ($env:DATABASE_URL) {
    Write-Host "Setting Vercel production DATABASE_URL from local production branch..."
    $env:DATABASE_URL | vercel @prodArgs
}

Write-Host "Done. Verify with: vercel env ls"
