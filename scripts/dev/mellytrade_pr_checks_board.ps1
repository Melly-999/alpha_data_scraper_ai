param(
    [int]$PrLimit = 30,
    [switch]$IncludeFiles,
    [switch]$IncludeChecks,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

# Read-only enforcement: any command matching these is refused before execution.
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
    '\bgh\s+secret\b'
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

    $rest = @()
    if ($Command.Count -gt 1) {
        $rest = $Command[1..($Command.Count - 1)]
    }

    $output = & $Command[0] @rest 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw [System.Exception]::new(($output | Out-String).Trim())
    }

    return $output
}

function Format-MarkdownTable {
    param(
        [Parameter(Mandatory = $true)][string[]]$Header,
        [Parameter(Mandatory = $true)][object[]]$Rows
    )
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add(("| " + ($Header -join " | ") + " |"))
    $lines.Add(("|" + (($Header | ForEach-Object { "---" }) -join "|") + "|"))
    foreach ($row in $Rows) {
        $lines.Add(("| " + ($row -join " | ") + " |"))
    }
    return $lines.ToArray()
}

function Get-RiskForFiles {
    param([string[]]$Files)

    if (-not $Files -or $Files.Count -eq 0) {
        return @{ Risk = "LOW"; Action = "review/merge gate (no files detected)" }
    }

    $risk = "LOW"
    foreach ($f in $Files) {
        if ($f -match '(?i)(\.env(\..+)?$|(^|/)secrets?/|(^|/)credentials?/|\.key$|\.pem$|\.p12$|\.pfx$)') {
            return @{ Risk = "BLOCKER"; Action = "do not merge; needs safety review (possible secret-bearing path)" }
        }
    }
    foreach ($f in $Files) {
        if ($f -match '(?i)((^|/)config\.json$|(^|/)requirements[^/]*\.txt$|(^|/)\.github/workflows/|(^|/)Dockerfile|(^|/)docker-compose|(^|/)brokers/|(^|/)risk/|mt5|ibkr|xtb|(^|/)app/|mellytrade-api/app/)') {
            $risk = "HIGH"
        }
    }
    if ($risk -eq "LOW") {
        foreach ($f in $Files) {
            if ($f -match '(?i)(frontend/src/|\.tsx$|\.ts$|\.css$|(^|/)tests?/)') {
                $risk = "MEDIUM"
            }
        }
    }

    switch ($risk) {
        "HIGH"   { return @{ Risk = "HIGH";   Action = "needs safety review; do not merge wholesale" } }
        "MEDIUM" { return @{ Risk = "MEDIUM"; Action = "review/merge gate" } }
        default  { return @{ Risk = "LOW";    Action = "review/merge gate (low risk)" } }
    }
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
$ghAvailable = [bool](Get-Command gh -ErrorAction SilentlyContinue)

$mainSha = "(unknown)"
try { $mainSha = (Invoke-ReadOnlyCommand @("git", "rev-parse", "HEAD") | Out-String).Trim() } catch { $mainSha = "(unknown)" }

$openPrs = @()
$ghError = $null
if ($ghAvailable) {
    try {
        $listRaw = Invoke-ReadOnlyCommand @(
            "gh", "pr", "list", "--state", "open", "--limit", "$PrLimit",
            "--json", "number,title,isDraft,mergeStateStatus,headRefName,baseRefName"
        )
        $listText = ($listRaw | Out-String)
        $openPrs = @(($listText | ConvertFrom-Json))
    } catch {
        $ghError = $_.Exception.Message
        $openPrs = @()
    }
}

$report = New-Object System.Collections.Generic.List[string]
$report.Add("# MellyTrade PR Checks Board")
$report.Add("")
$report.Add("## Summary")
$report.Add("- timestamp: $timestamp")
$report.Add("- repo: Melly-999/alpha_data_scraper_ai")
$report.Add("- current SHA: $mainSha")

$highCount = 0
$prRows = New-Object System.Collections.Generic.List[object]
$filesSections = New-Object System.Collections.Generic.List[string]
$checksSections = New-Object System.Collections.Generic.List[string]

if (-not $ghAvailable) {
    $report.Add("- gh CLI unavailable; PR board skipped (degraded).")
} elseif ($ghError) {
    $report.Add("- gh PR list unavailable: $ghError (degraded).")
} else {
    $report.Add("- open PR count: $($openPrs.Count)")

    foreach ($pr in $openPrs) {
        $files = @()
        try {
            $detail = Invoke-ReadOnlyCommand @("gh", "pr", "view", "$($pr.number)", "--json", "files") | ConvertFrom-Json
            $files = @($detail.files | ForEach-Object { $_.path })
        } catch {
            $files = @()
        }

        $riskInfo = Get-RiskForFiles -Files $files
        if ($riskInfo.Risk -eq "HIGH" -or $riskInfo.Risk -eq "BLOCKER") { $highCount++ }

        $checksSummary = "-"
        if ($IncludeChecks) {
            try {
                $checks = @(Invoke-ReadOnlyCommand @("gh", "pr", "checks", "$($pr.number)"))
                $passCount = @($checks | Where-Object { $_ -match '(?i)\bpass\b' }).Count
                $failCount = @($checks | Where-Object { $_ -match '(?i)\bfail\b' }).Count
                $checksSummary = "$passCount pass / $failCount fail"
                $checksSections.Add("### PR #$($pr.number) checks")
                foreach ($c in $checks) { $checksSections.Add("- $c") }
                $checksSections.Add("")
            } catch {
                $checksSummary = "unavailable"
            }
        }

        if ($IncludeFiles) {
            $filesSections.Add("### PR #$($pr.number) files")
            if ($files.Count -eq 0) { $filesSections.Add("- (no files / unavailable)") }
            foreach ($f in $files) { $filesSections.Add("- $f") }
            $filesSections.Add("")
        }

        $prRows.Add(@(
            "#$($pr.number)",
            $pr.title,
            $(if ($pr.isDraft) { "Yes" } else { "No" }),
            $pr.mergeStateStatus,
            $checksSummary,
            $riskInfo.Risk,
            $riskInfo.Action
        ))
    }
    $report.Add("- high-risk PR count: $highCount")
}

$report.Add("")
$report.Add("## PR Board")
if ($prRows.Count -eq 0) {
    $report.Add("- no open PRs (or gh unavailable).")
} else {
    foreach ($line in (Format-MarkdownTable -Header @("PR", "Title", "Draft", "Merge State", "Checks", "Risk", "Recommended Action") -Rows $prRows)) {
        $report.Add($line)
    }
}
$report.Add("")

if ($IncludeChecks -and $checksSections.Count -gt 0) {
    $report.Add("## PR Checks Detail")
    foreach ($line in $checksSections) { $report.Add($line) }
}

if ($IncludeFiles -and $filesSections.Count -gt 0) {
    $report.Add("## PR Files Detail")
    foreach ($line in $filesSections) { $report.Add($line) }
}

$report.Add("## Old PR Watchlist")
$watchlist = @(18, 17, 12, 10, 7)
if (-not $ghAvailable) {
    $report.Add("- gh CLI unavailable; watchlist state skipped.")
} else {
    foreach ($n in $watchlist) {
        try {
            $w = Invoke-ReadOnlyCommand @("gh", "pr", "view", "$n", "--json", "number,state,isDraft,title") | ConvertFrom-Json
            $report.Add("- #$($w.number) [$($w.state)] draft=$($w.isDraft) - $($w.title)")
        } catch {
            $report.Add("- #$n - state unavailable")
        }
    }
}
$report.Add("")

$report.Add("## Safety Confirmation")
$report.Add("- no PR mutation performed")
$report.Add("- no secret access attempted")
$report.Add("- read-only commands only")

$reportText = ($report -join [Environment]::NewLine)

if ($OutputPath -and $OutputPath.Trim()) {
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir -and -not (Test-Path -LiteralPath $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    Set-Content -LiteralPath $OutputPath -Value $reportText -Encoding UTF8
}

$reportText
