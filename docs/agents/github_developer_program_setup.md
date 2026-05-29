# GitHub Developer Program + GitHub App Setup — MellyTrade

> **Docs-only.** No private keys, tokens, or secrets are stored in this repo.
> This describes *how* to register a read-only GitHub App for MellyTrade agents.
> Safety posture unchanged: `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, `execution_enabled=false`, `max_risk_per_trade <= 1%`.

---

## 1. What the GitHub Developer Program is

The **GitHub Developer Program** is a free membership for developers building
on GitHub's APIs and platform (GitHub Apps, OAuth apps, Actions, webhooks). It
provides developer-focused resources, early access notes, and a place to
register integrations. Membership itself grants **no special repo permissions**
— access is always defined by the App/OAuth scopes you configure.

For MellyTrade we join the Developer Program purely to build and register a
**read-only GitHub App** that agents (Repo Captain, CI Doctor, Safety Reviewer)
use to *observe* repo state — never to merge, push, or trade.

## 2. Program / plan comparison

| Offering | What it is | Gives repo write/exec? | Use for MellyTrade |
|---|---|---|---|
| **GitHub Developer Program** | Membership for API/integration builders. | No (membership only). | Register the read-only App. |
| **GitHub App** | A first-class integration identity with **fine-grained, per-resource permissions** and its own installation token. | Only what you grant. | **Primary** — read-only agent access. |
| **GitHub Pro** | Paid personal plan (more Actions minutes, advanced features on private repos). | No new API powers. | Optional; not required for agents. |
| **GitHub Education** | Free Pro-tier benefits + partner credits for verified students/teachers. | No new API powers. | Optional eligibility benefit only. |

> Key point: **permissions come from the App configuration**, not from which
> program/plan you belong to. We keep the App read-only regardless of plan.

## 3. Recommended GitHub App permissions (read-only baseline)

| Resource | Access | Why |
|---|---|---|
| **Contents** | **Read** | Read files/diffs for review (no write). |
| **Pull requests** | **Read** | List PRs, read titles/state/diff metadata. |
| **Checks** | **Read** | Read CI check rollups for the CI Doctor. |
| **Metadata** | **Read** (mandatory) | Baseline repo metadata; required by GitHub. |
| **Issues** | **Read** (Read/Write *optional*, later) | Read for triage; write only if/when issue-creation is approved (Phase 5). |
| **Workflows** | **No access** | Never modify CI/CD from an agent. |
| **Secrets** | **No access** | Agents must never read or set secrets. |
| **Administration** | **No access** | No repo/org admin powers. |
| **Actions** | **No access** | No triggering/cancelling runs. |
| **Deployments / Environments** | **No access** | No deploy control. |

Subscribe webhooks to **read-oriented events** only: `pull_request`,
`check_suite`, `check_run`, `issues` (if Issues read enabled). Do **not**
subscribe to or act on `push`-to-`main` with any write intent.

## 4. Webhook safety

- **Use a webhook secret.** Configure a strong secret in the App settings;
  store it in the deployment environment's secret manager — **never in this
  repo**.
- **Verify signatures.** Validate the `X-Hub-Signature-256` HMAC on every
  delivery before processing. Reject unsigned or mismatched payloads.
- **Never commit the App private key.** The `.pem` key lives only in the secret
  manager / local OS keystore. It must never appear in git history, env files
  committed to the repo, or logs.
- **Store all secrets outside the repo.** Webhook secret, App ID, installation
  ID, and private key belong in the host's secret store (e.g. platform env vars
  / vault), not in `.env` files that are tracked.
- **Least privilege + short-lived tokens.** Use installation access tokens
  (auto-expiring) minted from the private key at runtime; never long-lived PATs.
- **Audit + rotate.** Log webhook receipts (without payload secrets) and rotate
  the webhook secret / private key on any suspicion of exposure.

## 5. Explicitly out of scope

- No write permissions in the baseline (Contents/PRs/Checks are **Read**).
- No `Workflows`, `Secrets`, `Administration`, `Actions`, or `Deployments`.
- No ability to merge, push to `main`, enable live trading, or place orders —
  those are not GitHub permissions and are forbidden by the MellyTrade safety
  contract regardless.

## 6. Registration checklist (no secrets committed)

1. Join the GitHub Developer Program (account-level, free).
2. Create a **GitHub App** (org or user owned) with the §3 read-only scopes.
3. Generate a private key → store in the secret manager (not the repo).
4. Set a webhook URL + webhook secret (secret in secret manager).
5. Install the App on `Melly-999/alpha_data_scraper_ai` only.
6. Record **non-secret** identifiers (App slug, public App ID) in deployment
   config outside the repo. Never record the private key or webhook secret here.
