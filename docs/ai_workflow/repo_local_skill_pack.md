# Repo-Local Skill Pack

This pack documents small reusable instruction modules stored under
`skills/*/SKILL.md`.

## Purpose

- Keep repeated AI instructions in repo-local files.
- Make planning, implementation, review, frontend smoke checks, publish gates,
  cleanup gates, and Context7 lookup repeatable.
- Keep the instructions readable from the repository without relying on any
  global skill installation.

These skills are development-time instructions only.

They must not be used to:

- execute trades
- place orders
- modify broker execution
- connect live
- change risk settings
- expose secrets

These files are repo-local reusable instructions. Tool-specific installation may
require manual configuration outside git.

## Skill catalog

| Skill path | Use when |
|---|---|
| `skills/mellytrade-planning/SKILL.md` | Planning and scoping a task |
| `skills/mellytrade-safe-implementation/SKILL.md` | Making a small safe patch |
| `skills/mellytrade-safety-review/SKILL.md` | Reviewing diffs for safety drift |
| `skills/mellytrade-frontend-smoke/SKILL.md` | Verifying frontend changes in a browser |
| `skills/mellytrade-publish-gate/SKILL.md` | Pushing a branch and opening a draft PR |
| `skills/mellytrade-cleanup-gate/SKILL.md` | Cleaning up after merge while preserving WIP |
| `skills/mellytrade-context7-docs/SKILL.md` | Looking up current docs before coding |

## Usage notes

- **Claude Code**: reference the matching skill before each task to keep the
  agent focused.
- **Codex**: use the skill as a compact instruction module for scoped work.
- **OpenCode**: load the skill content into the local shell workflow as needed.
- **VS Code / Cursor style workflows**: use the skill as a checklist or pasted
  instruction block for the current task.

## Safety reminder

These skills do not grant permission to modify trading execution, broker
execution, live trading, or risk posture.
