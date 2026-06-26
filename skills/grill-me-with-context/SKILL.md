---
name: grill-me-with-context
description: Stress-test repo-backed plans through project context and capture accepted decisions in docs or ADRs.
---

# Grill Me With Context

## Goal

Run the `$grill-me` questioning loop for a project-backed plan and use
`$domain-modeling` to capture durable terminology, rules, and accepted
decisions as they become clear.

Use this when the plan lives in a codebase or project workspace and the output
should improve future agent context, not just the current conversation.

## Trigger Rules

- Use when the user explicitly asks for grilling, pressure-testing, or
  challenge "with docs", "with context", "with ADRs", or "with domain model".
- Use for feature, architecture, workflow, migration, or product decisions that
  should update project context as the session resolves them.
- Do not use for generic personal decisions, one-off writing plans, or plans
  with no durable project documentation surface; use `$grill-me` alone instead.
- Do not update docs for rejected, tentative, or unresolved decisions.

## Workflow

### 1. Ground in the project

- Inspect the relevant repo files, existing docs, `CONTEXT.md`,
  `CONTEXT-MAP.md`, `project-memory/agents/domain.md`, and
  `project-memory/adr/` before asking questions.
- Load and follow `$grill-me` for the one-question-at-a-time interrogation
  loop.
- Load and follow `$domain-modeling` for inline documentation updates.
- Do not ask questions whose answers are already present in code or docs.

### 2. Grill one decision at a time

Use `$grill-me` to expose missing constraints, hidden assumptions, weak
tradeoffs, and unclear success criteria.

Ask exactly one high-signal question at a time. Include a recommended answer so
the user can accept, reject, or adjust quickly.

```text
Question: [one concrete question]
Recommended answer: [default and why, in one short sentence]
```

### 3. Capture durable docs as decisions land

After an answer resolves a durable point, use `$domain-modeling` inline:

- add or revise glossary terms in `CONTEXT.md`,
- record business rules, lifecycle states, actors, permissions, or invariants,
- update relevant project docs with accepted workflow semantics,
- offer an ADR under `project-memory/adr/` only when a decision is load-bearing
  enough that future work would otherwise reopen it.

Keep documentation updates small and evidence-backed. Prefer enriching the
closest existing doc over creating new files.

### 4. Stop with an execution handoff

Stop when the plan is actionable, the user asks to proceed, or remaining
uncertainty no longer blocks action.

Summarize:

- resolved decisions,
- docs updated,
- remaining risks,
- deferred questions,
- recommended next action.

## Guardrails

- Do not continue grilling after the user asks to proceed.
- Do not implement the plan unless the user explicitly switches to execution.
- Do not let documentation work interrupt the one-question flow; write docs
  between questions or when a decision has clearly landed.
- Do not create broad project doctrine from a single narrow decision.
