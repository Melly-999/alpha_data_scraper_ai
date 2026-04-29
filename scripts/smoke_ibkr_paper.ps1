param(
    [string]$BaseUrl = "http://127.0.0.1:8001"
)

$ErrorActionPreference = "Stop"

function Test-BackendReachable {
    param(
        [Parameter(Mandatory = $true)][string]$BaseUrl
    )

    try {
        Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$BaseUrl/health" -TimeoutSec 3 | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Invoke-SmokeJson {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [string]$Body
    )

    try {
        if ($Method -eq "POST") {
            $response = Invoke-WebRequest -UseBasicParsing -Method POST -Uri $Uri -ContentType "application/json" -Body $Body
        } else {
            $response = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $Uri
        }
        $json = $response.Content | ConvertFrom-Json
        Write-Host "OK   $Name [$($response.StatusCode)]"
        return $json
    } catch {
        Write-Host "FAIL $Name"
        Write-Host $_.Exception.Message
        exit 1
    }
}

# Friendly preflight: print a clear hint if the backend is not running so
# beginners do not have to decode a generic connection-refused error.
if (-not (Test-BackendReachable -BaseUrl $BaseUrl)) {
    Write-Host "FAIL preflight: backend is not running on $BaseUrl."
    Write-Host "     Start it with: .\scripts\start_backend_ibkr_paper.ps1"
    Write-Host "     This smoke check is read-only; it does not place orders."
    exit 1
}

$health = Invoke-SmokeJson -Name "/health" -Method "GET" -Uri "$BaseUrl/health"
if ($health.status -ne "ok" -or $health.safety.dry_run -ne $true -or $health.safety.auto_trade -ne $false) {
    Write-Host "FAIL /health safety fields"
    exit 1
}

$apiHealth = Invoke-SmokeJson -Name "/api/health" -Method "GET" -Uri "$BaseUrl/api/health"
if ($apiHealth.status -ne "ok" -or $apiHealth.safety.dry_run -ne $true -or $apiHealth.safety.auto_trade -ne $false) {
    Write-Host "FAIL /api/health safety fields"
    exit 1
}

$brokerHealth = Invoke-SmokeJson -Name "/api/broker/health" -Method "GET" -Uri "$BaseUrl/api/broker/health"
if ($brokerHealth.adapter -ne "ibkr_paper" -or $brokerHealth.supports_live_orders -ne $false) {
    Write-Host "FAIL broker health safety fields"
    exit 1
}
# Paper-only invariants: mode must stay paper, the port must be a known
# paper port, and the typed status must be one of the safe states. With
# TWS Paper running we expect connected=true; without it we accept any of
# the safe disconnected states the adapter exposes.
$allowedStatuses = @("connected", "ok", "missing_dependency", "connect_failed", "disabled")
if ($brokerHealth.mode -ne "paper" -and $brokerHealth.mode -ne "disabled") {
    Write-Host "FAIL broker health mode=$($brokerHealth.mode) (must be paper or disabled)"
    exit 1
}
if ($brokerHealth.port -notin @(7497, 4002, 0)) {
    Write-Host "FAIL broker health port=$($brokerHealth.port) (must be a paper port)"
    exit 1
}
if ($brokerHealth.status -notin $allowedStatuses) {
    Write-Host "FAIL broker health status=$($brokerHealth.status) not in $($allowedStatuses -join ', ')"
    exit 1
}

$account = Invoke-SmokeJson -Name "/api/broker/account" -Method "GET" -Uri "$BaseUrl/api/broker/account"
if ($account.adapter -ne "ibkr_paper") {
    Write-Host "FAIL broker account adapter"
    exit 1
}
# Account endpoint must never crash and must always be safe. When
# disconnected, balances are zeroed and a last_error explains why.
if ($account.connected -eq $false) {
    if ($account.net_liquidation -ne 0 -or $account.cash -ne 0 -or $account.buying_power -ne 0) {
        Write-Host "FAIL disconnected account snapshot is not zeroed"
        exit 1
    }
}

$body = '{"decision_id":"smoke-001","signal_id":"sig-001","symbol":"AAPL","direction":"BUY","confidence":72}'
$report = Invoke-SmokeJson -Name "/api/broker/dry-run-report" -Method "POST" -Uri "$BaseUrl/api/broker/dry-run-report" -Body $body
if ($report.broker -ne "ibkr_paper" -or $report.dry_run -ne $true) {
    Write-Host "FAIL dry-run report safety fields"
    exit 1
}

Write-Host "OK   IBKR paper smoke passed"
