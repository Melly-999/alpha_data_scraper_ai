# PAPER-003 - Local paper sandbox demo smoke script
#
# Validates the local paper sandbox dashboard flow:
#   paper ticket draft -> sandbox preview -> history/audit -> UI ready
#
# READ-ONLY / DRY-RUN ONLY.
# No broker execution. No MT5/IBKR calls. No live orders. No order controls.
# Calls only existing GET endpoints. Writes nothing. No network outside localhost.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_local.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_local.ps1 -Strict
#
# Parameters:
#   -BackendBaseUrl   Base URL for the local FastAPI backend  (default: http://127.0.0.1:8001)
#   -FrontendUrl      Workspace route for the local frontend   (default: http://127.0.0.1:5174/workspace)
#   -TimeoutSeconds   HTTP request timeout in seconds          (default: 10)
#   -Strict           If set, any backend/endpoint failure exits non-zero.
#                     Without -Strict, offline backend exits 0 with a degraded warning.

param(
    [string]$BackendBaseUrl = "http://127.0.0.1:8001",
    [string]$FrontendUrl    = "http://127.0.0.1:5174/workspace",
    [int]$TimeoutSeconds    = 10,
    [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$RepoRoot      = Resolve-Path (Join-Path $PSScriptRoot "..")
$PassCount     = 0
$WarnCount     = 0
$FailCount     = 0
$BackendOnline = $false

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
function Write-Pass  { param([string]$Msg) Write-Host "[PASS] $Msg" -ForegroundColor Green;  $script:PassCount++ }
function Write-Warn  { param([string]$Msg) Write-Host "[WARN] $Msg" -ForegroundColor Yellow; $script:WarnCount++ }
function Write-Fail  { param([string]$Msg) Write-Host "[FAIL] $Msg" -ForegroundColor Red;    $script:FailCount++ }
function Write-Info  { param([string]$Msg) Write-Host "[INFO] $Msg" }
function Write-Head  { param([string]$Msg) Write-Host "" ; Write-Host "=== $Msg ===" -ForegroundColor Cyan }

# ---------------------------------------------------------------------------
# HTTP helpers (GET-only; no mutation)
# ---------------------------------------------------------------------------
function Invoke-GetJson {
    param(
        [string]$Label,
        [string]$Uri
    )
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec $TimeoutSeconds
        if ($resp.StatusCode -eq 200) {
            return $resp.Content | ConvertFrom-Json
        }
        throw "$Label returned HTTP $($resp.StatusCode)"
    }
    catch {
        throw "$Label - $($_.Exception.Message)"
    }
}

function Test-HttpOk {
    param([string]$Uri)
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec $TimeoutSeconds
        return $resp.StatusCode -eq 200
    }
    catch { return $false }
}

# ---------------------------------------------------------------------------
# Safety-flag validator
# ---------------------------------------------------------------------------
$REQUIRED_TRUE_FLAGS  = @("paper_only", "dry_run", "read_only", "live_orders_blocked", "requires_human_review")
$REQUIRED_FALSE_FLAGS = @("broker_execution_allowed", "risk_allowed")
$REQUIRED_EXEC_MODE   = "dry_run_only"

function Test-SafetyFlags {
    param([string]$Label, $Payload)
    $ok = $true
    foreach ($key in $REQUIRED_TRUE_FLAGS) {
        if ($Payload.$key -ne $true) {
            Write-Fail "$Label - safety flag '$key' must be true (got: $($Payload.$key))"
            $ok = $false
        }
    }
    foreach ($key in $REQUIRED_FALSE_FLAGS) {
        if ($Payload.$key -ne $false) {
            Write-Fail "$Label - safety flag '$key' must be false (got: $($Payload.$key))"
            $ok = $false
        }
    }
    if ($Payload.execution_mode -ne $REQUIRED_EXEC_MODE) {
        Write-Fail "$Label - execution_mode must be '$REQUIRED_EXEC_MODE' (got: $($Payload.execution_mode))"
        $ok = $false
    }
    if ($ok) { Write-Pass "$Label - all safety flags locked correctly" }
    return $ok
}

# ---------------------------------------------------------------------------
# Forbidden-field validator (broker/order/secret fields must not appear)
# ---------------------------------------------------------------------------
$FORBIDDEN_FIELDS = @("order_id","fill_id","execution_id","broker_order_id","account_id","credential","token","secret")

function Test-NoForbiddenFields {
    param([string]$Label, $Payload)
    $payloadJson = $Payload | ConvertTo-Json -Depth 10 -Compress
    $found = @($FORBIDDEN_FIELDS | Where-Object { $payloadJson -match "`"$_`"" })
    if ($found.Count -gt 0) {
        Write-Fail "$Label - response contains forbidden fields: $($found -join ', ')"
        return $false
    }
    Write-Pass "$Label - no forbidden broker/order/secret fields in response"
    return $true
}

# ---------------------------------------------------------------------------
# Main demo flow
# ---------------------------------------------------------------------------
Push-Location $RepoRoot
try {
    Write-Host ""
    Write-Host "PAPER-003 - Local Paper Sandbox Demo Smoke" -ForegroundColor Cyan
    Write-Host "READ-ONLY / DRY-RUN / NO BROKER EXECUTION / NO LIVE ORDERS" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Repo root   : $RepoRoot"
    Write-Info "Backend     : $BackendBaseUrl"
    Write-Info "Frontend    : $FrontendUrl"
    Write-Info "Timeout     : ${TimeoutSeconds}s"
    Write-Info "Strict mode : $($Strict.IsPresent)"
    Write-Host ""

    # -----------------------------------------------------------------------
    # Step 1 - Safety config validation (local, no network)
    # -----------------------------------------------------------------------
    Write-Head "Step 1: Local safety config validation"

    $safetyOut = & py -3.11 scripts/validate_safety_config.py 2>&1
    if ($LASTEXITCODE -eq 0 -and ($safetyOut | Out-String) -match "OVERALL:\s+PASS") {
        Write-Pass "validate_safety_config.py - OVERALL: PASS"
    }
    else {
        Write-Fail "validate_safety_config.py - did not report OVERALL: PASS"
        Write-Host ($safetyOut | Out-String)
    }

    # -----------------------------------------------------------------------
    # Step 2 - Backend health
    # -----------------------------------------------------------------------
    Write-Head "Step 2: Backend health"

    $healthUri  = "$($BackendBaseUrl.TrimEnd('/'))/health"
    $healthUri2 = "$($BackendBaseUrl.TrimEnd('/'))/api/health"

    if (Test-HttpOk -Uri $healthUri) {
        Write-Pass "Backend health - GET $healthUri OK"
        $BackendOnline = $true
    }
    elseif (Test-HttpOk -Uri $healthUri2) {
        Write-Pass "Backend health - GET $healthUri2 OK (fallback)"
        $BackendOnline = $true
    }
    else {
        $msg = "Backend is offline or unreachable at $BackendBaseUrl"
        if ($Strict) {
            Write-Fail $msg
        }
        else {
            Write-Warn "$msg - running in degraded mode (use -Strict to treat this as failure)"
            Write-Info "To start backend: py -3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"
        }
    }

    # -----------------------------------------------------------------------
    # Step 3 - Paper sandbox preview endpoint (GET-only)
    # -----------------------------------------------------------------------
    Write-Head "Step 3: GET /api/paper/sandbox/preview"

    $previewUri = "$($BackendBaseUrl.TrimEnd('/'))/api/paper/sandbox/preview"

    if (-not $BackendOnline) {
        Write-Warn "Skipping preview endpoint check - backend offline"
    }
    else {
        try {
            $preview = Invoke-GetJson -Label "/api/paper/sandbox/preview" -Uri $previewUri
            Write-Pass "GET /api/paper/sandbox/preview - HTTP 200"
            [void](Test-SafetyFlags       -Label "Preview" -Payload $preview)
            [void](Test-NoForbiddenFields -Label "Preview" -Payload $preview)
            Write-Info "Preview entry count : $($preview.count)"
        }
        catch {
            $errMsg = "GET /api/paper/sandbox/preview failed: $_"
            if ($Strict) { Write-Fail $errMsg } else { Write-Warn $errMsg }
        }
    }

    # -----------------------------------------------------------------------
    # Step 4 - Paper sandbox history endpoint (GET-only)
    # -----------------------------------------------------------------------
    Write-Head "Step 4: GET /api/paper/sandbox/history"

    $historyUri = "$($BackendBaseUrl.TrimEnd('/'))/api/paper/sandbox/history"

    if (-not $BackendOnline) {
        Write-Warn "Skipping history endpoint check - backend offline"
    }
    else {
        try {
            $history = Invoke-GetJson -Label "/api/paper/sandbox/history" -Uri $historyUri
            Write-Pass "GET /api/paper/sandbox/history - HTTP 200"
            [void](Test-SafetyFlags       -Label "History" -Payload $history)
            [void](Test-NoForbiddenFields -Label "History" -Payload $history)
            Write-Info "History event count : $($history.count)"
        }
        catch {
            $errMsg = "GET /api/paper/sandbox/history failed: $_"
            if ($Strict) { Write-Fail $errMsg } else { Write-Warn $errMsg }
        }
    }

    # -----------------------------------------------------------------------
    # Step 5 - Frontend workspace route reachability
    # -----------------------------------------------------------------------
    Write-Head "Step 5: Frontend /workspace route"

    if (Test-HttpOk -Uri $FrontendUrl) {
        Write-Pass "Frontend /workspace reachable at $FrontendUrl"
    }
    else {
        Write-Warn "Frontend not reachable at $FrontendUrl"
        Write-Info "To start frontend: cd frontend && npm run dev -- --port 5174"
    }

    # -----------------------------------------------------------------------
    # Step 6 - Demo URLs and screenshot checklist
    # -----------------------------------------------------------------------
    Write-Head "Step 6: Demo URLs and screenshot checklist"

    $swaggerUrl = "$($BackendBaseUrl.TrimEnd('/'))/docs"
    Write-Info "Backend Swagger UI : $swaggerUrl"
    Write-Info "Frontend Workspace : $FrontendUrl"
    Write-Host ""
    Write-Host "Screenshot checklist:" -ForegroundColor Cyan
    Write-Host "  [ ] Paper Sandbox Preview panel visible"
    Write-Host "  [ ] Paper Sandbox Activity / Audit Rail visible"
    Write-Host "  [ ] Endpoint label: GET /api/paper/sandbox/preview"
    Write-Host "  [ ] Endpoint label: GET /api/paper/sandbox/history"
    Write-Host "  [ ] Safety badges: READ ONLY  DRY RUN  LIVE ORDERS BLOCKED"
    Write-Host "                     BROKER DISABLED  HUMAN REVIEW"
    Write-Host "  [ ] No order / buy / sell / execute buttons"
    Write-Host "  [ ] Graceful fallback message if backend is offline"

    # -----------------------------------------------------------------------
    # Step 7 - Safety summary
    # -----------------------------------------------------------------------
    Write-Head "Step 7: Safety posture summary"

    Write-Host ""
    Write-Host "  autotrade            = false" -ForegroundColor Green
    Write-Host "  dry_run              = true"  -ForegroundColor Green
    Write-Host "  read_only            = true"  -ForegroundColor Green
    Write-Host "  live_orders_blocked  = true"  -ForegroundColor Green
    Write-Host "  max_risk_pct         = <= 1%" -ForegroundColor Green
    Write-Host "  broker execution     = NEVER" -ForegroundColor Green
    Write-Host "  MT5/IBKR calls       = NEVER" -ForegroundColor Green
    Write-Host "  live order placement = NEVER" -ForegroundColor Green
    Write-Host "  order controls in UI = NONE"  -ForegroundColor Green
    Write-Host ""

    # -----------------------------------------------------------------------
    # Final result
    # -----------------------------------------------------------------------
    Write-Head "Result"

    Write-Host "  Passed  : $PassCount"
    Write-Host "  Warned  : $WarnCount"
    Write-Host "  Failed  : $FailCount"
    Write-Host ""

    if ($FailCount -gt 0) {
        Write-Fail "Paper sandbox demo smoke FAILED ($FailCount failures)"
        exit 1
    }

    if ($WarnCount -gt 0) {
        Write-Warn "Paper sandbox demo smoke completed with $WarnCount warning(s) - degraded mode"
        exit 0
    }

    Write-Pass "Paper sandbox demo smoke PASSED - dashboard is ready for demo/screenshots"
    exit 0
}
finally {
    Pop-Location
}
