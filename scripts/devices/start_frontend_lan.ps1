# scripts/devices/start_frontend_lan.ps1
#
# Start the MellyTrade frontend dev server bound to 0.0.0.0 so it is
# reachable from a device on the same LAN (e.g. iPad for PWA smoke testing).
#
# SAFETY
#   - autotrade=false, dry_run=true, read_only=true are enforced at config level
#   - this script does NOT set VITE_MELLY_API_BASE_URL or VITE_API_BASE_URL
#     because those env vars override the Vite proxy and point browsers to
#     127.0.0.1, which resolves to the iPad itself -- API calls would break.
#     Leave them unset so the Vite proxy forwards /api requests server-side
#     to 127.0.0.1:<BackendPort> on the host PC.
#   - --host 0.0.0.0 makes Vite reachable on the local LAN only.
#     Use for local device testing. Stop the server when done.
#     Never expose this on a public or untrusted network.
#   - No broker connection, no live trading, no order execution.
#
# USAGE
#   .\scripts\devices\start_frontend_lan.ps1
#   .\scripts\devices\start_frontend_lan.ps1 -BackendPort 8001 -FrontendPort 5173
#
# PREREQUISITES
#   1. Backend is running: .\scripts\start_backend_local.ps1
#   2. iPad and PC are on the same LAN or connected via Tailscale.
#   3. Windows Firewall allows inbound TCP on port 5173 (private networks).
#      See docs/devices/ipad_pwa_smoke_test.md for firewall instructions.

param(
    [string]$BackendPort  = "8001",
    [string]$FrontendPort = "5173"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Resolve paths relative to this script's location (scripts/devices/ -> repo root)
$RepoRoot    = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$FrontendRoot = Join-Path $RepoRoot "frontend"

if (-not (Test-Path (Join-Path $FrontendRoot "package.json"))) {
    throw "frontend/package.json not found. Expected repo root at: $RepoRoot"
}

# Try to detect the primary LAN IP for display purposes (IPv4, non-loopback)
$LanIp = try {
    $addr = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown" } |
        Sort-Object InterfaceIndex |
        Select-Object -First 1
    if ($addr) { $addr.IPAddress } else { "<your-pc-lan-ip>" }
} catch {
    "<your-pc-lan-ip>"
}

Set-Location $FrontendRoot

if (-not (Test-Path (Join-Path $FrontendRoot "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    npm install
} else {
    Write-Host "Frontend dependencies already installed."
}

Write-Host ""
Write-Host "======================================================"
Write-Host "  MellyTrade LAN Frontend -- READ-ONLY / DRY-RUN"
Write-Host "======================================================"
Write-Host "  SAFETY: autotrade=false   dry_run=true"
Write-Host "  SAFETY: live_orders_blocked=true   read_only=true"
Write-Host "  SAFETY: no execution buttons   no order routes"
Write-Host "  SAFETY: local LAN / Tailscale only -- not public"
Write-Host ""
Write-Host "  Local (PC):  http://127.0.0.1:$FrontendPort"
Write-Host "  LAN (iPad):  http://${LanIp}:$FrontendPort  <-- open on iPad"
Write-Host "  Terminal:    http://${LanIp}:$FrontendPort/terminal"
Write-Host ""
Write-Host "  API proxy:   /api --> 127.0.0.1:$BackendPort (server-side)"
Write-Host "  Backend:     run .\scripts\start_backend_local.ps1 first"
Write-Host ""
Write-Host "  WARNING: --host 0.0.0.0 binds to all local interfaces."
Write-Host "  Use for local device testing only. Stop when done (Ctrl+C)."
Write-Host "======================================================"
Write-Host ""

npm run dev -- --host 0.0.0.0 --port $FrontendPort
