Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    return $null -ne (Get-Command -Name $CommandName -ErrorAction SilentlyContinue)
}

function Invoke-CommandCheck {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName,
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,
        [Parameter(Mandatory = $true)]
        [string]$DisplayName,
        [int]$TimeoutSeconds = 5
    )

    if (-not (Test-CommandExists -CommandName $CommandName)) {
        Write-Host "${DisplayName}: MISSING"
        return
    }

    $job = $null
    try {
        $job = Start-Job -ScriptBlock {
            param(
                [string]$JobCommandName,
                [string[]]$JobArgumentList
            )

            try {
                $output = & $JobCommandName @JobArgumentList 2>&1
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
        } -ArgumentList $CommandName, $ArgumentList

        if (-not (Wait-Job -Job $job -Timeout $TimeoutSeconds)) {
            Stop-Job -Job $job -ErrorAction SilentlyContinue
            Write-Host "${DisplayName}: TIMEOUT"
            return
        }

        $result = Receive-Job -Job $job
        if ($result.Success) {
            if ([string]::IsNullOrWhiteSpace($result.Output)) {
                Write-Host "${DisplayName}: OK"
            } else {
                Write-Host "${DisplayName}: OK - $($result.Output)"
            }
            return
        }

        Write-Host "${DisplayName}: WARN - $($result.Output)"
    } finally {
        if ($null -ne $job) {
            Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Checking VS Code workspace tooling..."
Invoke-CommandCheck -CommandName "code" -ArgumentList @("--version") -DisplayName "VS Code CLI"
Invoke-CommandCheck -CommandName "code" -ArgumentList @("--list-extensions") -DisplayName "VS Code Extensions"
Invoke-CommandCheck -CommandName "git" -ArgumentList @("--version") -DisplayName "git"
Invoke-CommandCheck -CommandName "gh" -ArgumentList @("--version") -DisplayName "GitHub CLI"
Invoke-CommandCheck -CommandName "node" -ArgumentList @("--version") -DisplayName "node"
Invoke-CommandCheck -CommandName "npm" -ArgumentList @("--version") -DisplayName "npm"
Invoke-CommandCheck -CommandName "py" -ArgumentList @("-3.11", "--version") -DisplayName "Python 3.11"
Invoke-CommandCheck -CommandName "git" -ArgumentList @("status", "--short") -DisplayName "Repository Status"
Invoke-CommandCheck -CommandName "git" -ArgumentList @("branch", "--show-current") -DisplayName "Current Branch"

if (Test-Path -LiteralPath ".vscode\settings.json") {
    Write-Host ".vscode/settings.json: FOUND"
} else {
    Write-Host ".vscode/settings.json: MISSING"
}

if (Test-Path -LiteralPath ".vscode\extensions.json") {
    Write-Host ".vscode/extensions.json: FOUND"
} else {
    Write-Host ".vscode/extensions.json: MISSING"
}

Write-Host "Completed VS Code workspace tooling checks. No secrets are printed."
exit 0
