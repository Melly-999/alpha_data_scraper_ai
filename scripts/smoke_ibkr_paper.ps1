param(
    [string]$BaseUrl = "http://127.0.0.1:8001"
)

$ErrorActionPreference = "Stop"

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

$account = Invoke-SmokeJson -Name "/api/broker/account" -Method "GET" -Uri "$BaseUrl/api/broker/account"
if ($account.adapter -ne "ibkr_paper") {
    Write-Host "FAIL broker account adapter"
    exit 1
}

$body = '{"decision_id":"smoke-001","signal_id":"sig-001","symbol":"AAPL","direction":"BUY","confidence":72}'
$report = Invoke-SmokeJson -Name "/api/broker/dry-run-report" -Method "POST" -Uri "$BaseUrl/api/broker/dry-run-report" -Body $body
if ($report.broker -ne "ibkr_paper" -or $report.dry_run -ne $true) {
    Write-Host "FAIL dry-run report safety fields"
    exit 1
}

Write-Host "OK   IBKR paper smoke passed"
