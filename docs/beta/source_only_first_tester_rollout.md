# Source-Only First Tester Rollout

> Planning document only. Does not implement any installer, package, or
> distribution artifact. Does not change runtime behaviour or safety posture.

---

## Purpose

Prepare a safe first trusted-tester rollout using source-only GitHub repository
access.

This replaces the release-ZIP model for the initial source cohort. No pre-built
EXE, installer, or ZIP is shared. The tester clones the repository and builds
the launcher locally.

---

## Scope

This rollout shares repository access and instructions only.

It does not share:

- generated EXE
- ZIP bundle
- MSI installer
- final installer
- code-signed application
- auto-updater
- live trading access
- broker execution access
- broker credentials
- secrets
- API keys
- MT5 account IDs or login details
- Supabase service role keys
- investment advice
- guaranteed profit claims

---

## Safety posture

Every session must run with:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

The safety banner is printed at every launcher start. If the tester does not see
it, they must stop and report.

---

## Tester selection

Invite only 1 trusted tester first.

The tester should be able to:

- follow written setup steps
- run PowerShell commands
- report screenshots and error messages
- understand this is a read-only dry-run demo
- avoid entering credentials
- stop and report if safety banner is missing
- stop and report if order or execution controls appear

Do not invite yet:

- public users
- paid subscribers
- users expecting live trading
- users expecting financial advice
- anyone who may treat demo signals as trade instructions

---

## Operator preflight

Before granting access, run the full preflight gate:

```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app/test_source_only_beta_docs_static.py tests/app/test_source_only_beta_rollout_docs_static.py tests/app/test_desktop_distribution_docs_static.py tests/app/test_desktop_launcher_static.py tests/app/test_desktop_launcher_build_static.py tests/app/test_desktop_launcher_runtime_smoke_static.py tests/app/test_desktop_launcher_shortcut_static.py -q
py -3.11 -m pytest tests/app/test_safety_invariants.py tests/app/test_openapi_forbidden_paths.py -q
git status --short dist build
git status --short *.spec
git status --short *.exe
git status --short *.lnk
git status --short *.msi
git status --short *.zip
```

Required before proceeding:

- safety validator PASS
- all tests PASS
- no generated artifacts staged or committed
- no secrets in repository
- no broker credentials in repository
- no live trading enabled
- no execution controls exposed

---

## GitHub access model

Use read-only repository access only.

Do not grant:

- admin access
- maintain access
- write access
- secrets access
- deployment access
- GitHub Actions secret access

---

## What to send

Send to tester:

- source access guide: `docs/product/beta_tester_source_access_guide.md`
- desktop launcher quick start: `docs/product/beta_tester_desktop_launcher_quick_start.md`
- distribution notes: `docs/product/beta_tester_desktop_distribution_notes.md`
- feedback form: `docs/beta/source_only_tester_feedback_form.md`
- invite message: `docs/beta/source_only_tester_invite_message.md`
- stop and report conditions (summarised in source access guide)

Do not send:

- `.env` files or secrets
- broker credentials of any kind
- MT5 login details
- API keys
- account IDs
- Supabase service role keys
- generated EXE files
- generated ZIP bundles
- generated MSI/installer artifacts
- investment advice claims
- guaranteed profit claims

---

## Rollout steps

Perform each step manually:

1. Run full preflight gate (`docs/qa/source_only_beta_rollout_gate.md`). Gate must PASS.
2. Choose 1 trusted tester.
3. Grant read-only GitHub repository access manually via GitHub settings.
4. Send invite message manually (use `docs/beta/source_only_tester_invite_message.md`).
5. Ask tester to follow `docs/product/beta_tester_source_access_guide.md`.
6. Ask tester to report feedback using `docs/beta/source_only_tester_feedback_form.md`.
7. Review feedback before inviting anyone else.

---

## Stop conditions

Stop rollout immediately if tester reports:

- safety banner missing at launch
- `autotrade=true` in banner
- `dry_run=false` in banner
- `read_only=false` in banner
- `live_orders_blocked=false` in banner
- app asks for broker credentials
- app asks for secrets or API keys
- order or execution controls visible
- investment-advice-like copy in UI
- guaranteed-profit-like copy in UI
- generated artifact was accidentally shared or committed
- app connects to any address outside `localhost`

If any stop condition occurs:

- halt rollout immediately
- do not invite additional testers
- resolve the issue
- re-run full preflight gate before resuming

---

## Expansion rule

Do not invite a second tester until:

- first tester feedback has been reviewed
- all P0 issues resolved or explicitly accepted with documented rationale
- all P1 issues resolved or deferred with documented plan
- safety posture re-verified (safety validator and tests PASS)
- no new execution-like controls introduced

---

## Related docs

- `docs/distribution/source_only_beta_package_review.md` - safe sharing model
- `docs/qa/source_only_beta_preflight_checklist.md` - operator preflight checklist
- `docs/qa/source_only_beta_rollout_gate.md` - rollout gate
- `docs/product/beta_tester_source_access_guide.md` - tester-facing guide
- `docs/product/beta_tester_desktop_launcher_quick_start.md` - launcher quick start
- `docs/beta/source_only_tester_invite_message.md` - invite message templates
- `docs/beta/source_only_tester_feedback_form.md` - feedback form
- `docs/tasks/desktop_launcher_exe_plan.md` - DESKTOP-001 plan and BETA-ACCESS-001 status

---

*MellyTrade BETA-ACCESS-001 - Source-Only First Tester Rollout - local-only, read-only, advisory.*
