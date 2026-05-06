# Newsbot skill migration

This repository now hosts the repo-managed market routing skill for the OpenClaw `news` agent.

## Current source of truth

Skill directory:

- `skills/newsbot-stock-routing/`

OpenClaw config loads it via:

- `~/.openclaw/openclaw.json`
- `skills.load.extraDirs += /home/openclaw/桌面/openclaw/codes/openclaw-stock-mcp/skills`

## Why migrated

Previously the `news` agent used a workspace-local skill:

- `/home/openclaw/.openclaw/workspace-news/skills/newsbot-stock-routing/`

That made the routing instructions drift-prone because:

- code/schema evolved in this repo
- skill lived elsewhere
- docs/tests and skill could fall out of sync

The repo-managed layout keeps code, tests, docs, and skill versioned together.

## Workspace-local skill status

The previous workspace-local skill was moved to:

- `/home/openclaw/.openclaw/workspace-news/.trash/newsbot-stock-routing.migrated-2026-05-06`

This is only a backup and should not be treated as active.

## Maintenance rule

When changing any of the following, review this skill in the same PR/commit series:

- `market_brief`
- `sector_review`
- `review_envelope_v1`
- `sentiment_temperature_v1`
- `rotation_signal_v1`
- provider routing behavior
- payload validation rules

## Verification commands

```bash
openclaw skills list --eligible | grep newsbot-stock-routing
openclaw skills info newsbot-stock-routing
```
