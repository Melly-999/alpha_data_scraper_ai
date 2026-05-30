#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

files=(
  ".coderabbit.yaml"
  "docker-compose.observability.yml"
  ".env.observability.example"
  ".mcp.example.json"
  "docs/observability/datadog_setup.md"
  "docs/dev/claude_code_connectors.md"
  "docs/dev/oh_my_claudecode_setup.md"
)

failures=()

for file in "${files[@]}"; do
  if [[ ! -f "$repo_root/$file" ]]; then
    failures+=("Missing file: $file")
  fi
done

unsafe_flags=(
  "autotrade=true"
  "dry_run=false"
  "read_only=false"
  "live_orders_blocked=false"
  "execution_enabled=true"
)

sensitive_terms=(
  "MT5_LOGIN"
  "MT5_PASSWORD"
  "IBKR"
  "XTB"
  "broker_order_id"
  "account_id"
)

for file in "${files[@]}"; do
  path="$repo_root/$file"
  [[ -f "$path" ]] || continue

  if [[ "$file" != docs/* && "$file" != ".coderabbit.yaml" ]]; then
    for flag in "${unsafe_flags[@]}"; do
      if grep -Fq "$flag" "$path"; then
        failures+=("Unsafe flag found in $file: $flag")
      fi
    done
  fi

  if [[ "$file" == ".env.observability.example" ]]; then
    if ! grep -Fqx 'DD_API_KEY=replace_with_datadog_api_key' "$path"; then
      failures+=("Placeholder DD_API_KEY line is missing or modified in $file")
    fi
    if grep -Eq '^DD_API_KEY=' "$path" && ! grep -Fqx 'DD_API_KEY=replace_with_datadog_api_key' "$path"; then
      failures+=("Non-placeholder DD_API_KEY value detected in $file")
    fi
  fi

  if [[ "$file" != docs/* ]]; then
    for term in "${sensitive_terms[@]}"; do
      if grep -Fq "$term" "$path"; then
        failures+=("Sensitive broker term found in $file: $term")
      fi
    done
  fi
done

if [[ "${#failures[@]}" -gt 0 ]]; then
  echo "FAIL"
  printf '%s\n' "${failures[@]}"
  exit 1
fi

echo "PASS"
echo "Validated files: ${#files[@]}"
