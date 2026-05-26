# AI Agent Lab Setup for MellyTrade

This document outlines the installation and safe usage of advanced AI coding tools in the MellyTrade environment.

## 1. OpenCode
- Status: DOCUMENT_ONLY until user approves
- What it does: An AI coding assistant integrated with VS Code for enhanced coding productivity.
- Use in: AI Agent Lab only
- Secrets: No tokens or keys in workspace or repo
- Installer: Must be reviewed before execution
- Do NOT run remote scripts blindly
- Use isolated branches or worktrees

## 2. OpenClaw
- Status: DOCUMENT_ONLY until user approves
- What it does: Command-line interactive AI coding agent
- Use in: AI Agent Lab only
- Secrets: No API keys or tokens stored
- Installer: Review before execution, no blind pipe
- Use isolated branches or worktrees

## 3. 9Router
- Status: DOCUMENT_ONLY until user approves
- What it does: AI multi-task routing service
- Use in: AI Agent Lab only
- Secrets: No tokens or keys
- Installer: Download and review before running
- Do NOT blindly pipe installers
- Use isolated branches or worktrees

## 4. free-claude-code
- Status: DOCUMENT_ONLY until user approves
- What it does: Alternative Claude coding assistant
- Use in: AI Agent Lab only
- Secrets: Strict no secrets in environment or prompts
- Installer: Manual review mandatory
- Use isolated branches or worktrees

## 5. ANUS CLI
- Status: DOCUMENT_ONLY until user approves
- What it does: AI command line utility for code generation
- Use in: AI Agent Lab only
- Secrets: No keys/token storage
- Installer: Follow official docs and review installers
- Use isolated branches or worktrees

## 6. OpenSquilla
- Status: DOCUMENT_ONLY until user approves
- What it does: AI-powered code analysis tool
- Use in: AI Agent Lab only
- Installer: Review before installation
- Secrets: No secrets in config

## 7. zerostack
- Status: DOCUMENT_ONLY until user approves
- What it does: Cloud-native AI orchestration framework
- Use in: AI Agent Lab only
- Installer: Review before installation
- Secrets: No secrets in repo

## 8. Terax AI
- Status: DOCUMENT_ONLY until user approves
- What it does: AI development platform
- Use in: AI Agent Lab only
- Installer: Review official installer
- Secrets: None stored

## 9. AIPointer
- Status: DOCUMENT_ONLY until user approves
- What it does: AI code helper and pointer
- Use in: AI Agent Lab only
- Installer: Review before use
- Secrets: No tokens

## 10. OpenPets
- Status: DOCUMENT_ONLY until user approves
- What it does: AI assistant for pet projects
- Use in: AI Agent Lab only
- Installer: Review before use
- Secrets: No stored sensitive keys

## 11. ai-memory
- Status: DOCUMENT_ONLY until user approves
- What it does: AI persistent memory assistant
- Use in: AI Agent Lab only
- Installer: Review usage and install
- Secrets: No secrets stored

---

**Important:**
- Always review installers before running.
- Never run remote installer scripts blindly.
- Keep AI agent work isolated in branches or worktrees.
- Avoid storing secrets in environment or repo.

## Non-Interactive Checks Only
- Check scripts must not launch agents interactively.
- Use `--version`, `version`, or `--help` only for detection checks.
- Run OpenCode, OpenClaw, ANUS, and 9Router manually only after explicit approval.
- Never pass secrets to agent prompts.
- Agent lab tools should run in separate worktrees or sandboxes.
