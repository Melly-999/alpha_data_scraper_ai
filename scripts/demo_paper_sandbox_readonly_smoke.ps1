param(
    [string]$BackendBaseUrl = "http://127.0.0.1:8001",
    [string]$FrontendBaseUrl = "http://127.0.0.1:5173",
    [switch]$SkipFrontend
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PassCount = 0
$FailCount = 0

function Write-Result {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("PASS", "FAIL", "INFO", "WARN")][string]$Level,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Detail = ""
    )

    switch ($Level) {
        "PASS" { $script:PassCount++; $tag = "[PASS]" }
        "FAIL" { $script:FailCount++; $tag = "[FAIL]" }
        "INFO" { $tag = "[INFO]" }
        "WARN" { $tag = "[WARN]" }
    }

    $line = "$tag $Name"
    if ($Detail) {
        $line += "  ($Detail)"
    }
    Write-Host $line
}

function Invoke-JsonGet {
    param(
        [Parameter(Mandatory = $true)][string]$Uri
    )

    $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -ne 200) {
        throw "HTTP $($response.StatusCode) $($response.StatusDescription)"
    }

    return $response.Content | ConvertFrom-Json
}

function Get-Payload {
    param(
        [Parameter(Mandatory = $true)]$Body,
        [Parameter(Mandatory = $true)][string]$PreferredProperty
    )

    if ($null -ne $Body.PSObject.Properties[$PreferredProperty]) {
        return $Body.$PreferredProperty
    }

    return $Body
}

function Test-SafetyField {
    param(
        [Parameter(Mandatory = $true)]$Body,
        [Parameter(Mandatory = $true)][string]$Field,
        [Parameter(Mandatory = $true)]$ExpectedValue,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($null -eq $Body.PSObject.Properties[$Field]) {
        Write-Result -Level INFO -Name "$Label $Field unavailable"
        return
    }

    $actual = $Body.$Field
    if ($actual -eq $ExpectedValue) {
        Write-Result -Level PASS -Name "$Label $Field=$ExpectedValue"
    } else {
        Write-Result -Level FAIL -Name "$Label $Field" -Detail "got: $actual"
    }
}

function Test-MaxRisk {
    param(
        [Parameter(Mandatory = $true)]$Body,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if ($null -eq $Body.PSObject.Properties["max_risk_per_trade"]) {
        Write-Result -Level INFO -Name "$Label max_risk_per_trade unavailable"
        return
    }

    $actual = [double]$Body.max_risk_per_trade
    if ($actual -le 1.0) {
        Write-Result -Level PASS -Name "$Label max_risk_per_trade<=1.0" -Detail "$actual"
    } else {
        Write-Result -Level FAIL -Name "$Label max_risk_per_trade" -Detail "got: $actual"
    }
}

function Test-OptionalFrontendRoute {
    param([Parameter(Mandatory = $true)][string]$Path)

    $uri = "$($FrontendBaseUrl.TrimEnd('/'))$Path"
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $uri -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Result -Level PASS -Name "Frontend $Path returned HTTP 200"
            return $true
        }

        Write-Result -Level FAIL -Name "Frontend $Path returned HTTP $($response.StatusCode)"
        return $false
    } catch {
        Write-Result -Level FAIL -Name "Frontend $Path failed" -Detail $_.Exception.Message
        return $false
    }
}

Write-Host ""
Write-Host "MellyTrade PAPER-003 read-only smoke"
Write-Host "GET-only demo validation for paper sandbox preview + audit rail"
Write-Host "Backend:  $BackendBaseUrl"
Write-Host "Frontend: $FrontendBaseUrl"
Write-Host ""

# ---------------------------------------------------------------------------
# Health: probe both documented variants and accept either.
# ---------------------------------------------------------------------------
$healthCandidates = @(
    "$($BackendBaseUrl.TrimEnd('/'))/api/health",
    "$($BackendBaseUrl.TrimEnd('/'))/health"
)

$healthBody = $null
$healthUri = $null
foreach ($candidate in $healthCandidates) {
    try {
        $healthBody = Invoke-JsonGet -Uri $candidate
        $healthUri = $candidate
        break
    } catch {
        continue
    }
}

if ($null -eq $healthBody) {
    Write-Result -Level FAIL -Name "Backend health unreachable"
    Write-Host "Start the backend, then re-run:"
    Write-Host "  py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
    Write-Host "Or:"
    Write-Host "  .\scripts\start_backend.ps1"
    exit 1
}

Write-Result -Level PASS -Name "Backend health reachable" -Detail $healthUri

if ($healthBody.status -eq "ok") {
    Write-Result -Level PASS -Name "Health status=ok"
} else {
    Write-Result -Level FAIL -Name "Health status" -Detail "got: $($healthBody.status)"
}

if ($healthBody.safety) {
    Test-SafetyField -Body $healthBody.safety -Field "auto_trade" -ExpectedValue $false -Label "health.safety"
    Test-SafetyField -Body $healthBody.safety -Field "dry_run" -ExpectedValue $true -Label "health.safety"
    Test-SafetyField -Body $healthBody.safety -Field "read_only" -ExpectedValue $true -Label "health.safety"
    Test-SafetyField -Body $healthBody.safety -Field "live_orders_blocked" -ExpectedValue $true -Label "health.safety"
    Test-MaxRisk -Body $healthBody.safety -Label "health.safety"
} else {
    Write-Result -Level INFO -Name "Health safety payload unavailable"
}

# ---------------------------------------------------------------------------
# Paper sandbox preview
# ---------------------------------------------------------------------------
try {
    $previewBody = Invoke-JsonGet -Uri "$($BackendBaseUrl.TrimEnd('/'))/api/paper/sandbox/preview"
    Write-Result -Level PASS -Name "GET /api/paper/sandbox/preview returned HTTP 200"
} catch {
    Write-Result -Level FAIL -Name "GET /api/paper/sandbox/preview failed" -Detail $_.Exception.Message
    $previewBody = $null
}

if ($null -ne $previewBody) {
    $preview = Get-Payload -Body $previewBody -PreferredProperty "state"
    Test-SafetyField -Body $preview -Field "paper_only" -ExpectedValue $true -Label "preview"
    Test-SafetyField -Body $preview -Field "dry_run" -ExpectedValue $true -Label "preview"
    Test-SafetyField -Body $preview -Field "read_only" -ExpectedValue $true -Label "preview"
    Test-SafetyField -Body $preview -Field "live_orders_blocked" -ExpectedValue $true -Label "preview"
    Test-SafetyField -Body $preview -Field "requires_human_review" -ExpectedValue $true -Label "preview"
    Test-SafetyField -Body $preview -Field "broker_execution_allowed" -ExpectedValue $false -Label "preview"
    Test-SafetyField -Body $preview -Field "risk_allowed" -ExpectedValue $false -Label "preview"
    Test-SafetyField -Body $preview -Field "execution_mode" -ExpectedValue "dry_run_only" -Label "preview"

    if ($null -ne $preview.PSObject.Properties["count"]) {
        if ([int]$preview.count -ge 0) {
            Write-Result -Level PASS -Name "preview.count is non-negative" -Detail "$($preview.count)"
        } else {
            Write-Result -Level FAIL -Name "preview.count" -Detail "got: $($preview.count)"
        }
    }
    if ($null -ne $preview.PSObject.Properties["entries"]) {
        Write-Result -Level PASS -Name "preview.entries present" -Detail "$(@($preview.entries).Count) item(s)"
    }
}

# ---------------------------------------------------------------------------
# Paper sandbox history
# ---------------------------------------------------------------------------
try {
    $historyBody = Invoke-JsonGet -Uri "$($BackendBaseUrl.TrimEnd('/'))/api/paper/sandbox/history"
    Write-Result -Level PASS -Name "GET /api/paper/sandbox/history returned HTTP 200"
} catch {
    Write-Result -Level FAIL -Name "GET /api/paper/sandbox/history failed" -Detail $_.Exception.Message
    $historyBody = $null
}

if ($null -ne $historyBody) {
    $history = Get-Payload -Body $historyBody -PreferredProperty "history"
    Test-SafetyField -Body $history -Field "paper_only" -ExpectedValue $true -Label "history"
    Test-SafetyField -Body $history -Field "dry_run" -ExpectedValue $true -Label "history"
    Test-SafetyField -Body $history -Field "read_only" -ExpectedValue $true -Label "history"
    Test-SafetyField -Body $history -Field "live_orders_blocked" -ExpectedValue $true -Label "history"
    Test-SafetyField -Body $history -Field "requires_human_review" -ExpectedValue $true -Label "history"
    Test-SafetyField -Body $history -Field "broker_execution_allowed" -ExpectedValue $false -Label "history"
    Test-SafetyField -Body $history -Field "risk_allowed" -ExpectedValue $false -Label "history"
    Test-SafetyField -Body $history -Field "execution_mode" -ExpectedValue "dry_run_only" -Label "history"

    if ($null -ne $history.PSObject.Properties["count"]) {
        if ([int]$history.count -ge 0) {
            Write-Result -Level PASS -Name "history.count is non-negative" -Detail "$($history.count)"
        } else {
            Write-Result -Level FAIL -Name "history.count" -Detail "got: $($history.count)"
        }
    }
    if ($null -ne $history.PSObject.Properties["events"]) {
        Write-Result -Level PASS -Name "history.events present" -Detail "$(@($history.events).Count) item(s)"
    }
}

# ---------------------------------------------------------------------------
# Optional frontend routes
# ---------------------------------------------------------------------------
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "Frontend route checks"
    $frontendOk = $true
    foreach ($path in @("/", "/terminal")) {
        if (-not (Test-OptionalFrontendRoute -Path $path)) {
            $frontendOk = $false
        }
    }
    if ($frontendOk) {
        Write-Result -Level PASS -Name "Frontend routes responded"
    }
}
else {
    Write-Result -Level WARN -Name "Frontend checks skipped"
}

Write-Host ""
Write-Host "Summary"
Write-Host "  PASS: $PassCount"
Write-Host "  FAIL: $FailCount"
Write-Host "  Safety posture: autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max risk <=1%"

if ($FailCount -gt 0) {
    Write-Host "RESULT: FAIL"
    exit 1
}

Write-Host "RESULT: PASS"
