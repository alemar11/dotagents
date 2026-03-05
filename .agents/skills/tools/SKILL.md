---
name: tools
description: Orchestrate repository maintenance tasks for Codex skills, including metadata/doc sync, consistency checks, and skill-specific refresh runbooks.
---

# Tools

## Goal
Use this project-maintainer skill to keep skills aligned, healthy, and releasable. This skill orchestrates maintenance workflows; it does not replace domain skills.

## Trigger rules
Use this skill when users ask to:
- Maintain or clean up one or more skills
- Sync `SKILL.md`, `agents/openai.yaml`, and repository docs
- Run a maintenance pass before release
- Refresh Postgres best-practices references

## Workflow
1) Route the request with `references/maintenance-router.md`.
2) For metadata/docs alignment, follow `references/metadata-sync.md`.
3) For repository-wide structure and rules checks, follow `references/doc-consistency.md`.
4) For Postgres best-practices refresh, follow `references/postgres-refresh.md` (self-contained workflow in this skill).
5) Before finishing, run `references/release-checklist.md` and report pass/fail with actionable findings.

## Guardrails
- Keep this skill orchestration-only in v1.
- Prefer repeatable commands and documented checks in this skill before inventing ad-hoc flows.
- Do not depend on markdown guidance outside this skill's `references/` folder.
- Keep changes scoped to requested maintenance outcomes.
- If no meaningful updates are needed, return `PASS (NOOP)` and avoid persistent file edits.
