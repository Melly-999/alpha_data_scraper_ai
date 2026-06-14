<#
.SYNOPSIS
    Read-only smoke test for MellyTrade's simulated / paper broker preview surface.

.DESCRIPTION
    BROKER-SIM-READONLY-SMOKE-SCRIPT-001.

    GET-only verification of the already-safe broker / paper / safety surfaces
    described in docs/tasks/broker_sim_readiness_audit_001.md. The script:

      * issues GET requests only (never POST/PUT/PATCH/DELETE),
      * requires no credentials and reads no .env files,
      * never sends broker auth headers,
      * asserts the documented safety flags
        (dry_run, auto_trade, read_only, live_orders_blocked, max risk <= 1%),
      * scans every response body for forbidden / sensitive field names,
      * records missing routes as SKIP/INFO (not as failures),
      * exits non-zero ONLY on a hard safety failure
        (an unsafe flag value, or a forbidden field present in a response),
      * exits zero on an acceptable degraded state (backend unreachable),
        so it can run safely in CI or on a developer box with no backend.

    This is NOT live trading. It does not connect to a real broker, does not
    place / submit / cancel orders, and does not execute trades. It is GET-only
    evidence for the read-only simulated broker preview.

.PARAMETER BaseUrl
    Backend base URL. Defaults to the local backend convention
    (http://127.0.0.1:8001). Pass a hosted URL to smoke the hosted backend,
    e.g. -BaseUrl https://your-backend.example.com

.PARAMETER TimeoutSec
    Per-request timeout in seconds (default 8).

.EXAMPLE
    .\scripts\broker_sim_readonly_smoke.ps1
    # Local backend on 127.0.0.1:8001

.EXAMPLE
    .\scripts\broker_sim_readonly_smoke.ps1 -BaseUrl https://your-backend.example.com -TimeoutSec 15
    # Hosted backend, GET-only
#>

param(
    [string]$BaseUrl = "http://127.0.0.1:8001",
    [int]$TimeoutSec = 8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:PassCount = 0
$script:SafetyFailCount = 0   # hard failures -> exit 1
$script:WarnCount = 0         # non-fatal (endpoint missing/errored while up)
$script:SkipCount = 0

$Base = $BaseUrl.TrimEnd('/')

# Field names that must never appear in a read-only preview response.
$ForbiddenFields = @(
    "account_id",
    "broker_account_id",
    "broker_order_id",
    "execution_id",
    "secret",
    "token",
    "api_key",
    "private_key"
)

function Write-Result {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("PASS", "FAIL", "WARN", "SKIP", "INFO")][string]$Level,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Detail = ""
    )
    switch ($Level) {
        "PASS" { $script:PassCount++; $tag = "[PASS]" }
        "FAIL" { $script:SafetyFailCount++; $tag = "[FAIL]" }
        "WARN" { $script:WarnCount++; $tag = "[WARN]" }
        "SKIP" { $script:SkipCount++; $tag = "[SKIP]" }
        "INFO" { $tag = "[INFO]" }
    }
    $line = "$tag $Name"
    if ($Detail) { $line += "  ($Detail)" }
    Write-Host $line
}

# GET only. Returns @{ Ok = $bool; Status = <int>; Body = <obj>; Error = <string> }.
function Invoke-Probe {
    param([Parameter(Mandatory = $true)][string]$Path)
    $uri = "$Base$Path"
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $uri -TimeoutSec $TimeoutSec -ErrorAction Stop
        $body = $null
        if ($resp.Content) {
            try { $body = $resp.Content | ConvertFrom-Json } catch { $body = $null }
        }
        return @{ Ok = $true; Status = [int]$resp.StatusCode; Body = $body; Error = "" }
    } catch {
        $status = 0
        if ($_.Exception.PSObject.Properties["Response"] -and $_.Exception.Response) {
            try { $status = [int]$_.Exception.Response.StatusCode.value__ } catch { $status = 0 }
        }
        return @{ Ok = $false; Status = $status; Body = $null; Error = $_.Exception.Message }
    }
}

# Recursively collect property names from a parsed-JSON object graph.
# Only objects (PSCustomObject) and collections are traversed; every other
# value (string, number, bool, datetime, ...) is treated as a leaf. This avoids
# walking into .NET value-type internals such as DateTime.Date, which is
# self-referential and would otherwise loop forever.
function Get-PropertyNames {
    param($Node)
    $names = New-Object System.Collections.Generic.List[string]
    $stack = New-Object System.Collections.Stack
    $stack.Push($Node)
    while ($stack.Count -gt 0) {
        $cur = $stack.Pop()
        if ($null -eq $cur) { continue }
        if ($cur -is [System.Management.Automation.PSCustomObject]) {
            foreach ($p in $cur.PSObject.Properties) {
                $names.Add($p.Name)
                $stack.Push($p.Value)
            }
        } elseif (($cur -is [System.Collections.IEnumerable]) -and -not ($cur -is [string])) {
            foreach ($item in $cur) { $stack.Push($item) }
        }
        # else: scalar leaf -- nothing to traverse.
    }
    return $names
}

# Fail if any forbidden field name appears anywhere in the response body.
function Test-NoForbiddenFields {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        $Body
    )
    if ($null -eq $Body) { return }
    $names = Get-PropertyNames -Node $Body
    $hits = @($names | Where-Object { $ForbiddenFields -contains $_.ToLowerInvariant() } | Select-Object -Unique)
    if ($hits.Count -gt 0) {
        Write-Result -Level FAIL -Name "$Label forbidden field(s) present" -Detail ($hits -join ", ")
    } else {
        Write-Result -Level PASS -Name "$Label no forbidden fields"
    }
}

# Assert a boolean safety flag, if present.
function Test-Flag {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)]$Body,
        [Parameter(Mandatory = $true)][string]$Field,
        [Parameter(Mandatory = $true)][bool]$Expected
    )
    if ($null -eq $Body -or $null -eq $Body.PSObject.Properties[$Field]) {
        Write-Result -Level INFO -Name "$Label.$Field unavailable"
        return
    }
    if ([bool]$Body.$Field -eq $Expected) {
        Write-Result -Level PASS -Name "$Label.$Field=$Expected"
    } else {
        Write-Result -Level FAIL -Name "$Label.$Field" -Detail "got: $($Body.$Field)"
    }
}

Write-Host ""
Write-Host "MellyTrade broker-sim read-only smoke  |  backend: $Base"
Write-Host "GET-only. No POST/PUT/PATCH/DELETE. No credentials. No execution. No secrets."
Write-Host "Simulated / demo data only -- this does not connect to a broker or place orders."
Write-Host ""

# ---------------------------------------------------------------------------
# Preflight: backend reachable? Unreachable == acceptable degraded -> exit 0.
# ---------------------------------------------------------------------------
$health = Invoke-Probe -Path "/health"
if (-not $health.Ok) {
    $alt = Invoke-Probe -Path "/api/health"
    if ($alt.Ok) { $health = $alt }
}
if (-not $health.Ok) {
    Write-Result -Level INFO -Name "backend not reachable at $Base"
    Write-Host "[INFO] Nothing to verify (degraded / offline). This is not a safety failure."
    Write-Host "[INFO] Start a local backend with: .\scripts\start_backend_local.ps1"
    Write-Host ""
    Write-Host "RESULT: SKIPPED (backend offline) -- no orders placed, no mutations made."
    exit 0
}
Write-Result -Level PASS -Name "backend reachable" -Detail "/health"
Test-NoForbiddenFields -Label "health" -Body $health.Body
if ($null -ne $health.Body -and $null -ne $health.Body.PSObject.Properties["safety"]) {
    $hs = $health.Body.safety
    Test-Flag -Label "health.safety" -Body $hs -Field "dry_run" -Expected $true
    Test-Flag -Label "health.safety" -Body $hs -Field "auto_trade" -Expected $false
}

# ---------------------------------------------------------------------------
# Core safety anchor: /api/safety/status  (required when backend is up)
# ---------------------------------------------------------------------------
$safety = Invoke-Probe -Path "/api/safety/status"
if ($safety.Ok -and $null -ne $safety.Body) {
    Write-Result -Level PASS -Name "GET /api/safety/status -> HTTP $($safety.Status)"
    $s = $safety.Body
    Test-Flag -Label "safety" -Body $s -Field "dry_run" -Expected $true
    Test-Flag -Label "safety" -Body $s -Field "auto_trade" -Expected $false
    Test-Flag -Label "safety" -Body $s -Field "read_only" -Expected $true
    Test-Flag -Label "safety" -Body $s -Field "live_orders_blocked" -Expected $true
    if ($null -ne $s.PSObject.Properties["max_risk_per_trade_pct"]) {
        $mr = [double]$s.max_risk_per_trade_pct
        if ($mr -le 1.0) {
            Write-Result -Level PASS -Name "safety.max_risk_per_trade_pct<=1.0" -Detail "$mr"
        } else {
            Write-Result -Level FAIL -Name "safety.max_risk_per_trade_pct" -Detail "got: $mr"
        }
    } else {
        Write-Result -Level INFO -Name "safety.max_risk_per_trade_pct unavailable"
    }
    Test-NoForbiddenFields -Label "safety" -Body $s
} else {
    # Backend is up but the safety anchor is unreadable -> we cannot confirm safety.
    Write-Result -Level FAIL -Name "GET /api/safety/status unreadable" -Detail $safety.Error
}

# ---------------------------------------------------------------------------
# Read-only GET surface. Missing routes -> SKIP (not a failure).
# Each present route is scanned for forbidden fields.
# ---------------------------------------------------------------------------
$readOnlyProbes = @(
    "/api/broker/health",
    "/api/broker/account",
    "/api/brokers",
    "/api/alpaca-paper/status",
    "/api/alpaca-paper/account-preview",
    "/api/alpaca-paper/market-clock",
    "/api/account/overview",
    "/api/positions/open",
    "/api/positions/history",
    "/api/orders",
    "/api/risk/status",
    "/api/risk/violations",
    "/api/terminal/summary"
)

foreach ($path in $readOnlyProbes) {
    $r = Invoke-Probe -Path $path
    if ($r.Ok) {
        Write-Result -Level PASS -Name "GET $path -> HTTP $($r.Status)"
        Test-NoForbiddenFields -Label $path -Body $r.Body
    } elseif ($r.Status -eq 404) {
        Write-Result -Level SKIP -Name "GET $path not present (HTTP 404)"
    } else {
        Write-Result -Level WARN -Name "GET $path unavailable" -Detail $r.Error
    }
}

# ---------------------------------------------------------------------------
# Per-adapter broker sub-routes (read-only): discover ids from /api/brokers.
# ---------------------------------------------------------------------------
$brokers = Invoke-Probe -Path "/api/brokers"
if ($brokers.Ok -and $null -ne $brokers.Body) {
    $adapters = $brokers.Body
    if ($adapters.PSObject.Properties["brokers"]) { $adapters = $adapters.brokers }
    elseif ($adapters.PSObject.Properties["adapters"]) { $adapters = $adapters.adapters }
    $ids = @()
    foreach ($a in @($adapters)) {
        if ($null -eq $a) { continue }
        if ($a -is [string]) { $ids += $a; continue }
        foreach ($key in @("id", "adapter_id", "name", "slug")) {
            if ($a.PSObject.Properties[$key]) { $ids += [string]$a.$key; break }
        }
    }
    $ids = @($ids | Where-Object { $_ } | Select-Object -Unique)
    if ($ids.Count -eq 0) {
        Write-Result -Level INFO -Name "/api/brokers exposed no adapter ids to probe"
    }
    foreach ($id in $ids) {
        foreach ($sub in @("status", "account", "positions")) {
            $r = Invoke-Probe -Path "/api/brokers/$id/$sub"
            if ($r.Ok) {
                Write-Result -Level PASS -Name "GET /api/brokers/$id/$sub -> HTTP $($r.Status)"
                Test-NoForbiddenFields -Label "/api/brokers/$id/$sub" -Body $r.Body
            } elseif ($r.Status -eq 404) {
                Write-Result -Level SKIP -Name "GET /api/brokers/$id/$sub not present (HTTP 404)"
            } else {
                Write-Result -Level WARN -Name "GET /api/brokers/$id/$sub unavailable" -Detail $r.Error
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================"
Write-Host "  Broker-sim read-only smoke"
Write-Host "  PASS: $($script:PassCount)   SAFETY-FAIL: $($script:SafetyFailCount)   WARN: $($script:WarnCount)   SKIP: $($script:SkipCount)"
Write-Host "  Safety posture: autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true, max risk <=1%"
Write-Host "  GET-only: no orders placed, no mutations made, no credentials used."
if ($script:SafetyFailCount -gt 0) {
    Write-Host "  RESULT: FAIL -- review [FAIL] lines above"
    Write-Host "======================================================"
    Write-Host ""
    exit 1
}
Write-Host "  RESULT: PASS -- read-only surface safe"
Write-Host "======================================================"
Write-Host ""
exit 0
