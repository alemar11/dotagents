---
name: domain-modeling
description: Build and maintain project domain language, context docs, and ADRs from repo evidence and accepted decisions.
---

# Domain Modeling

## Goal

Keep a project's shared language and durable decisions current while work is
being discussed. Turn clarified terminology, boundaries, rules, and decisions
into lightweight project documentation that future agents and maintainers can
reuse.

This is an inline documentation skill, not a standalone brainstorming session.
Update docs only when the conversation or repo evidence resolves something
durable.

## Trigger Rules

- Use when the user asks to model a domain, define terms, sharpen vocabulary,
  record architectural or product decisions, or update project context docs.
- Use when another skill is clarifying a codebase-backed plan and domain terms,
  business concepts, workflows, or durable decisions become clear.
- Do not invent a domain model before there is evidence from the user, repo, or
  existing docs.
- Do not update docs for transient preferences, tentative ideas, or decisions
  the user has not accepted.

## Workflow

### 1. Inspect existing context

- Look for `CONTEXT.md`, `CONTEXT-MAP.md`,
  `project-memory/agents/domain.md`, `project-memory/adr/`, `README.md`,
  project docs, product specs, issue templates, and nearby code or tests that
  define the vocabulary already in use.
- If `CONTEXT-MAP.md` exists, use it to choose the relevant context-specific
  `CONTEXT.md` before editing domain language.
- Prefer updating an existing relevant file over creating a new one.
- If no domain context file exists and a durable term or rule needs a home,
  create `CONTEXT.md` at the project root.

### 2. Sharpen the model

Track these items while the conversation progresses:

- **Terms**: project-specific words, aliases, and phrases.
- **Boundaries**: where one concept, workflow, actor, or module stops and
  another starts.
- **Rules**: invariants, permissions, lifecycle transitions, validations, and
  failure states.
- **Decisions**: accepted choices that future work should not relitigate.
- **Open questions**: unresolved points that should remain visibly uncertain.

When a term is fuzzy, challenge it with a concrete edge case before writing it
down. When two names appear to mean the same thing, ask whether they are aliases
or distinct concepts.

### 3. Update docs inline

Write the smallest durable update that preserves the resolved meaning:

- Add or revise glossary entries in `CONTEXT.md`.
- Add short workflow or rule notes to the most relevant project doc.
- Add an ADR under `project-memory/adr/` only for load-bearing decisions that
  future agents or maintainers would otherwise reopen.
- Leave open questions clearly marked instead of smoothing over uncertainty.

Keep docs practical:

- Use project vocabulary from the repo and user.
- Link to relevant source files, issues, or ADRs when they are available.
- Avoid generic domain-driven-design exposition.
- Do not rewrite broad docs just to add one clarified term.

### 4. Report what changed

When returning to the user or calling skill, summarize:

- docs created or updated,
- terms, rules, or decisions captured,
- unresolved domain questions,
- any decision that may deserve a future ADR.

## Documentation Shapes

Use simple Markdown shapes unless the project already has a stronger local
format.

For `CONTEXT.md`:

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

## Guardrails

- Do not make runtime skills depend on repo-maintenance docs.
- Do not create ADRs for every small preference; reserve them for durable,
  load-bearing decisions.
- Do not remove existing domain notes unless the user explicitly invalidates
  them or repo evidence proves they are stale.
- Do not ask documentation questions that can be answered by reading the repo.
