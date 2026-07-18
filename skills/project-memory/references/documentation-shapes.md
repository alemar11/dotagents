# Documentation Shapes

Use simple Markdown shapes unless the project already has a stronger local
format.

## Root CONTEXT.md

```markdown
# Context

## Project Purpose

## Product Areas

## Glossary

### Term

Short project-specific definition.

- Also called: optional alias
- Not: nearby concept it should not be confused with
- Source: optional durable repo file or ADR link

## Durable Rules And Boundaries

- Durable rule or invariant.

## Open Questions

- Question that remains unresolved.
```

When the root routes internal scopes or child repositories, add the canonical
`## Scoped Contexts` or `## Repository Registry` table from `domain.md`. Do not
invent a second routing shape.

## Scoped CONTEXT.md

```markdown
# [Scope] Context

Parent context: [`CONTEXT.md`](<relative-path-to-root-CONTEXT.md>)

## Scope Purpose And Non-Goals

## Domain Vocabulary

## Boundaries And Handoffs

## Durable Rules

## Relevant Decisions

- [`ADR-0001`](<relative-path-to-root-project-memory/adr/ADR-0001.md>)

## Open Questions
```

Record only the scope-specific delta. Shared purpose, vocabulary, and rules
remain in the root context.

## ADRs

For ADRs under `project-memory/adr/`:

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
