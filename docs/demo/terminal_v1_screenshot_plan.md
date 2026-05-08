# MellyTrade Terminal V1 — Screenshot Plan

A specification for the portfolio / demo screenshot set that accompanies
Terminal V1. This document **defines what to capture** and **why each
capture matters**; it does not commit any actual image files. Real
captures are added later, under `docs/assets/terminal-v1/`, only when
they are taken from the running application.

---

## Purpose

Terminal V1 is a read-only, dry-run trading dashboard prototype. A
small, deliberate screenshot set lets reviewers, recruiters, and
portfolio visitors evaluate the work without running the stack
themselves. This plan locks down which views to capture, which safety
proof must be visible in each one, and where the resulting files will
live so the README and the local-demo runbook can link to them
consistently.

The plan is intentionally **modest**: six screenshots, one
walk-through, no marketing fluff. Each capture either demonstrates a
feature shipped in PR #55 or proves the safety posture is enforced.

---

## Safety Context

Every screenshot in this set must be captured on a build that satisfies
the Terminal V1 safety contract:

- **Read-only** dashboard surface (no mutating UI controls).
- **Dry-run** mode (`autotrade.dry_run = true`).
- **No live trading** — `autotrade.enabled = false`.
- **No order buttons** anywhere in any captured view.
- **No execution routes** exposed in the navigation or DOM.
- **No broker write paths** reachable from the captured UI.
- **Max risk per trade ≤ 1%**, surfaced by the safety banner.

If a future change makes any of the above untrue, the corresponding
screenshot **must not be re-captured** until the contract is restored.
The screenshots are evidence of posture; do not retouch or stage them
to misrepresent state.

---

## Screenshot Set

| ID | Screenshot | What to capture | Why it matters | Required visible safety proof | Suggested filename |
|---:|---|---|---|---|---|
| 1 | Dashboard with safety banner | The full Dashboard page with the persistent safety banner pinned to the top. Both the safety pills and the first row of dashboard cards must be visible in one frame. | Single most informative reviewer view. Demonstrates the safety-first posture *as the first thing a user sees*. | All four pills green: `DRY RUN`, `READ-ONLY MODE`, `LIVE ORDERS BLOCKED`, `MAX RISK ≤ N.N%`. | `terminal-dashboard-safety-banner.png` |
| 2 | Audit feed with safety notes | Audit Trail page (or the Dashboard "Audit Events" card), filtered or scrolled so at least one `safety`-severity event with a populated `safety_note` is visible. | Demonstrates Task 2: structured audit output with explicit safety explanations, not just opaque event slugs. | At least one row showing `severity: safety` plus a non-empty `safety_note`; e.g. the `live_orders_blocked` event. | `terminal-audit-feed-safety-notes.png` |
| 3 | Daily Trading Plan Preview | The Daily Trading Plan card on the Dashboard with its full content visible: header tags, label line, and at least three plan rows (instrument, bias, setup quality, risk tier, no-trade condition). | Demonstrates Task 4: a planning surface that *cannot* be confused for an order ticket. Showcases the read-only label clearly. | Both card tags visible: `READ-ONLY PLAN PREVIEW` and `NO ORDERS PLACED`; meta line `Max risk per trade ≤ 1.0%`; at least one `no-trade` line per visible row. | `terminal-daily-plan-preview.png` |
| 4 | Resource states (loading / empty / degraded / last-updated) | A composite or single capture showing at least one of the non-ready states from the shared `ResourceState` shell. The most reproducible state is **degraded** — stop the backend, refresh the page, capture the red "Backend unavailable" card. | Demonstrates Task 1: graceful read-only degradation. Reviewers see the system fails *informatively* rather than silently. | The "Backend unavailable" message and the `Last successful update at HH:MM:SS` footer; the safety banner must remain pinned and is acceptable in either green or muted state. | `terminal-resource-states.png` |
| 5 | Safety regression tests passing | Terminal output of `py -3.11 -m pytest tests/app/test_safety_invariants.py -q` showing the green `passed` summary. Capture the prompt and the output together. | Demonstrates Task 3: the read-only / dry-run posture is enforced by an executable test, not just by code review. | The full command as run, plus a `passed` count of at least 39 (the count introduced in commit `78c4281`). | `terminal-safety-tests-passing.png` |
| 6 | Frontend production build passing | Terminal output of `cd frontend && npm run build` showing the Vite "built in …" line and the bundle size summary. | Demonstrates the frontend type-checks and builds cleanly with the Terminal V1 changes applied. | The `tsc -b && vite build` invocation visible; the `built in` line; no `error TS` lines anywhere in the capture. | `terminal-build-passing.png` |

---

## How to Capture

A clean capture flow that any reviewer can reproduce on a Windows
workstation. Tools: built-in **Snipping Tool** (`Win+Shift+S`) for app
captures, plus a regular terminal capture for the build/test ones.

### 1. Start the backend

From the repository root:

```powershell
py -3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Wait for `Application startup complete.` Leave the terminal running.

### 2. Start the frontend

In a second terminal, also from the repository root:

```powershell
cd frontend
npm install        # first run only; on subsequent runs prefer `npm ci`
npm run dev
```

### 3. Open the app in the browser

```text
http://127.0.0.1:5173
```

Wait for the safety banner to turn fully green before capturing
anything.

### 4. Capture the application screenshots (1–4)

- **Screenshot 1** — Dashboard at default scroll position. Capture the
  top of the page so the safety banner is included.
- **Screenshot 2** — Open `Audit Trail` in the sidebar. Filter by
  severity `safety` (or scroll until a `safety_note` is visible).
- **Screenshot 3** — Return to `Dashboard`. Scroll to the "Daily
  Trading Plan Preview" card. Capture the card framed cleanly with both
  tags visible.
- **Screenshot 4** — Switch back to the backend terminal and press
  `Ctrl+C` to stop Uvicorn. In the browser, open `Positions` and
  refresh; capture the red "Backend unavailable" state. Restart Uvicorn
  afterwards to clean up.

### 5. Capture the validation screenshots (5–6)

These are terminal-only. Pick a wide terminal so the full output fits.

```powershell
# Screenshot 5
py -3.11 -m pytest tests/app/test_safety_invariants.py -q

# Screenshot 6
cd frontend
npm run build
```

After the command finishes, capture the visible terminal output
including the prompt line above it.

---

## Recommended Asset Path

Real captures should be placed under:

```text
docs/assets/terminal-v1/
```

with the following exact filenames so future references in `README.md`
and `docs/demo/terminal_v1_local_demo.md` resolve cleanly:

- `terminal-dashboard-safety-banner.png`
- `terminal-audit-feed-safety-notes.png`
- `terminal-daily-plan-preview.png`
- `terminal-resource-states.png`
- `terminal-safety-tests-passing.png`
- `terminal-build-passing.png`

> **No binary image files are committed by this plan.** The directory
> and the files above are reserved names for a future, separate commit
> that adds the real captures.

Recommended capture format: `.png` for crisp screenshots; keep each
file under ~300 KB by saving at viewport size rather than full screen.
Avoid lossy `.jpg` for UI captures — small text degrades.

---

## README Integration Plan

Once the real screenshots exist under `docs/assets/terminal-v1/`, the
top-level `README.md` and `docs/demo/terminal_v1_local_demo.md` can be
extended with markdown image references that look like:

```markdown
![MellyTrade Terminal V1 dashboard](docs/assets/terminal-v1/terminal-dashboard-safety-banner.png)
```

Recommended placement:

- One **hero image** (`#1` from the table above) near the top of
  `README.md`, just under the "MellyTrade Terminal V1" heading.
- The five remaining captures linked from the `Screenshot Checklist`
  section of the local demo runbook (`docs/demo/terminal_v1_local_demo.md`).

The README is intentionally **not** edited by this plan: it is a
docs-only preparatory step. README integration happens in a separate,
small follow-up PR that lands together with the actual `.png` files.

---

## Acceptance Criteria

A reviewer should be able to confirm all of the following before this
document is considered complete:

- [ ] This screenshot plan exists at `docs/demo/terminal_v1_screenshot_plan.md`.
- [ ] No fake / staged / mocked screenshots have been committed.
- [ ] No binary image assets have been committed by *this* PR.
- [ ] No secrets, credentials, account IDs, or broker tokens appear in
      the document.
- [ ] No live-trading instructions appear anywhere in the capture flow.
- [ ] Every screenshot description reinforces the read-only / dry-run
      posture (either by the safety banner being visible, or by
      capturing a known safety-severity audit event, or by passing tests
      that enforce the posture).
- [ ] The recommended filename set matches exactly what the future
      README integration commit will reference.

---

**Last updated**: 2026-05-08
