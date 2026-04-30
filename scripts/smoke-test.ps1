# Smoke test for MellyTrade Direction B (Sprint 1C)
# Runs mellytrade-api backend and frontend dev server, validates endpoints
# Usage: .\scripts\smoke-test.ps1

$BackendJob = $null
$FrontendJob = $null

function Cleanup {
  Write-Host "Cleaning up..."
  if ($BackendJob) { Stop-Job -Job $BackendJob -Force -ErrorAction SilentlyContinue }
  if ($FrontendJob) { Stop-Job -Job $FrontendJob -Force -ErrorAction SilentlyContinue }
}

trap {
  Cleanup
  exit 1
}

Write-Host "Starting mellytrade-api (port 8000)..."
Push-Location mellytrade_v3/mellytrade-api
$BackendJob = Start-Job -ScriptBlock {
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
}
Pop-Location

Write-Host "Waiting for backend to be ready..."
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
  try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
      Write-Host "✓ Backend ready"
      break
    }
  } catch {
    # Still starting, retry
  }
  $attempt++
  if ($attempt -eq $maxAttempts) {
    Write-Host "✗ Backend did not start"
    Cleanup
    exit 1
  }
  Start-Sleep -Seconds 1
}

Write-Host "Starting frontend dev server (port 5173)..."
Push-Location frontend
$FrontendJob = Start-Job -ScriptBlock {
  npm run dev
}
Pop-Location

Write-Host "Waiting for frontend to be ready..."
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
  try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
      Write-Host "✓ Frontend ready"
      break
    }
  } catch {
    # Still starting, retry
  }
  $attempt++
  if ($attempt -eq $maxAttempts) {
    Write-Host "✗ Frontend did not start"
    Cleanup
    exit 1
  }
  Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Running smoke tests..."
Write-Host ""

# Test 1: Backend health endpoint
Write-Host "Test 1: GET /health (backend safety posture)"
$health = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing).Content | ConvertFrom-Json
$health | ConvertTo-Json
if ($health.dry_run -eq $true) {
  Write-Host "✓ dry_run is enabled"
} else {
  Write-Host "✗ dry_run is not enabled"
  Cleanup
  exit 1
}

# Test 2: Backend signals endpoint
Write-Host ""
Write-Host "Test 2: GET /signals (signal feed)"
$signals = (Invoke-WebRequest -Uri "http://localhost:8000/signals?limit=5" -UseBasicParsing).Content | ConvertFrom-Json
Write-Host "Signals count: $($signals.signals.Length)"
Write-Host "✓ Signals endpoint reachable"

# Test 3: Audit feed endpoint
Write-Host ""
Write-Host "Test 3: GET /audit (audit feed)"
$audit = (Invoke-WebRequest -Uri "http://localhost:8000/audit?limit=5" -UseBasicParsing).Content | ConvertFrom-Json
Write-Host "Audit events count: $($audit.events.Length)"
Write-Host "✓ Audit endpoint reachable"

# Test 4: Risk config endpoint
Write-Host ""
Write-Host "Test 4: GET /risk/config (risk gates)"
$risk = (Invoke-WebRequest -Uri "http://localhost:8000/risk/config" -UseBasicParsing).Content | ConvertFrom-Json
Write-Host "Max risk %: $($risk.max_risk_pct)"
Write-Host "✓ Risk config endpoint reachable"

# Test 5: Frontend dev proxy (via dev server)
Write-Host ""
Write-Host "Test 5: Frontend dev proxy /melly-api/health"
try {
  $proxy = (Invoke-WebRequest -Uri "http://localhost:5173/melly-api/health" -UseBasicParsing).Content | ConvertFrom-Json
  if ($proxy.dry_run -eq $true) {
    Write-Host "✓ Dev proxy working"
  } else {
    Write-Host "✗ Dev proxy returned invalid response"
    Cleanup
    exit 1
  }
} catch {
  Write-Host "✗ Dev proxy failed"
  Cleanup
  exit 1
}

Write-Host ""
Write-Host "✓ All smoke tests passed!"
Cleanup
