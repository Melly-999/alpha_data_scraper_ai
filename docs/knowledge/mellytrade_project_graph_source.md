# MellyTrade Project Knowledge Graph Source

## Current Active Context
- Active task/branch context: `claude/mobile-ai-000-roadmap-u9GEY`
- Purpose: organize Mobile AI / Mobile PWA roadmap and connect it with agents, ClickUp, GitHub PR flow, validation, and safety constraints.

## Main Project Nodes
- MellyTrade Repo
- Mobile/PWA Roadmap
- Mobile/PWA Demo
- AI Workspace
- Portfolio Dashboard
- Paper Sandbox
- Audit/Event Feed
- Melly Pet
- Safety Contract
- ClickUp Task Board
- GitHub PR Flow
- ChatGPT Planning
- Claude Code Execution
- Codex Implementation
- Roadmap Docs
- Validation Gate
- Knowledge Graph Source Doc

## Agent Roles
- ChatGPT Planning = planning, prompts, review, context summaries
- Claude Code Execution = larger repo tasks, docs, UI, roadmap updates
- Codex Implementation = isolated implementation patches and tests
- ClickUp Task Board = operational task tracking
- GitHub PR Flow = branches, commits, PRs, CI, review, merge history
- Ace Knowledge Graph = visual dependency map, not an execution agent

## Safety Contract
- autotrade=false
- dry_run=true
- read_only=true where applicable
- live_orders_blocked=true
- max risk <= 1%
- no broker execution
- no secrets
- no buy/sell/execute/order buttons
- no live trading UX
- manual review before merge

## Relationship Map
- Claude Mobile AI Roadmap Task updates Mobile/PWA Roadmap
- Mobile/PWA Roadmap extends AI Workspace
- Mobile/PWA Roadmap uses Melly Pet for onboarding
- AI Workspace must obey Safety Contract
- Portfolio Dashboard must obey Safety Contract
- Paper Sandbox must obey Safety Contract
- ClickUp Task Board tracks roadmap tasks
- GitHub PR Flow records branch, PR, tests, validation, and merge history
- Validation Gate enforces Safety Contract
- ChatGPT Planning creates prompts for Claude Code and Codex
- Claude Code executes larger repo tasks
- Codex executes isolated implementation tasks
- Roadmap Docs preserve project memory
- Ace Knowledge Graph visualizes dependencies before implementation

## Prompt for Ace Knowledge Graph
Create an interactive knowledge graph for the MellyTrade project using the nodes, safety contract, and relationships listed in this document.

Represent the following project nodes clearly as connected entities:
- MellyTrade Repo
- Mobile/PWA Roadmap
- Mobile/PWA Demo
- AI Workspace
- Portfolio Dashboard
- Paper Sandbox
- Audit/Event Feed
- Melly Pet
- Safety Contract
- ClickUp Task Board
- GitHub PR Flow
- ChatGPT Planning
- Claude Code Execution
- Codex Implementation
- Roadmap Docs
- Validation Gate
- Knowledge Graph Source Doc

Apply these safety constraints to the relevant operational nodes:
- autotrade=false
- dry_run=true
- read_only=true where applicable
- live_orders_blocked=true
- max risk <= 1%
- no broker execution
- no secrets
- no buy/sell/execute/order buttons
- no live trading UX
- manual review before merge

Model the relationships as dependency and workflow links:
- Claude Mobile AI Roadmap Task updates Mobile/PWA Roadmap
- Mobile/PWA Roadmap extends AI Workspace
- Mobile/PWA Roadmap uses Melly Pet for onboarding
- AI Workspace must obey Safety Contract
- Portfolio Dashboard must obey Safety Contract
- Paper Sandbox must obey Safety Contract
- ClickUp Task Board tracks roadmap tasks
- GitHub PR Flow records branch, PR, tests, validation, and merge history
- Validation Gate enforces Safety Contract
- ChatGPT Planning creates prompts for Claude Code and Codex
- Claude Code executes larger repo tasks
- Codex executes isolated implementation tasks
- Roadmap Docs preserve project memory
- Ace Knowledge Graph visualizes dependencies before implementation

Keep the graph focused on dependency mapping, roadmap context, and safety-first delivery. Do not add execution or trading capability.

## Daily Workflow
- Before a task: inspect graph dependencies
- During a task: keep scope limited to related nodes
- After a task: update graph source with branch/PR/status if relevant
- Never store secrets in the graph

## Non-goals
- Ace Knowledge Graph does not replace GitHub
- Ace Knowledge Graph does not run tests
- Ace Knowledge Graph does not merge PRs
- Ace Knowledge Graph does not store secrets
- Ace Knowledge Graph does not execute trades
- Ace Knowledge Graph is for understanding dependencies only