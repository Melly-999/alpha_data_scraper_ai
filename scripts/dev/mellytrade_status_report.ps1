param(
    [string]$RepoPath = "C:/AI/MellyTrade_Workspace/02_Repo/alpha_data_scraper_ai",
    [string]$OutputPath = "",
    [switch]$RunSafetyValidation,
    [switch]$IncludePrChecks,
    [int]$PrLimit = 20
)

$ErrorActionPreference = "Stop"

$denyPatterns = @(
    '\bgit\s+add\b',
    '\bgit\s+commit\b',
    '\bgit\s+push\b',
    '\bgit\s+reset\b',
    '\bgit\s+clean\b',
    '\bgit\s+checkout\b',
    '\bgit\s+switch\b',
    '\bgit\s+branch\s+-D\b',
    '\bgit\s+worktree\s+remove\b',
    '\bgh\s+pr\s+merge\b',
    '\bgh\s+pr\s+close\b',
    '\bgh\s+pr\s+ready\b',
    '\bgh\s+pr\s+edit\b',
    '\bgh\s+workflow\s+run\b',
    '\bgh\s+secret\b',
    '\bsecret\s+list\b',
    '\bsecret\s+set\b'
)

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Command
    )

    $commandLine = ($Command -join " ").ToLowerInvariant()
    foreach ($pattern in $denyPatterns) {
        if ($commandLine -match $pattern) {
            throw "Forbidden command detected by denylist: $commandLine"
        }
    }

    $args = @()
    if ($Command.Count -gt 1) {
        $args = $Command[1..($Command.Count - 1)]
    }

    $output = & $Command[0] @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw [System.Exception]::new(($output | Out-String).Trim())
    }

    return $output
}

function Format-MarkdownTable {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Header,
        [Parameter(Mandatory = $true)]
        [object[]]$Rows
    )

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add(("| " + ($Header -join " | ") + " |"))
    $lines.Add(("|" + (($Header | ForEach-Object { "---" }) -join "|") + "|"))

    foreach ($row in $Rows) {
        $lines.Add(("| " + ($row -join " | ") + " |"))
    }

    return $lines.ToArray()
}

if (-not (Test-Path -LiteralPath $RepoPath)) {
    throw "Repository path not found: $RepoPath"
}

Set-Location -LiteralPath $RepoPath

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
$branch = $null
$sha = $null
$gitStatus = @()
$recentCommits = @()
$worktrees = @()
$openPrs = @()
$prChecksText = @()
$safetyValidationText = @()
$ghAvailable = [bool](Get-Command gh -ErrorAction SilentlyContinue)

try { $branch = (Invoke-ReadOnlyCommand @("git", "branch", "--show-current") | Out-String).Trim() } catch { $branch = "(unknown)" }
try { $sha = (Invoke-ReadOnlyCommand @("git", "rev-parse", "HEAD") | Out-String).Trim() } catch { $sha = "(unknown)" }
try {
    $originalHome = $env:HOME
    $originalXdg = $env:XDG_CONFIG_HOME
    $env:HOME = $RepoPath
    $env:XDG_CONFIG_HOME = $RepoPath
    $gitStatus = @(Invoke-ReadOnlyCommand @("git", "status", "--short"))
} catch {
    $gitStatus = @("ERROR: $($_.Exception.Message)")
} finally {
    $env:HOME = $originalHome
    $env:XDG_CONFIG_HOME = $originalXdg
}
try { $recentCommits = @(Invoke-ReadOnlyCommand @("git", "log", "--oneline", "-n", "5")) } catch { $recentCommits = @("ERROR: $($_.Exception.Message)") }
try { $worktrees = @(Invoke-ReadOnlyCommand @("git", "worktree", "list")) } catch { $worktrees = @("ERROR: $($_.Exception.Message)") }

if ($ghAvailable) {
    try {
        $openPrs = @(Invoke-ReadOnlyCommand @(
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "$PrLimit",
            "--json",
            "number,title,state,isDraft,headRefName,baseRefName,mergeStateStatus,updatedAt"
        ) | ConvertFrom-Json)
    } catch {
        $openPrs = @()
        $prChecksText = @("GH PR list unavailable: $($_.Exception.Message)")
    }
} else {
    $prChecksText = @("gh CLI unavailable; PR checks skipped.")
}

$dirtyCount = @($gitStatus | Where-Object { $_.Trim() -ne "" }).Count
$dirtySummary = if ($dirtyCount -eq 0) { "clean" } else { "dirty ($dirtyCount entries)" }
$safetyReminder = "autotrade=false; dry_run=true; read_only=true; live_orders_blocked=true; execution_enabled=false; max risk <=1%"

$report = New-Object System.Collections.Generic.List[string]
$report.Add("# MellyTrade Local Status Report")
$report.Add("")
$report.Add("## Summary")
$report.Add("- repo path: $RepoPath")
$report.Add("- branch: $branch")
$report.Add("- SHA: $sha")
$report.Add("- timestamp: $timestamp")
$report.Add("- dirty state summary: $dirtySummary")
$report.Add("- safety posture reminder: $safetyReminder")
$report.Add("")
$report.Add("## Git Status")
if ($gitStatus.Count -eq 0) {
    $report.Add("- clean")
} else {
    foreach ($line in $gitStatus) {
        $report.Add("- $line")
    }
}
$report.Add("- classification: $dirtySummary")
$report.Add("")
$report.Add("## Recent Commits")
if ($recentCommits.Count -eq 0) {
    $report.Add("- no commits returned")
} else {
    foreach ($line in $recentCommits) {
        $report.Add("- $line")
    }
}
$report.Add("")
$report.Add("## Worktrees")
if ($worktrees.Count -eq 0) {
    $report.Add("- no worktrees returned")
} else {
    foreach ($line in $worktrees) {
        $report.Add("- $line")
    }
}
$report.Add("")
$report.Add("## Open PRs")
if (-not $ghAvailable) {
    $report.Add("- gh CLI unavailable; PR list skipped.")
} elseif ($openPrs.Count -eq 0) {
    $report.Add("- no open PRs found.")
} else {
    $rows = foreach ($pr in $openPrs) {
        @(
            "#$($pr.number)",
            $pr.title,
            $(if ($pr.isDraft) { "Yes" } else { "No" }),
            $pr.mergeStateStatus,
            $pr.headRefName,
            $pr.updatedAt
        )
    }
    foreach ($tableLine in (Format-MarkdownTable -Header @("PR", "Title", "Draft", "Merge State", "Branch", "Updated") -Rows $rows)) {
        $report.Add($tableLine)
    }
}
$report.Add("")

if ($IncludePrChecks) {
    $report.Add("## PR Checks")
    if (-not $ghAvailable) {
        $report.Add("- gh CLI unavailable; checks skipped.")
    } elseif ($openPrs.Count -eq 0) {
        $report.Add("- no open PRs found.")
    } else {
        foreach ($pr in $openPrs) {
            $report.Add("")
            $report.Add("### PR #$($pr.number) - $($pr.title)")
            try {
                $checks = @(Invoke-ReadOnlyCommand @("gh", "pr", "checks", "$($pr.number)"))
                if ($checks.Count -eq 0) {
                    $report.Add("- no checks reported")
                } else {
                    foreach ($line in $checks) {
                        $report.Add("- $line")
                    }
                }
            } catch {
                $report.Add("- checks unavailable: $($_.Exception.Message)")
            }
        }
    }
    $report.Add("")
}

if ($RunSafetyValidation) {
    $report.Add("## Safety Validation")
    try {
        $safetyValidationText = @(Invoke-ReadOnlyCommand @("py", "-3.11", "scripts/validate_safety_config.py"))
        if ($safetyValidationText.Count -eq 0) {
            $report.Add("- safety validation completed with no console output")
        } else {
            foreach ($line in $safetyValidationText) {
                $report.Add("- $line")
            }
        }
    } catch {
        $report.Add("- safety validation failed: $($_.Exception.Message)")
    }
    $report.Add("")
}

$report.Add("## Risk Flags")
$riskRows = New-Object System.Collections.Generic.List[object]

foreach ($entry in $gitStatus) {
    if ($entry -match '^\s*([AM\?\!]{1,2})\s+(.+)$') {
        $path = $Matches[2]
        $severity = "LOW"
        $reason = "Tracked or untracked file changed."
        $action = "Review the diff and keep the change scope minimal."

        if ($path -match '(^|/|\\)(config\.json|requirements[^/\\]*|Dockerfile[^/\\]*|package-lock\.json|yarn\.lock|pnpm-lock\.yaml)$') {
            $severity = "HIGH"
            $reason = "Config, dependency, or Dockerfile change detected."
            $action = "Verify this file is expected and safety-compliant."
        } elseif ($path -match '(^|/|\\)(app|frontend|brokers|mellytrade_v3)(/|\\)') {
            $severity = "HIGH"
            $reason = "Runtime application path changed."
            $action = "Confirm this is not part of a runtime or trading change."
        } elseif ($path -match '\.env(\..+)?$' -or $path -match 'secrets?[/\\]' -or $path -match 'credentials?[/\\]') {
            $severity = "BLOCKER"
            $reason = "Potential secret-bearing file detected."
            $action = "Remove secrets from the diff immediately."
        } elseif ($path -match '\.(exe|dll|so|dylib|zip|7z|tar|gz|png|jpg|jpeg|gif)$') {
            $severity = "MEDIUM"
            $reason = "Generated binary or asset change detected."
            $action = "Verify the artifact is intentional."
        } elseif ($path -match '(^|/|\\)\.github/workflows(/|\\)') {
            $severity = "HIGH"
            $reason = "Workflow change detected."
            $action = "Confirm CI behavior remains read-only and safe."
        }

        if ($path -match '(?i)old|current_pr_stack|agent_mcp_roadmap') {
            $reason = "Roadmap or status-tracking file changed."
        }

        if ($path -match '(\.env|PRIVATE KEY|API_KEY|CLAUDE_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|MT5_LOGIN|MT5_PASSWORD|IBKR_ACCOUNT_ID|broker_order_id|account_id|autotrade=true|dry_run=false|read_only=false|live_orders_blocked=false|execution_enabled=true|place_order|execute_order|buy|sell|execute|order)') {
            $severity = "BLOCKER"
            $reason = "Sensitive or execution-enabling string detected."
            $action = "Remove or neutralize the unsafe string."
        }

        $riskRows.Add(@($path, $severity, $reason, $action))
    }
}

if ($riskRows.Count -eq 0) {
    $report.Add("- no risk flags detected from git status entries.")
} else {
    foreach ($tableLine in (Format-MarkdownTable -Header @("Finding", "Severity", "Reason", "Suggested Action") -Rows $riskRows)) {
        $report.Add($tableLine)
    }
}
$report.Add("")
$report.Add("## Next Recommended Action")
$report.Add("- If AGENT-MCP-003 is not merged, finish AGENT-MCP-003.")
$report.Add("- After this task, recommend AGENT-MCP-004 PR/checks board generator.")
$report.Add("")
$report.Add("## Safety Confirmation")
$report.Add("- no repo mutation performed")
$report.Add("- no git write command executed")
$report.Add("- no GitHub PR mutation executed")
$report.Add("- no secret access attempted")
$report.Add("- no broker credentials accessed")
$report.Add("- no live trading enabled")
$report.Add("- safety posture unchanged")

$reportText = ($report -join [Environment]::NewLine)

if ($OutputPath -and $OutputPath.Trim()) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir -and -not (Test-Path -LiteralPath $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    Set-Content -LiteralPath $OutputPath -Value $reportText -Encoding UTF8
}

$reportText
