# DEMO-009 — iPad / PWA Screenshot Checklist

## Purpose

Use this checklist to capture proof for the successful MellyTrade iPad / PWA smoke test.

This is a text checklist only. It does not include or require binary image assets.

## Required Capture Set

- [ ] iPad Safari URL loaded
- [ ] Paper Run Preview panel visible
- [ ] Safety chips visible
- [ ] Text / number input focus with no zoom
- [ ] Side select focused or open with no zoom
- [ ] Load Preview or Refresh Preview visible and usable
- [ ] Add to Home Screen flow visible
- [ ] Standalone PWA home screen icon visible
- [ ] Standalone PWA launch visible without Safari chrome

## Optional Supporting Captures

- [ ] Allowed preview result
- [ ] Blocked preview result
- [ ] Terminal / workspace overview
- [ ] Safety posture indicators
- [ ] Empty or degraded preview state, if applicable

## Suggested Capture Notes

- Use the direct `Paper Run Preview` URL on iPad Safari or in the installed PWA.
- Capture the `Side` select specifically to document the no-zoom behavior.
- Keep the backend out of scope in screenshots; it must remain loopback-only.
- Keep the narrative read-only and demo-safe.

## Safety Reminder

The screenshot set must not imply:

- live trading
- broker execution
- order placement
- guaranteed profit
- secret or account disclosure
- public backend exposure

## Evidence Labeling

Recommended naming pattern:

- `demo_009_01_ipad_safari_url.png`
- `demo_009_02_paper_run_preview_panel.png`
- `demo_009_03_safety_chips.png`
- `demo_009_04_input_focus_no_zoom.png`
- `demo_009_05_side_select_no_zoom.png`
- `demo_009_06_add_to_home_screen.png`
- `demo_009_07_standalone_pwa_icon.png`
- `demo_009_08_standalone_pwa_launch.png`

## Reviewer Use

This checklist is safe to attach to an internal demo review, portfolio review, or QA handoff as long as it remains text-only and read-only in scope.
