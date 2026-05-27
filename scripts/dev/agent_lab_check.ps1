Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    return $null -ne (Get-Command -Name $CommandName -ErrorAction SilentlyContinue)
}

function Invoke-VersionCheck {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName,
        [Parameter(Mandatory = $true)]
        [string[][]]$ArgumentSets,
        [Parameter(Mandatory = $true)]
        [string]$DisplayName,
        [int]$TimeoutSeconds = 5
    )

    Write-Host "${DisplayName}: FOUND"

    foreach ($argumentSet in $ArgumentSets) {
        $job = $null
        try {
            $job = Start-Job -ScriptBlock {
                param(
                    [string]$JobCommandName,
                    [string[]]$JobArgumentSet
                )

                try {
                    $output = & $JobCommandName @JobArgumentSet 2>&1
                    [pscustomobject]@{
                        Success = ($LASTEXITCODE -eq 0)
                        Output = ((@($output) | ForEach-Object { $_.ToString().Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join " ")
                    }
                } catch {
                    [pscustomobject]@{
                        Success = $false
                        Output = $_.Exception.Message
                    }
                }
            } -ArgumentList $CommandName, $argumentSet

            if (-not (Wait-Job -Job $job -Timeout $TimeoutSeconds)) {
                Stop-Job -Job $job -Force -ErrorAction SilentlyContinue
                Write-Host "${DisplayName}: TIMEOUT ($($argumentSet -join ' '))"
                return
            }

            $result = Receive-Job -Job $job

            if ($result.Success) {
                if ([string]::IsNullOrWhiteSpace($result.Output)) {
                    Write-Host "${DisplayName}: VERSION OK ($($argumentSet -join ' '))"
                } else {
                    Write-Host "${DisplayName}: VERSION OK ($($argumentSet -join ' ')) - $($result.Output)"
                }
                return
            }
        } catch {
            Write-Host "${DisplayName}: VERSION SKIPPED ($($argumentSet -join ' '))"
            return
        } finally {
            if ($null -ne $job) {
                Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
            }
        }
    }

    Write-Host "${DisplayName}: VERSION SKIPPED"
}

$toolChecks = @(
    @{ Command = "opencode"; Display = "OpenCode"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "openclaw"; Display = "OpenClaw"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "9router"; Display = "9Router"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "fcc-claude"; Display = "FCC Claude"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "fcc-server"; Display = "FCC Server"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "anus"; Display = "ANUS"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "rmux"; Display = "rmux"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "codiff"; Display = "codiff"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "md2html"; Display = "md2html"; Args = @(@("--version"), @("version"), @("--help")) },
    @{ Command = "tailscale"; Display = "Tailscale"; Args = @(@("version")) },
    @{ Command = "cargo"; Display = "cargo"; Args = @(@("--version")) },
    @{ Command = "rustc"; Display = "rustc"; Args = @(@("--version")) },
    @{ Command = "node"; Display = "node"; Args = @(@("--version")) },
    @{ Command = "npm"; Display = "npm"; Args = @(@("--version")) },
    @{ Command = "gh"; Display = "GitHub CLI"; Args = @(@("--version")) },
    @{ Command = "git"; Display = "git"; Args = @(@("--version")) },
    @{ Command = "code"; Display = "VS Code CLI"; Args = @(@("--version")) }
)

Write-Host "Checking AI Agent Lab tools with non-interactive version probes..."

foreach ($toolCheck in $toolChecks) {
    if (-not (Test-CommandExists -CommandName $toolCheck.Command)) {
        Write-Host "$($toolCheck.Display): MISSING"
        continue
    }

    Invoke-VersionCheck `
        -CommandName $toolCheck.Command `
        -ArgumentSets $toolCheck.Args `
        -DisplayName $toolCheck.Display `
        -TimeoutSeconds 5
}

Write-Host "Completed non-interactive tool checks. No secrets are printed."
exit 0
