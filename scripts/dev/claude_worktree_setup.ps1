<#
.SYNOPSIS
    Safely create the recommended git worktrees for parallel Claude Code sessions.

.DESCRIPTION
    Non-destructive. Each recommended worktree = one branch = one Claude Code
    session. The script:
      - SKIPS (with a warning) any worktree path that already exists.
      - NEVER deletes, merges, pushes, or marks anything ready.
      - NEVER checks out over a dirty/existing worktree.
      - Uses `git worktree add`, basing new branches on origin/main unless the
        branch already exists (in which case it attaches to the existing branch).

    MellyTrade safety posture is unaffected by this dev-tooling script:
      autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true,
      execution_enabled=false, max_risk_per_trade <= 1%.

.PARAMETER DryRun
    Print the git commands that WOULD run, without executing them.

.EXAMPLE
    .\scripts\dev\claude_worktree_setup.ps1 -DryRun
.EXAMPLE
    .\scripts\dev\claude_worktree_setup.ps1
#>

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Repo root = two levels up from this script (scripts/dev/<file>).
$RepoRoot   = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ParentDir  = (Resolve-Path (Join-Path $RepoRoot "..")).Path

Write-Host "MellyTrade parallel-session worktree setup" -ForegroundColor Cyan
Write-Host "Repo root : $RepoRoot"
Write-Host "Parent dir: $ParentDir"
if ($DryRun) { Write-Host "MODE      : DRY-RUN (no changes will be made)" -ForegroundColor Yellow }
Write-Host ""

function Invoke-Git {
    param([string[]]$GitArgs)
    if ($DryRun) {
        Write-Host "DRY-RUN > git $($GitArgs -join ' ')" -ForegroundColor DarkGray
        return ""
    }
    return (& git -C $RepoRoot @GitArgs 2>&1)
}

function Test-LocalBranch {
    param([string]$Branch)
    $null = & git -C $RepoRoot rev-parse --verify --quiet "refs/heads/$Branch" 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Add-Worktree {
    param(
        [string]$Path,
        [string]$Branch,
        [string]$Base,        # used only when creating a NEW branch
        [string]$Comment
    )

    Write-Host "----------------------------------------------------------------"
    Write-Host "Worktree : $Path"
    Write-Host "Branch   : $Branch"
    Write-Host "Purpose  : $Comment"

    if (Test-Path $Path) {
        Write-Warning "Path already exists -> SKIPPING (non-destructive). No checkout performed."
        return
    }

    if (Test-LocalBranch -Branch $Branch) {
        # Attach a worktree to the EXISTING branch (do not re-create or reset it).
        Write-Host "Branch exists locally -> attaching existing branch to new worktree."
        Invoke-Git @("worktree", "add", $Path, $Branch) | ForEach-Object { Write-Host $_ }
    }
    else {
        Write-Host "Branch not found locally -> creating from base '$Base'."
        # Fetch is read-only and safe; only refresh remotes, never reset.
        Invoke-Git @("fetch", "origin", "--quiet") | Out-Null
        Invoke-Git @("worktree", "add", "-b", $Branch, $Path, $Base) | ForEach-Object { Write-Host $_ }
    }
}

# ---------------------------------------------------------------------------
# 1. Lead / PR Monitor — read-only branch for tracking PRs and checks.
# ---------------------------------------------------------------------------
Add-Worktree `
    -Path    (Join-Path $ParentDir "alpha_data_scraper_ai-lead-monitor") `
    -Branch  "devx/lead-monitor-readonly" `
    -Base    "origin/main" `
    -Comment "Read-only Lead/PR Monitor session (no edits, no commits)."

# ---------------------------------------------------------------------------
# 2. Quality Stack — black/flake8/mypy work.
#    Prefer the existing TYPE-001A branch. If absent, create it from LINT-001
#    (chore/lint-001-fix-flake8). If LINT-001 is also missing, STOP and report.
# ---------------------------------------------------------------------------
$qualityPath   = Join-Path $ParentDir "alpha_data_scraper_ai-quality-stack"
$qualityBranch = "chore/type-001a-mypy-gate-unblock"
$lintBase      = "chore/lint-001-fix-flake8"

Write-Host "----------------------------------------------------------------"
Write-Host "Worktree : $qualityPath"
Write-Host "Branch   : $qualityBranch"
Write-Host "Purpose  : Quality stack (black/flake8/mypy) session."

if (Test-Path $qualityPath) {
    Write-Warning "Path already exists -> SKIPPING (non-destructive)."
}
elseif (Test-LocalBranch -Branch $qualityBranch) {
    Write-Host "TYPE-001A branch exists -> attaching existing branch."
    Invoke-Git @("worktree", "add", $qualityPath, $qualityBranch) | ForEach-Object { Write-Host $_ }
}
elseif (Test-LocalBranch -Branch $lintBase) {
    Write-Host "TYPE-001A absent; creating from '$lintBase'."
    Invoke-Git @("worktree", "add", "-b", $qualityBranch, $qualityPath, $lintBase) | ForEach-Object { Write-Host $_ }
}
else {
    Write-Warning "STOP: neither '$qualityBranch' nor base '$lintBase' exists locally."
    Write-Warning "Cannot safely create the quality-stack worktree. Resolve LINT-001 first, then re-run."
}

# ---------------------------------------------------------------------------
# 3. Security Dependency Monitor — dependency-audit work (requirements only).
# ---------------------------------------------------------------------------
Add-Worktree `
    -Path    (Join-Path $ParentDir "alpha_data_scraper_ai-security-deps") `
    -Branch  "chore/sec-deps-monitor" `
    -Base    "origin/main" `
    -Comment "Security dependency monitor (pip-audit/pip check; requirements only when approved)."

# ---------------------------------------------------------------------------
# 4. UI Review — read-only review of the Open Design frontend PR.
# ---------------------------------------------------------------------------
Add-Worktree `
    -Path    (Join-Path $ParentDir "alpha_data_scraper_ai-ui-review") `
    -Branch  "review/ui-open-design-readonly" `
    -Base    "origin/main" `
    -Comment "Read-only UI review session for the Open Design terminal tabs PR."

Write-Host ""
Write-Host "Done. Run '.\scripts\dev\claude_session_status.ps1' to view state." -ForegroundColor Green
Write-Host "Reminder: one session per worktree; only one committer at a time; no merges without approval." -ForegroundColor Yellow
