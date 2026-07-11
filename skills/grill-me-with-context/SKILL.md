---
name: grill-me-with-context
description: Stress-test repo-backed plans through project context and either capture accepted decisions or hand them back for deferred capture.
---

# Grill Me With Context

## Goal

Run the `$grill-me` questioning loop for a project-backed plan. Capture durable
terminology, rules, and accepted decisions through
`$project-memory domain-memory` in inline mode, or return them as a structured
handoff in deferred mode.

Use this when the plan lives in a codebase or project workspace and the output
should improve future agent context, not just the current conversation.

## Capture Modes

- `inline` is the default for direct invocation. Use `$project-memory` with the
  `domain-memory` slice and `inline-update` operation to update the appropriate
  context docs or ADRs as accepted decisions land.
- `defer-to-caller` is available when an explicit parent workflow requests it
  or the user directly requests a non-writing or deferred result. Inspect the
  same project context and resolve the same decisions, but do not edit
  repository documentation. Return a structured
  `domain_knowledge_delta` so the caller can assign capture to a later tracked
  implementation or integration task.

Do not ask the user to choose between these modes when the caller already
provided one. Direct user invocation remains `inline` unless the user
explicitly requests a non-writing or deferred result.

### Mode Resolution

Resolve the mode deterministically before inspecting or questioning:

1. Direct `$grill-me-with-context` invocation uses `inline`.
2. An explicit user request such as "do not edit docs" or "defer capture" uses
   `defer-to-caller` and returns the structured delta to the user.
3. A parent workflow uses the mode it passes explicitly.

Do not infer deferred mode merely because the request is planning-only, because
the user did not separately request documentation edits, or because another
skill exists in the conversation. Without an explicit override, direct
invocation preserves the original inline capture behavior.

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
- In `inline` mode, load and follow `$project-memory domain-memory` with the
  `inline-update` operation for documentation updates.
- In `defer-to-caller` mode, use the domain routing evidence to identify target
  surfaces, but do not invoke documentation writes.
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

### 3. Capture or structure durable decisions

In `inline` mode, after an answer resolves a durable point, use
`$project-memory domain-memory` with `operation: inline-update`:

- add or revise glossary terms in `CONTEXT.md`,
- record business rules, lifecycle states, actors, permissions, or invariants,
- update relevant project docs with accepted workflow semantics,
- offer an ADR under `project-memory/adr/` only when a decision is load-bearing
  enough that future work would otherwise reopen it.

Keep documentation updates small and evidence-backed. Prefer enriching the
closest existing doc over creating new files.

In `defer-to-caller` mode, return this structure instead of writing docs:

```yaml
capture_mode: defer-to-caller
domain_knowledge_delta:
  status: required | none
  decisions:
    - Accepted durable term, rule, boundary, or decision.
  target_surfaces:
    - current-repository/<repo-relative-path>
    - <repo-slug>/<repo-relative-path>
  evidence:
    - current-repository/<repo-relative-path>
    - <repo-slug>/<repo-relative-path>
    - <hosted-source-or-accepted-decision-reference>
  unresolved: []
```

Use `status: required` when accepted durable knowledge is new or changes an
existing rule. Use `status: none` with empty `decisions`, `target_surfaces`, and
`evidence` when the planning discussion introduced no durable project
knowledge. The `unresolved` list is independent of capture status: keep it empty
for an actionable handoff, or record remaining product-shaping questions there
and return them to the caller as blockers. Continue grilling when possible
rather than deferring a resolvable blocker. Recommend a target surface when one
does not yet exist; do not create it in deferred mode. In multi-repo or
orchestrator work, qualify every target and repo-local evidence item with its
repository slug. Use the literal `current-repository/` prefix only for the
single current checkout.

### 4. Stop with an execution handoff

Stop when the plan is actionable, the user asks to proceed, or remaining
uncertainty no longer blocks action.

If one or more durable decisions landed during the session, an `inline`
closeout must say which ones were captured in docs and which ones were
consciously deferred.
Do not end with a generic `docs updated` line when the real outcome was "no
doc write yet"; name the deferred capture and the reason.
If capture was deferred because the repo has no suitable `CONTEXT.md`, ADR, or
other destination yet, say that explicitly and name the missing destination
file or surface.

In `defer-to-caller` mode, return the structured result without a standalone
documentation closeout. When a parent workflow invoked the skill, it owns
tracker placement and the user-facing summary. For a direct user request, add a
brief handoff with remaining risks, blockers, and the recommended next action,
but do not claim that durable docs were updated.

In `inline` mode, summarize:

- resolved decisions,
- docs updated, or explicitly deferred documentation with destination and
  reason,
- remaining risks,
- deferred questions,
- recommended next action.

## Guardrails

- Do not continue grilling after the user asks to proceed.
- Do not silently change a direct invocation from `inline` to deferred mode.
- Do not implement the plan unless the user explicitly switches to execution.
- Do not let documentation work interrupt the one-question flow; in `inline`
  mode, write docs between questions or when a decision has clearly landed.
- Never write `CONTEXT.md`, project docs, or ADRs in `defer-to-caller` mode.
- Do not silently leave durable accepted decisions undocumented. In `inline`
  mode, capture them or explicitly defer capture in the closeout. In
  `defer-to-caller` mode, record them and their intended destinations in the
  structured delta.
- Do not create broad project doctrine from a single narrow decision.
