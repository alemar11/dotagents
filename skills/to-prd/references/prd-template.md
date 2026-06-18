# PRD Template

Use this shape unless the project already has a stronger local PRD format.

```markdown
# PRD: [Feature Name]

## Status

Draft

## Source

- Conversation, issue, doc, or repo evidence used to create this PRD.

## Problem

What user or system problem this solves.

## Goals

- Concrete outcome this PRD should deliver.

## Non-Goals

- Explicitly excluded work.

## Users and Use Cases

- Target user, actor, or system.
- Primary workflow.

## Requirements

- Functional requirement.
- Behavior, data, permission, API, or integration requirement when relevant.

## Repository Scope

- For orchestrator workspace PRDs only: affected repos, each repo's role, and
  any repo-local implementation notes. Use `N/A` for ordinary single-repo PRDs.

## Cross-Repo Contracts

- For orchestrator workspace PRDs only: API shape, schema, version, migration,
  fixture, deploy, or compatibility contracts that issue splitting must
  preserve. Use `N/A` for ordinary single-repo PRDs.

## Acceptance Criteria

- [ ] Specific, testable product or system outcome.

## Risks

- Risk, tradeoff, or compatibility concern.

## Open Questions

- Question that must be resolved before or during issue splitting.

## Issue-Splitting Notes

- Suggested vertical slices, sequencing constraints, or dependencies for
  `$to-issues`.

## Integration Gates

- For orchestrator workspace PRDs only: proof required before a vertical issue
  can move to `issues/done/` or close in the coordination tracker.
```
