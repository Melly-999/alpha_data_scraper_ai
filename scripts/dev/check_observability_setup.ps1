#!/usr/bin/env pwsh
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
  ".coderabbit.yaml",
  "docker-compose.observability.yml",
  ".env.observability.example",
  ".mcp.example.json",
  "docs/observability/datadog_setup.md",
  "docs/dev/claude_code_connectors.md",
  "docs/dev/oh_my_claudecode_setup.md"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $files) {
  $path = Join-Path $repoRoot $file
  if (-not (Test-Path -LiteralPath $path)) {
    $failures.Add("Missing file: $file")
  }
}

$unsafeFlags = @(
  "autotrade=true",
  "dry_run=false",
  "read_only=false",
  "live_orders_blocked=false",
  "execution_enabled=true"
)

$sensitiveTerms = @(
  "MT5_LOGIN",
  "MT5_PASSWORD",
  "IBKR",
  "XTB",
  "broker_order_id",
  "account_id"
)

foreach ($file in $files) {
  $path = Join-Path $repoRoot $file
  if (-not (Test-Path -LiteralPath $path)) {
    continue
  }

  $content = Get-Content -LiteralPath $path -Raw

  if ($file -notlike "docs/*" -and $file -ne ".coderabbit.yaml") {
    foreach ($flag in $unsafeFlags) {
      if ($content.Contains($flag)) {
        $failures.Add("Unsafe flag found in ${file}: $flag")
      }
    }
  }

  if ($file -eq ".env.observability.example") {
    if ($content -notmatch '(?m)^DD_API_KEY=replace_with_datadog_api_key$') {
      $failures.Add("Placeholder DD_API_KEY line is missing or modified in $file")
    }
    if ($content -match '(?m)^DD_API_KEY=(?!replace_with_datadog_api_key$).+$') {
      $failures.Add("Non-placeholder DD_API_KEY value detected in $file")
    }
  }

  if ($file -notlike "docs/*") {
    foreach ($term in $sensitiveTerms) {
      if ($content.Contains($term)) {
        $failures.Add("Sensitive broker term found in ${file}: $term")
      }
    }
  }
}

if ($failures.Count -gt 0) {
  Write-Host "FAIL"
  $failures | ForEach-Object { Write-Host $_ }
  exit 1
}

Write-Host "PASS"
Write-Host "Validated files: $($files.Count)"
