# Documentation Shapes

Use simple Markdown shapes unless the project already has a stronger local
format.

## CONTEXT.md

```markdown
# Context

## Glossary

### Term

Short project-specific definition.

- Also called: optional alias
- Not: nearby concept it should not be confused with
- Source: optional issue, file, or ADR link

## Rules

- Durable rule or invariant.

## Open Questions

- Question that remains unresolved.
```

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
