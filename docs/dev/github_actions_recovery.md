# MellyTrade — GitHub Actions Recovery Checklist

A practical, self-contained checklist for diagnosing and fixing the
"Actions has been disabled" error currently affecting this repo.

---

## Known error

```
$ gh workflow run pytest.yml --ref feature/safety-status-contract
could not create workflow dispatch event:
HTTP 422: Actions has been disabled for this user.
(https://api.github.com/repos/Melly-999/alpha_data_scraper_ai/actions/workflows/<id>/dispatches)
```

```
$ gh pr checks 57
no checks reported on the 'feature/safety-status-contract' branch
```

This is **not** a bug in any workflow YAML. The block is at the
account/billing/repo policy layer, *upstream* of the workflow files.

---

## Important distinction: workflow active ≠ Actions allowed

GitHub has three layers of "is this workflow allowed to run?":

| Layer | Check | Where to fix |
|---|---|---|
| **Per-workflow toggle** | `gh workflow list` shows the workflow as `active` | The YAML file itself, or `gh workflow enable <name>` |
| **Repo-level Actions permission** | Repo `Settings → Actions → General → Actions permissions` | Repository owner, in the GitHub UI |
| **Account / org-level Actions allowance** | Account `Settings → Actions` and `Settings → Billing` | Account owner, in the GitHub UI |

**Right now, all our workflows show as `active` in `gh workflow list`,
but every dispatch returns 422.** That points to layer 2 or layer 3,
*not* layer 1. **Do not edit the YAML files** to "fix" this — it
won't help, and it risks breaking things once the upstream block is
lifted.

---

## Layer-by-layer recovery checklist

Work through these in order. Stop as soon as the dispatch attempt
succeeds.

### 1. Repo-level Actions permissions

1. Open `https://github.com/Melly-999/alpha_data_scraper_ai/settings/actions`.
2. Under **Actions permissions**, confirm one of:
   - "Allow all actions and reusable workflows" — preferred.
   - "Allow `Melly-999`, and select non-`Melly-999`, actions and reusable workflows" — fine if you want to scope to vetted publishers.
3. **Do not** select "Disable actions" or "Allow `Melly-999` actions only" — both can produce the 422 we're seeing.
4. Save. Then re-try `gh workflow run`.

### 2. Account-level Actions allowance

The 422 message specifically says *"disabled for this user"*, which
makes layer 3 the most likely culprit.

1. Open `https://github.com/settings/actions`.
2. Confirm Actions are not globally disabled on your account.
3. If you see "Actions are currently disabled on your account", look
   for the reason banner. Common causes:
   - Spending limit hit (see step 3 below).
   - Account flagged or restricted (rare; contact GitHub support).
   - Organization policy override (if your account belongs to an org).

### 3. Billing & spending limit

This is the most common silent cause of "disabled for this user".

1. Open `https://github.com/settings/billing/spending_limit`.
2. Confirm your **GitHub Actions spending limit** is **not** `$0` if you
   run any workflows on private repos or any workflow that consumes
   non-included minutes.
3. Open `https://github.com/settings/billing` and verify a payment
   method is on file.
4. Open `https://github.com/settings/billing/summary` and check the
   **Actions minutes used** vs **included minutes** for the current
   billing cycle. If you've exhausted the included minutes and the
   spending limit is `$0`, Actions are paused until next cycle.
5. Set a non-zero spending limit if you need workflows to run for the
   rest of the cycle.

### 4. Org-level policy (if applicable)

If `Melly-999` belongs to an organization:

1. Open the org's `Settings → Actions → General`.
2. Verify the org-level Actions permissions allow your repos to run
   workflows.
3. Check **Policies → Workflow permissions** — sometimes set to
   "Read repository contents permission" only, which blocks `gh pr
   ready` from triggering re-runs.
4. If you don't admin the org, ask the org owner.

### 5. Two-factor / re-auth

Occasionally a recently-rotated PAT or cookie expires while
`gh` keeps working for read calls but fails on dispatch.

```powershell
gh auth status
gh auth refresh -s repo,workflow
```

If `gh auth status` doesn't list `workflow` in the scopes, refresh.

---

## How to verify the recovery

Once you believe the block is lifted, verify in this order. Each step
should produce more information than the previous one.

### Step A — confirm `gh` can list workflows

```powershell
gh workflow list
```

Expected: a non-empty list. (We've already confirmed this works
before — it should still work after recovery.)

### Step B — dispatch the safety regression workflow

```powershell
gh workflow run pytest.yml --ref feature/safety-status-contract
```

Expected: empty output, exit code 0. **Not** the 422 error.

### Step C — confirm a run was created

```powershell
gh run list --branch feature/safety-status-contract --limit 5
```

Expected: a row marked `queued` or `in_progress` for `Pytest CI`.

### Step D — wait and watch the run

```powershell
gh run watch
```

Or, for a specific run id:

```powershell
gh run view <run-id> --log-failed
```

Expected: green tick once tests finish (or red, in which case fix the
test and don't blame the recovery).

### Step E — confirm checks now show on the PR

```powershell
gh pr checks 57
gh pr checks 56
```

Expected: pending or completed checks per workflow, no longer
"no checks reported on the branch".

### Step F — re-run any open PR's checks

If a PR was opened *during* the outage, no workflow ever ran on it. To
trigger a fresh run after recovery:

```powershell
# Either dispatch via workflow_dispatch:
gh workflow run pytest.yml --ref <branch>

# Or push an empty commit to nudge pull_request triggers:
git switch <branch>
git commit --allow-empty -m "ci: re-trigger after Actions recovery"
git push
```

Prefer the first approach (no extra commit).

---

## What NOT to do

These are tempting but wrong. Don't:

- ❌ **Edit `.github/workflows/*.yml`** to "fix" the dispatch failure.
  The YAML is fine. The block is upstream.
- ❌ **Remove `pull_request:` triggers** to "make CI quieter" while
  Actions are off. They'll do nothing now and produce nothing useful
  when Actions return.
- ❌ **Bypass safety checks** because CI isn't ticking. The local
  validation comment is the substitute, not a permission to skip.
- ❌ **Merge a PR without local validation** because "CI is broken
  anyway". The validation comment must be present.
- ❌ **Force-push to `main`** to "fast-forward" past a missing CI
  check. Force-push to `main` is never authorised.
- ❌ **Disable failing tests** to "let CI go green" once Actions return.
  If a test is failing, fix the code or fix the test on its own merits.
- ❌ **Change billing limits beyond what you understand.** Set the
  smallest amount that lets your workflows run, not "uncapped".
- ❌ **Share a screenshot of the billing page** (it can include
  partial card info). Share `gh workflow list` output instead.

---

## Operating without CI in the meantime

While Actions remain disabled, every PR follows the same pattern:

1. Run **local validation**: `pytest tests/app/ -q` and `npm run build`.
2. Post a **validation comment** on the PR with the results (template
   in `docs/dev/ai_dev_workflow.md`, "What must always be included in
   the final PR comment").
3. Mark the PR ready for review.
4. The product owner reads the diff *and* the validation comment
   before merging.
5. After merge, re-run `pytest tests/app/ -q` on `main` locally to
   confirm the squash didn't break anything (rare but possible if `main`
   moved during the PR's life).

The validation comment is the single source of evidence until CI
returns. Take it seriously: include the test count, the warning
count, and the safety confirmation block verbatim.

---

## Long-term: prevent recurrence

Once Actions are back, take three small actions to make this less likely
to bite again:

1. **Set a non-zero spending limit** with a small monthly cap (e.g. `$5`)
   so a quota exhaustion stops the world but a cycle reset doesn't
   leave you blocked for days.
2. **Enable email notifications** for "Actions disabled" events on the
   account. GitHub usually sends one but the inbox filter may be
   eating it.
3. **Document credentials rotation** — if a PAT is involved anywhere,
   note the rotation date in the secrets inventory (planned in
   SEC-002).

---

**Last updated**: 2026-05-09
