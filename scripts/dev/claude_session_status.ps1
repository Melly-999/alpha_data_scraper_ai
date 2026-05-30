<#
.SYNOPSIS
    Read-only status overview for parallel Claude Code sessions.

.DESCRIPTION
    Prints the current worktree path, branch, working-tree status, the full
    worktree list, open PRs, and key PR check rollups (if the GitHub CLI `gh`
    is available). Strictly READ-ONLY:
      - does not modify files,
      - does not rerun checks,
      - skips gracefully if `gh` is unavailable or a PR does not exist.

    MellyTrade safety posture is unaffected by this dev-tooling script.

.EXAMPLE
    .\scripts\dev\claude_session_status.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

function Section($title) {
    Write-Host ""
    Write-Host "=== $title ===" -ForegroundColor Cyan
}

Section "Current path"
Write-Host (Get-Location).Path

Section "Git branch"
& git -C $RepoRoot rev-parse --abbrev-ref HEAD 2>&1 | ForEach-Object { Write-Host $_ }

Section "git status --short"
$st = & git -C $RepoRoot status --short 2>&1
if ([string]::IsNullOrWhiteSpace(($st | Out-String))) { Write-Host "(clean)" } else { $st | ForEach-Object { Write-Host $_ } }

Section "git worktree list"
& git -C $RepoRoot worktree list 2>&1 | ForEach-Object { Write-Host $_ }

# --- GitHub CLI section (optional) ---
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Section "GitHub PRs"
    Write-Host "gh CLI not found on PATH -> skipping PR status." -ForegroundColor Yellow
    Write-Host "Install GitHub CLI (https://cli.github.com) and run 'gh auth login' to enable PR status."
    return
}

Section "Open PRs (gh pr list)"
& gh pr list --state open --limit 30 2>&1 | ForEach-Object { Write-Host $_ }

Section "Key PR checks (read-only)"
$keyPrs = @(230, 231, 233, 234, 235, 236, 237)
foreach ($pr in $keyPrs) {
    # Confirm the PR exists before asking for checks; skip gracefully otherwise.
    $null = & gh pr view $pr --json number 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host ("PR #{0}: not found -> skipping." -f $pr) -ForegroundColor DarkGray
        continue
    }
    Write-Host ("--- PR #{0} ---" -f $pr) -ForegroundColor White
    & gh pr checks $pr 2>&1 | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "Read-only status complete. No files changed, no checks rerun." -ForegroundColor Green
