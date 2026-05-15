param(
    [string]$BackendUrl = "http://127.0.0.1:8001",
    [string]$FrontendUrl = "http://127.0.0.1:5173",
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$NoStart
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FrontendRoot = Join-Path $RepoRoot "frontend"
$BackendUriObject = [Uri]$BackendUrl
$FrontendUriObject = [Uri]$FrontendUrl
$StartedProcesses = @()
$FailureCount = 0
$WarnCount = 0
$BackendStatus = if ($SkipBackend) { "SKIPPED" } else { "PENDING" }
$ScannerStatus = if ($SkipBackend) { "SKIPPED" } else { "PENDING" }
$FrontendStatus = if ($SkipFrontend) { "SKIPPED" } else { "PENDING" }

function Write-Check {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Level,
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "[$Level] $Message"
}

function Add-Failure {
    param([Parameter(Mandatory = $true)][string]$Message)

    $script:FailureCount += 1
    Write-Check -Level "FAIL" -Message $Message
}

function Add-Warning {
    param([Parameter(Mandatory = $true)][string]$Message)

    $script:WarnCount += 1
    Write-Check -Level "WARN" -Message $Message
}

function Add-Pass {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Check -Level "PASS" -Message $Message
}

function Start-TrackedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    $process = Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $Command
        ) `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -PassThru

    $script:StartedProcesses += [PSCustomObject]@{
        Name = $Name
        Process = $process
    }

    Add-Pass "Started $Name helper process (PID $($process.Id))"
}

function Stop-TrackedProcesses {
    foreach ($entry in @($script:StartedProcesses | Sort-Object { $_.Process.Id } -Descending)) {
        try {
            if ($null -ne $entry.Process -and -not $entry.Process.HasExited) {
                Stop-Process -Id $entry.Process.Id -Force
                Add-Pass "Stopped $($entry.Name) helper process (PID $($entry.Process.Id))"
            }
        }
        catch {
            Add-Warning "Could not stop $($entry.Name) helper process: $($_.Exception.Message)"
        }
    }
}

function Test-Http200 {
    param([Parameter(Mandatory = $true)][string]$Uri)

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec 5
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Wait-ForHttp200 {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Http200 -Uri $Uri) {
            return $true
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Invoke-JsonGet {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Uri
    )

    $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec 10
    if ($response.StatusCode -ne 200) {
        throw "$Name returned HTTP $($response.StatusCode)"
    }

    return [PSCustomObject]@{
        StatusCode = $response.StatusCode
        Json = $response.Content | ConvertFrom-Json
    }
}

function Get-NestedJsonKeys {
    param([Parameter(Mandatory = $false)]$Value)

    $keys = @()
    if ($null -eq $Value) {
        return $keys
    }

    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($key in $Value.Keys) {
            $keys += [string]$key
            $keys += Get-NestedJsonKeys -Value $Value[$key]
        }
        return $keys
    }

    if (($Value -is [System.Collections.IEnumerable]) -and -not ($Value -is [string])) {
        foreach ($item in $Value) {
            $keys += Get-NestedJsonKeys -Value $item
        }
        return $keys
    }

    foreach ($property in $Value.PSObject.Properties) {
        $keys += [string]$property.Name
        $keys += Get-NestedJsonKeys -Value $property.Value
    }

    return $keys
}

function Ensure-BackendReady {
    $brokersUri = "$($BackendUrl.TrimEnd('/'))/api/brokers"
    if (Test-Http200 -Uri $brokersUri) {
        Add-Pass "Backend is reachable at $brokersUri"
        return $true
    }

    if ($NoStart) {
        Add-Failure "Backend is not reachable at $brokersUri. Start it manually or rerun without -NoStart."
        return $false
    }

    $command = "& { Set-Location '$RepoRoot'; py -3.11 -m uvicorn app.main:app --host '$($BackendUriObject.Host)' --port $($BackendUriObject.Port) }"
    Start-TrackedProcess -Name "backend" -Command $command -WorkingDirectory $RepoRoot

    if (Wait-ForHttp200 -Uri $brokersUri -TimeoutSeconds 45) {
        Add-Pass "Backend started and is reachable at $brokersUri"
        return $true
    }

    Add-Failure "Backend did not become reachable at $brokersUri within 45 seconds."
    return $false
}

function Ensure-FrontendReady {
    $rootUri = "$($FrontendUrl.TrimEnd('/'))/"
    if (Test-Http200 -Uri $rootUri) {
        Add-Pass "Frontend is reachable at $rootUri"
        return $true
    }

    if ($NoStart) {
        Add-Failure "Frontend is not reachable at $rootUri. Start it manually or rerun without -NoStart."
        return $false
    }

    if (-not (Test-Path -LiteralPath (Join-Path $FrontendRoot "node_modules"))) {
        Add-Failure "frontend/node_modules is missing, so the smoke script will not auto-install dependencies. Start the frontend manually after installing dependencies."
        return $false
    }

    $viteApiBase = "$($BackendUrl.TrimEnd('/'))/api"
    $command = "& { `$env:VITE_API_BASE_URL = '$viteApiBase'; Set-Location '$FrontendRoot'; npm run dev -- --host '$($FrontendUriObject.Host)' --port $($FrontendUriObject.Port) --strictPort }"
    Start-TrackedProcess -Name "frontend" -Command $command -WorkingDirectory $FrontendRoot

    if (Wait-ForHttp200 -Uri $rootUri -TimeoutSeconds 45) {
        Add-Pass "Frontend started and is reachable at $rootUri"
        return $true
    }

    Add-Failure "Frontend did not become reachable at $rootUri within 45 seconds."
    return $false
}

function Test-FrontendRoute {
    param([Parameter(Mandatory = $true)][string]$Path)

    $uri = "$($FrontendUrl.TrimEnd('/'))$Path"
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $uri -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Add-Pass "Frontend route $Path returned HTTP 200"
            return $true
        }

        Add-Failure "Frontend route $Path returned HTTP $($response.StatusCode)"
        return $false
    }
    catch {
        Add-Failure "Frontend route $Path failed: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-SafetyCheck {
    Add-Pass "Running local safety configuration validation"
    $output = & py -3.11 scripts/validate_safety_config.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        $joined = ($output | Out-String).Trim()
        Add-Failure "Safety validation exited with code $LASTEXITCODE. $joined"
        return $false
    }

    $joined = ($output | Out-String)
    if ($joined -notmatch "OVERALL:\s+PASS") {
        Add-Failure "Safety validation did not report OVERALL: PASS."
        return $false
    }

    Add-Pass "Safety configuration check reported OVERALL: PASS"
    return $true
}

Push-Location $RepoRoot
try {
    Write-Host "MellyTrade local read-only demo smoke"
    Write-Host "Repo: $RepoRoot"
    Write-Host "BackendUrl: $BackendUrl"
    Write-Host "FrontendUrl: $FrontendUrl"
    Write-Host ""

    [void](Invoke-SafetyCheck)

    if (-not $SkipBackend) {
        if (Ensure-BackendReady) {
            $backendFailuresBefore = $FailureCount
            try {
                $brokers = Invoke-JsonGet -Name "/api/brokers" -Uri "$($BackendUrl.TrimEnd('/'))/api/brokers"
                Add-Pass "/api/brokers returned HTTP $($brokers.StatusCode)"

                $scannerDefault = Invoke-JsonGet -Name "/api/signals/scanner/preview" -Uri "$($BackendUrl.TrimEnd('/'))/api/signals/scanner/preview"
                Add-Pass "/api/signals/scanner/preview returned HTTP $($scannerDefault.StatusCode)"

                $scannerFiltered = Invoke-JsonGet -Name "/api/signals/scanner/preview?symbols=AAPL,NVDA,EURUSD,XAUUSD" -Uri "$($BackendUrl.TrimEnd('/'))/api/signals/scanner/preview?symbols=AAPL,NVDA,EURUSD,XAUUSD"
                Add-Pass "/api/signals/scanner/preview?symbols=AAPL,NVDA,EURUSD,XAUUSD returned HTTP $($scannerFiltered.StatusCode)"

                $payload = $scannerFiltered.Json
                $forbiddenFields = @(
                    "account_id",
                    "order_id",
                    "execution_id",
                    "trade_id",
                    "secret",
                    "token",
                    "api_key",
                    "credential"
                )

                if ($payload.read_only -ne $true) {
                    Add-Failure "Scanner preview read_only must be true."
                }

                if ($payload.execution_mode -ne "dry_run_only") {
                    Add-Failure "Scanner preview execution_mode must be dry_run_only."
                }

                if (-not ($payload.PSObject.Properties.Name -contains "results")) {
                    Add-Failure "Scanner preview response is missing results."
                }
                elseif (@($payload.results).Count -eq 0) {
                    Add-Failure "Scanner preview results must contain at least one item."
                }
                else {
                    Add-Pass "Scanner preview returned a results array"
                }

                $actualSymbols = @($payload.results | ForEach-Object { $_.symbol })
                $expectedSymbols = @("AAPL", "NVDA", "EURUSD", "XAUUSD")
                if (($actualSymbols -join ",") -ne ($expectedSymbols -join ",")) {
                    Add-Failure "Scanner preview symbols were [$($actualSymbols -join ', ')] but expected [$($expectedSymbols -join ', ')]"
                }
                else {
                    Add-Pass "Scanner preview normalized the requested symbols as expected"
                }

                $allKeys = @(Get-NestedJsonKeys -Value $payload | ForEach-Object { $_.ToString().ToLowerInvariant() })
                $foundForbidden = @($forbiddenFields | Where-Object { $allKeys -contains $_ })
                if ($foundForbidden.Count -gt 0) {
                    Add-Failure "Scanner preview exposed forbidden fields: $($foundForbidden -join ', ')"
                }
                else {
                    Add-Pass "Scanner preview response does not expose forbidden fields"
                }

                if ($FailureCount -eq $backendFailuresBefore) {
                    $BackendStatus = "PASS"
                    $ScannerStatus = "PASS"
                }
                else {
                    $BackendStatus = "FAIL"
                    $ScannerStatus = "FAIL"
                }
            }
            catch {
                Add-Failure "Backend GET checks failed: $($_.Exception.Message)"
                $BackendStatus = "FAIL"
                $ScannerStatus = "FAIL"
            }
        }
        else {
            $BackendStatus = "FAIL"
            $ScannerStatus = "FAIL"
        }
    }
    else {
        Add-Warning "Skipping backend checks by request."
    }

    if (-not $SkipFrontend) {
        if (Ensure-FrontendReady) {
            $routesPassed = $true
            foreach ($path in @("/", "/terminal", "/signals", "/brokers", "/portfolio")) {
                if (-not (Test-FrontendRoute -Path $path)) {
                    $routesPassed = $false
                }
            }

            if ($routesPassed) {
                $FrontendStatus = "PASS"
            }
            else {
                $FrontendStatus = "FAIL"
            }
        }
        else {
            $FrontendStatus = "FAIL"
        }
    }
    else {
        Add-Warning "Skipping frontend checks by request."
    }

    Write-Host ""
    Write-Host "Summary"
    Write-Host "backend status: $BackendStatus"
    Write-Host "scanner preview status: $ScannerStatus"
    Write-Host "frontend status: $FrontendStatus"
    Write-Host "safety posture: autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max risk <=1%"

    if ($FailureCount -gt 0) {
        Write-Check -Level "FAIL" -Message "Local read-only demo smoke FAILED"
        exit 1
    }

    if ($WarnCount -gt 0) {
        Write-Check -Level "WARN" -Message "Local read-only demo smoke completed with warnings"
    }

    Write-Check -Level "PASS" -Message "Local read-only demo smoke PASSED"
    exit 0
}
finally {
    Stop-TrackedProcesses
    Pop-Location
}
