# Start the local free-claude-code proxy on 127.0.0.1:8082.
#
# Safety:
#   - This script does NOT read or store secrets.
#   - It does NOT enable live trading or touch the MellyTrade backend.
#   - Real API keys (OpenRouter, etc.) must be exported in your shell *before*
#     calling this script. See docs/dev/free_claude_code.env.example.

$ErrorActionPreference = "Stop"

$ProxyRoot = "C:\AI\free-claude-code"
$Host_     = "127.0.0.1"
$Port      = 8082

if (-not (Test-Path $ProxyRoot)) {
    Write-Host "ERROR: free-claude-code not found at $ProxyRoot" -ForegroundColor Red
    Write-Host "Clone it first, e.g.:"
    Write-Host "  git clone <repo-url> $ProxyRoot"
    exit 1
}

Set-Location $ProxyRoot
Write-Host "Proxy root: $ProxyRoot"

$venvActivate = Join-Path $ProxyRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtualenv: $venvActivate"
    . $venvActivate
} else {
    Write-Host "No .venv found; using the current Python interpreter."
}

Write-Host ""
Write-Host "Starting uvicorn server:app on http://${Host_}:${Port} ..."
Write-Host "Press Ctrl+C to stop."
Write-Host ""
Write-Host "After the proxy is up, in a NEW PowerShell window run:" -ForegroundColor Cyan
Write-Host '  $env:ANTHROPIC_AUTH_TOKEN = "freecc"' -ForegroundColor Cyan
Write-Host '  $env:ANTHROPIC_BASE_URL   = "http://127.0.0.1:8082"' -ForegroundColor Cyan
Write-Host '  $env:CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY = "1"' -ForegroundColor Cyan
Write-Host '  $env:MODEL = "open_router/deepseek/deepseek-r1-0528:free"' -ForegroundColor Cyan
Write-Host '  $env:ALLOWED_DIR = "C:/AI/MellyTrade_Workspace/02_Repo"' -ForegroundColor Cyan
Write-Host '  # Optional: $env:OPENROUTER_API_KEY = "<your key>"' -ForegroundColor Cyan
Write-Host '  claude' -ForegroundColor Cyan
Write-Host ""

python -m uvicorn server:app --host $Host_ --port $Port
