<!-- SE-owned reference derived from the durable repository-context contract. -->

# Documentation Shapes

Use simple Markdown shapes unless the consumer repository already has a
stronger local convention. Do not add schema versions to generated Markdown
without a concrete parser or migration requirement.

## Root CONTEXT.md

```markdown
# Context

## Project Purpose

Short evidence-backed purpose and stable non-goals.

## Product Areas

Brief shared areas; link detailed material from the context index below.

## Glossary

### Term

Short project-specific definition.

## Durable Rules And Boundaries

- Contextual rule that is not required on every task.

## Context Files

| File | Scope | Read when | Owner |
| --- | --- | --- | --- |
| [`worker-runtime.md`](project-context/worker-runtime.md) | Agents | Working on worker lifecycle | Runtime team |

## Scoped Contexts

| Scope | Owned paths | Context |
| --- | --- | --- |
| Agents | `agents/` | `agents/CONTEXT.md` |

## ADR Index

See [`project-context/adr/index.md`](project-context/adr/index.md).

## Open Questions

- Explicit unresolved question.
```

Omit sections without evidence. `CONTEXT.md` is an entry point and index; do
not copy a topic file's full body or reproduce the complete ADR index there.
Use `—` for a scoped row whose context file is not yet created, and inspect the
owned paths directly rather than creating a dangling pointer.

## Subproject CONTEXT.md

Every first-class subproject context links back to the root and contains only a
scope delta:

```markdown
# Accounting Context

Repository context: [`../../CONTEXT.md`](../../CONTEXT.md)

Scope: `apps/accounting/`

## Project Purpose Delta

Purpose or non-goals unique to this subproject.

## Glossary

Only subproject-specific terms.

## Durable Rules And Boundaries

Only contextual rules that do not need to be active for every task.

## Context Files

| File | Read when | Owner |
| --- | --- | --- |
| [`ledger-workflow.md`](project-context/ledger-workflow.md) | Changing ledger workflows | Accounting team |

## ADR Index

See [`project-context/adr/index.md`](project-context/adr/index.md).

## Open Questions

- Explicit unresolved local question.
```

Omit unsupported sections. Do not repeat shared root content. The local
`project-context/` is created only with its first topic or accepted local ADR;
the local `TRANSLATION.md` is created only with evidenced localization rules.

## Topic File

Every generated `project-context/<topic>.md` starts with:

```markdown
# Worker Runtime

Scope: `agents/`

Read when: working on worker startup, shutdown, or lifecycle ownership.

Owner/update logic: maintain with the worker runtime implementation and its
focused tests; remove stale claims when behavior changes.

## Overview

## Contracts And Boundaries

## Operational Notes

## Examples

## Open Questions
```

Use only sections supported by evidence. A topic file is conditionally loaded
detail, not a replacement for an always-active `AGENTS.md` rule.

## ADR Index

Create `project-context/adr/index.md` with the first accepted ADR:

```markdown
# ADR Index

| ADR | Status | Summary |
| --- | --- | --- |
| [`ADR-0001`](ADR-0001-descriptive-name.md) | Accepted | Short decision summary. |
```

Keep each root or subproject index canonical and concise. Add one row per ADR,
preserve stable links, and do not duplicate full ADR bodies in `CONTEXT.md`.

## ADR

Use `ADR-0001-descriptive-name.md` with a zero-padded monotonically allocated
number and lowercase hyphenated descriptive suffix:

```markdown
# ADR-0001: Decision title

## Status

Accepted

## Context

Why this decision is needed.

## Decision

What was decided.

## Consequences

What this enables, costs, or rules out.
```

Only accepted, load-bearing decisions belong here. Store cross-project
decisions in the root ADR tree and subproject-only decisions in the local ADR
tree. If a new decision contradicts an existing root or local ADR, surface the
conflict instead of silently overwriting it.
