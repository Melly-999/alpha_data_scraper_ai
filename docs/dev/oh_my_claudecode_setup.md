# oh-my-claudecode Setup

oh-my-claudecode is a Claude Code plugin workflow for faster task framing, deeper interviews, validation loops, and multi-agent assistance. In MellyTrade it must stay aligned with the read-only, paper-trading posture.

## Safe Install Commands

```text
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
/oh-my-claudecode:omc-setup
```

If the plugin command style differs in your environment, use the fallback sequence:

```text
/plugin install oh-my-claudecode
/setup
/omc-setup
```

## Recommended Modes

- `/deep-interview` for requirements gathering
- `/team` for larger scoped tasks
- `/ralph` for bugfixes that should run to completion
- `/ultraqa` for validation loops
- `/ask codex` for a second-opinion review
- `/ask gemini` for UI and UX review

## MellyTrade Safety Warnings

- No autonomous live trading
- No direct push to main
- No secret access
- No broker credentials
- No order execution
- All trading actions stay read-only, paper, or dry-run

## Operating Rule

Use the plugin to improve review quality and iteration speed, not to bypass repository safety gates or trading controls.
