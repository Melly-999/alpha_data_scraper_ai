<#
.SYNOPSIS
    Read-only cleanup PLANNER for MellyTrade git worktrees.

.DESCRIPTION
    Prints the current worktree list and, by NAME ONLY, flags likely-stale
    worktrees. It NEVER deletes, prunes, merges, or modifies anything. Suggested
    cleanup commands are printed as COMMENTS for a human to run manually, and
    only AFTER the corresponding PRs have merged.

    MellyTrade safety posture is unaffected by this dev-tooling script.

.EXAMPLE
    .\scripts\dev\claude_worktree_cleanup_plan.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "MellyTrade worktree cleanup PLAN (read-only; nothing will be deleted)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== git worktree list ===" -ForegroundColor Cyan
$raw = & git -C $RepoRoot worktree list 2>&1
$raw | ForEach-Object { Write-Host $_ }

# Name-only heuristics for likely-stale worktrees. These are HINTS only.
$stalePatterns = @(
    "observability-connectors-v2",  # empty/superseded duplicate observed previously
    "postmerge-",                   # post-merge scratch checkouts
    "smoke",                        # transient smoke-test checkouts
    "patch2",                       # ad-hoc patch checkouts
    "salvage"                       # salvage/temporary work
)

Write-Host ""
Write-Host "=== Likely-stale candidates (by name only) ===" -ForegroundColor Yellow
$lines = $raw | Where-Object { $_ -is [string] }
$flagged = @()
foreach ($line in $lines) {
    foreach ($pat in $stalePatterns) {
        if ($line -match [regex]::Escape($pat)) {
            Write-Host "  CANDIDATE: $line"
            $path = ($line -split "\s+")[0]
            $flagged += $path
            break
        }
    }
}
if ($flagged.Count -eq 0) {
    Write-Host "  (no name-based stale candidates found)"
}

Write-Host ""
Write-Host "=== Suggested MANUAL cleanup (commented; DO NOT auto-run) ===" -ForegroundColor Yellow
Write-Host "# WARNING: only run these AFTER the related PRs have merged and you have"
Write-Host "# confirmed each worktree has no unpushed commits or uncommitted changes."
Write-Host "#"
foreach ($p in $flagged) {
    Write-Host "# git worktree remove `"$p`""
}
Write-Host "# git worktree prune    # removes administrative records for deleted dirs"
Write-Host "#"
Write-Host "# Active sprint worktrees (KEEP until their PRs merge):"
Write-Host "#   alpha_data_scraper_ai-format-001            (PR #234)"
Write-Host "#   alpha_data_scraper_ai-sec-req-002c-...      (PR #233)"
Write-Host "#   alpha_data_scraper_ai-sec-req-004           (PR #236)"
Write-Host "#   alpha_data_scraper_ai-observability-...     (PR #231)"
Write-Host "#   alpha_data_scraper_ai-devx-parallel         (this PR)"

Write-Host ""
Write-Host "Plan only. No worktree was removed or pruned." -ForegroundColor Green
