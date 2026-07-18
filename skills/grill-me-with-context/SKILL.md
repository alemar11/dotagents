---
name: grill-me-with-context
description: Stress-test repo-backed plans through project context and either capture accepted decisions or hand them back for deferred capture.
---

# Grill Me With Context

## Goal

Run the `$grill-me` questioning loop for a project-backed plan. Capture durable
terminology, rules, and accepted decisions through
`$project-memory domain-memory` with `capture_mode=inline`, or return them as a
structured handoff with `capture_mode=defer-to-caller`.

Use this when the plan lives in a codebase or project workspace and the output
should improve future agent context, not just the current conversation.

## Capture Modes

- `capture_mode=inline` is the default for direct invocation. Use
  `$project-memory` with `memory_slice=domain-memory` and
  `domain_operation=inline-update` to update the appropriate context docs or
  ADRs as accepted decisions land.
- `capture_mode=defer-to-caller` is available when an explicit parent workflow requests it
  or the user directly requests a non-writing or deferred result. Inspect the
  same project context and resolve the same decisions, but do not edit
  repository documentation. Return an optional structured `knowledge_delta`
  data object so the caller can assign capture to a later tracked
  implementation or integration task.

Load `$project-memory`'s `references/options.md` before resolving this field.
Do not ask the user to choose when the caller already provided a canonical
value. Direct user invocation remains `capture_mode=inline` unless the user
explicitly requests a non-writing or deferred result.

### Mode Resolution

Resolve the mode deterministically before inspecting or questioning:

1. An explicit user request such as "do not edit docs" or "defer capture" uses
   `capture_mode=defer-to-caller` and returns the structured delta to the user.
   This narrower no-write instruction wins over every writing default.
2. Otherwise, a parent workflow uses the canonical `capture_mode` it passes
   explicitly.
3. Otherwise, direct `$grill-me-with-context` invocation uses
   `capture_mode=inline`.

Do not infer `capture_mode=defer-to-caller` merely because the request is
planning-only, because the user did not separately request documentation
edits, or because another skill exists in the conversation. Without an
explicit override, direct invocation preserves `capture_mode=inline`.

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

- Inspect the relevant repository files and existing docs. Read root
  `CONTEXT.md` when it exists and treat the current Git repository as a
  selected root. In a coordination workspace, also follow its
  `Repository Registry` to affected child-repository roots and read each
  available child root context. Then read
  every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table and the relevant root
  `project-memory/adr/` trees before asking questions. When a root or matched
  route has no context, inspect its repository paths directly without
  inventing one.
- Load and follow `$grill-me` for the one-question-at-a-time interrogation
  loop.
- With `capture_mode=inline`, load and follow `$project-memory domain-memory`
  with `memory_slice=domain-memory` and `domain_operation=inline-update` for
  documentation updates.
- With `capture_mode=defer-to-caller`, use the domain routing evidence to identify target
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

With `capture_mode=inline`, after an answer resolves a durable point, use
`$project-memory domain-memory` with `memory_slice=domain-memory` and
`domain_operation=inline-update`:

- add or revise glossary terms in `CONTEXT.md`,
- record business rules, lifecycle states, actors, permissions, or invariants,
- update relevant project docs with accepted workflow semantics,
- offer an ADR under `project-memory/adr/` only when a decision is load-bearing
  enough that future work would otherwise reopen it.

Keep documentation updates small and evidence-backed. Prefer enriching the
closest existing doc over creating new files.

With `capture_mode=defer-to-caller`, return this structure instead of writing
docs:

```yaml
capture_mode: defer-to-caller
capture_outcome: deferred
knowledge_delta:
  decisions:
    - Accepted durable term, rule, boundary, or decision.
  target_surfaces:
    - current-repository/<repo-relative-path>
    - <repo-slug>/<repo-relative-path>
  evidence:
    - current-repository/<repo-relative-path>
    - <repo-slug>/<repo-relative-path>
    - <hosted-source-or-accepted-decision-reference>
planning_blockers: []
```

Emit the optional `knowledge_delta` object with
`capture_outcome=deferred` only when accepted durable knowledge is new or
changes an existing rule. When the planning discussion introduced no durable
project knowledge, omit `knowledge_delta` entirely and return
`capture_outcome=no-durable-change`. Keep `planning_blockers` separate from the
knowledge data: leave it empty for an actionable handoff, or record remaining
product-shaping questions there and return them to the caller as blockers.
Continue grilling when possible rather than deferring a resolvable blocker.
Recommend a target surface when one does not yet exist; do not create it with
`capture_mode=defer-to-caller`. In multi-repo or
orchestrator work, qualify every target and repo-local evidence item with its
repository slug. Use the literal `current-repository/` prefix only for the
single current checkout.

### 4. Stop with an execution handoff

Stop when the plan is actionable, the user asks to proceed, or remaining
uncertainty no longer blocks action.

If one or more durable decisions landed during the session, a
`capture_mode=inline` closeout must emit `capture_outcome=captured` when all
accepted changes landed, or `capture_outcome=deferred` with separate destination
and reason data for any capture that did not land.
Do not end with a generic `docs updated` line when the real outcome was "no
doc write yet"; name the deferred capture and the reason.
If capture was deferred because the repo has no suitable `CONTEXT.md`, ADR, or
other destination yet, say that explicitly and name the missing destination
file or surface.

With `capture_mode=defer-to-caller`, return the structured result without a standalone
documentation closeout. When a parent workflow invoked the skill, it owns
tracker placement and the user-facing summary. For a direct user request, add a
brief handoff with remaining risks, blockers, and the recommended next action,
but do not claim that durable docs were updated.

With `capture_mode=inline`, summarize:

- `capture_outcome`,
- resolved decisions,
- docs updated, or explicitly deferred documentation with destination and
  reason,
- remaining risks,
- deferred questions,
- recommended next action.

## Guardrails

- Do not continue grilling after the user asks to proceed.
- Do not silently change a direct invocation from `capture_mode=inline` to
  `capture_mode=defer-to-caller`.
- Do not implement the plan unless the user explicitly switches to execution.
- Do not let documentation work interrupt the one-question flow; with
  `capture_mode=inline`, write docs between questions or when a decision has
  clearly landed.
- Never write `CONTEXT.md`, project docs, or ADRs with
  `capture_mode=defer-to-caller`.
- Do not silently leave durable accepted decisions undocumented. With
  `capture_mode=inline`, capture them or explicitly defer capture in the
  closeout. With `capture_mode=defer-to-caller`, record them and their intended
  destinations in the optional `knowledge_delta` object.
- Do not create broad project doctrine from a single narrow decision.
