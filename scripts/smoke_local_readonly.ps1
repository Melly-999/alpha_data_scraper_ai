param(
    [string]$BaseUrl = "http://127.0.0.1:8001"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PassCount = 0
$FailCount = 0

function Write-Result {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("PASS", "FAIL")][string]$Level,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Detail = ""
    )
    if ($Level -eq "PASS") {
        $script:PassCount++
        $tag = "[PASS]"
    } else {
        $script:FailCount++
        $tag = "[FAIL]"
    }
    $line = "$tag $Name"
    if ($Detail) { $line += "  ($Detail)" }
    Write-Host $line
}

function Invoke-GetJson {
    param(
        [Parameter(Mandatory = $true)][string]$Uri
    )
    # GET only -- never POST/PUT/PATCH/DELETE
    $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri -TimeoutSec 8 -ErrorAction Stop
    return $response.Content | ConvertFrom-Json
}

# ---------------------------------------------------------------------------
# Preflight: confirm backend is reachable before running checks
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "MellyTrade local read-only smoke  |  backend: $BaseUrl"
Write-Host "GET-only. No POST/PUT/DELETE. No execution. No secrets required."
Write-Host ""

try {
    Invoke-GetJson -Uri "$BaseUrl/health" | Out-Null
} catch {
    Write-Host "[FAIL] preflight: backend not reachable at $BaseUrl"
    Write-Host "       Start it with: .\scripts\start_backend_local.ps1"
    Write-Host "       Then re-run this script."
    exit 1
}
Write-Host "[INFO] backend reachable -- running checks"
Write-Host ""

# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------
try {
    $h = Invoke-GetJson -Uri "$BaseUrl/health"
    if ($h.status -eq "ok") {
        Write-Result -Level PASS -Name "/health  status=ok"
    } else {
        Write-Result -Level FAIL -Name "/health  status" -Detail "got: $($h.status)"
    }
    # Safety flags
    if ($h.safety.dry_run -eq $true) {
        Write-Result -Level PASS -Name "/health  safety.dry_run=true"
    } else {
        Write-Result -Level FAIL -Name "/health  safety.dry_run" -Detail "got: $($h.safety.dry_run)"
    }
    if ($h.safety.auto_trade -eq $false) {
        Write-Result -Level PASS -Name "/health  safety.auto_trade=false"
    } else {
        Write-Result -Level FAIL -Name "/health  safety.auto_trade" -Detail "got: $($h.safety.auto_trade)"
    }
    if ($h.safety.max_risk_per_trade -le 1.0) {
        Write-Result -Level PASS -Name "/health  safety.max_risk_per_trade<=$($h.safety.max_risk_per_trade)"
    } else {
        Write-Result -Level FAIL -Name "/health  safety.max_risk_per_trade" -Detail "got: $($h.safety.max_risk_per_trade)"
    }
} catch {
    Write-Result -Level FAIL -Name "/health" -Detail $_.Exception.Message
}

# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------
try {
    $ah = Invoke-GetJson -Uri "$BaseUrl/api/health"
    if ($ah.status -eq "ok") {
        Write-Result -Level PASS -Name "/api/health  status=ok"
    } else {
        Write-Result -Level FAIL -Name "/api/health  status" -Detail "got: $($ah.status)"
    }
} catch {
    Write-Result -Level FAIL -Name "/api/health" -Detail $_.Exception.Message
}

# ---------------------------------------------------------------------------
# /api/signals/scanner/preview
# ---------------------------------------------------------------------------
try {
    $scan = Invoke-GetJson -Uri "$BaseUrl/api/signals/scanner/preview"
    if ($null -ne $scan.results) {
        Write-Result -Level PASS -Name "/api/signals/scanner/preview  results present ($($scan.results.Count) symbols)"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/scanner/preview  results" -Detail "null"
    }
    # Every result must be advisory-only
    $bad = $scan.results | Where-Object { $_.risk_allowed -ne $false }
    if (-not $bad) {
        Write-Result -Level PASS -Name "/api/signals/scanner/preview  all risk_allowed=false"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/scanner/preview  risk_allowed" -Detail "$($bad.Count) result(s) have risk_allowed=true"
    }
    $badMode = $scan.results | Where-Object { $_.execution_mode -ne "dry_run_only" }
    if (-not $badMode) {
        Write-Result -Level PASS -Name "/api/signals/scanner/preview  all execution_mode=dry_run_only"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/scanner/preview  execution_mode" -Detail "$($badMode.Count) result(s) not dry_run_only"
    }
    $badReview = $scan.results | Where-Object { $_.requires_human_review -ne $true }
    if (-not $badReview) {
        Write-Result -Level PASS -Name "/api/signals/scanner/preview  all requires_human_review=true"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/scanner/preview  requires_human_review" -Detail "$($badReview.Count) result(s) false"
    }
} catch {
    Write-Result -Level FAIL -Name "/api/signals/scanner/preview" -Detail $_.Exception.Message
}

# ---------------------------------------------------------------------------
# /api/signals/decisions
# ---------------------------------------------------------------------------
try {
    $dec = Invoke-GetJson -Uri "$BaseUrl/api/signals/decisions"
    if ($dec.dry_run -eq $true) {
        Write-Result -Level PASS -Name "/api/signals/decisions  dry_run=true"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/decisions  dry_run" -Detail "got: $($dec.dry_run)"
    }
    if ($dec.auto_trade -eq $false) {
        Write-Result -Level PASS -Name "/api/signals/decisions  auto_trade=false"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/decisions  auto_trade" -Detail "got: $($dec.auto_trade)"
    }
    if ($dec.read_only -eq $true) {
        Write-Result -Level PASS -Name "/api/signals/decisions  read_only=true"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/decisions  read_only" -Detail "got: $($dec.read_only)"
    }
} catch {
    Write-Result -Level FAIL -Name "/api/signals/decisions" -Detail $_.Exception.Message
}

# ---------------------------------------------------------------------------
# /api/signals/lifecycle
# ---------------------------------------------------------------------------
try {
    $lc = Invoke-GetJson -Uri "$BaseUrl/api/signals/lifecycle"
    if ($lc.dry_run -eq $true) {
        Write-Result -Level PASS -Name "/api/signals/lifecycle  dry_run=true"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/lifecycle  dry_run" -Detail "got: $($lc.dry_run)"
    }
    if ($lc.auto_trade -eq $false) {
        Write-Result -Level PASS -Name "/api/signals/lifecycle  auto_trade=false"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/lifecycle  auto_trade" -Detail "got: $($lc.auto_trade)"
    }
    if ($lc.supports_live_orders -eq $false) {
        Write-Result -Level PASS -Name "/api/signals/lifecycle  supports_live_orders=false"
    } else {
        Write-Result -Level FAIL -Name "/api/signals/lifecycle  supports_live_orders" -Detail "got: $($lc.supports_live_orders)"
    }
} catch {
    Write-Result -Level FAIL -Name "/api/signals/lifecycle" -Detail $_.Exception.Message
}

# ---------------------------------------------------------------------------
# /api/risk/config -- optional, skip gracefully if route absent
# ---------------------------------------------------------------------------
try {
    $rc = Invoke-GetJson -Uri "$BaseUrl/api/risk/config"
    if ($rc.dry_run -eq $true) {
        Write-Result -Level PASS -Name "/api/risk/config  dry_run=true"
    } else {
        Write-Result -Level FAIL -Name "/api/risk/config  dry_run" -Detail "got: $($rc.dry_run)"
    }
    if ($rc.auto_trade -eq $false) {
        Write-Result -Level PASS -Name "/api/risk/config  auto_trade=false"
    } else {
        Write-Result -Level FAIL -Name "/api/risk/config  auto_trade" -Detail "got: $($rc.auto_trade)"
    }
} catch {
    Write-Host "[SKIP] /api/risk/config  (not available or unreachable)"
}

# ---------------------------------------------------------------------------
# /api/brokers -- optional, skip gracefully if route absent
# ---------------------------------------------------------------------------
try {
    $brokers = Invoke-GetJson -Uri "$BaseUrl/api/brokers"
    if ($null -ne $brokers) {
        Write-Result -Level PASS -Name "/api/brokers  reachable"
    }
} catch {
    Write-Host "[SKIP] /api/brokers  (not available or unreachable)"
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================"
$total = $PassCount + $FailCount
Write-Host "  Smoke result: $PassCount PASS  /  $FailCount FAIL  ($total checks)"
if ($FailCount -eq 0) {
    Write-Host "  RESULT: PASS -- all safety checks green"
} else {
    Write-Host "  RESULT: FAIL -- review FAIL lines above"
}
Write-Host "  Read-only: no orders placed, no mutations made."
Write-Host "======================================================"
Write-Host ""

if ($FailCount -gt 0) { exit 1 }
