# Mobile AI Claude Provider (MOBILE-AI-008C)

**Type:** backend AI provider integration — **default-disabled**

Implements the optional real `claude` provider from the MOBILE-AI-008A contract
(`docs/mobile/mobile_ai_provider_integration_contract.md`), behind the existing
analysis-only screenshot endpoint (`POST /api/mobile/ai/screenshot/preview`).

## Enablement (all three required)

- `MOBILE_AI_PROVIDER=claude`
- `MOBILE_AI_PROVIDER_ENABLED=true`
- `ANTHROPIC_API_KEY` present (backend env only; **never** in the frontend)

Optional: `CLAUDE_MOBILE_AI_MODEL` (defaults to a current Claude model).

If any condition is unmet, or the SDK/key is unavailable, or the call errors,
the service **degrades to the deterministic stub** — the endpoint never fails
and never surfaces provider/key details.

## Safety guarantees (enforced in code, not by the model)

- The model may only fill **descriptive** chart-review fields (bias, trend,
  momentum, volatility, pattern, key levels, checklist). It can never set risk
  numbers, the paper plan, or any safety flag.
- Risk and the paper plan come from the deterministic scaffold; risk ≤ 1%.
- The response stays the Literal-locked `ScreenshotAnalysisPreview`:
  `analysis_only=true`, `paper_only=true`, `live_orders_blocked=true`,
  `broker_execution=false`, `requires_human_review=true`, `stored=false`.
  Only `provider_used` flips to `true` when the real provider ran.
- The image is sent to Anthropic for analysis only; it is **not stored** and
  **not logged** (only size/MIME used locally). No broker, order, wallet, or
  execution surface exists.

## Privacy

Enabling this provider sends uploaded screenshots to Anthropic. Review the
provider's data-use policy and
`docs/mobile/mobile_ai_image_privacy_retention_policy.md` first. Do not enable
in environments where users may upload screenshots containing account numbers,
API keys, or other secrets.

## Files

- `app/services/mobile_ai_claude_provider.py` — `ClaudeProvider` (lazy-imports
  `anthropic`; already a project dependency, so no new dependency is added).
- `app/services/mobile_ai_provider.py` — `select_provider()` gates the provider
  behind the enabled flag + key.
- `app/schemas/mobile_ai.py` — `provider_used` relaxed from `Literal[False]`
  to `bool` (informational; still defaults `False`).
- `tests/app/test_mobile_ai_claude_provider.py` — SDK mocked; no network call.

## Testing

Tests mock `ClaudeProvider._call_model`, so no real Anthropic call is made in
CI and no key is required to run them. The default (disabled) path keeps the
deterministic mock and never imports the SDK.
