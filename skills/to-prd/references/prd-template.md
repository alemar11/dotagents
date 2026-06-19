# PRD Template

Use this shape unless the project already has a stronger local PRD format.

```markdown
# PRD: [Feature Name]

## Source

- Conversation, issue, doc, or repo evidence used to create this PRD.

## Planning Identity

- Feature slug: accepted lowercase kebab-case slug.
- Product or project slug: for monorepos or orchestrator workspaces.
- Workspace path: for monorepos or multi-context repos.
- Context file: selected `CONTEXT.md` when `CONTEXT-MAP.md` is used.

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

## Product / Repository Scope

- For single-repo PRDs: say `current repository` and name any relevant module
  or package.
- For monorepo PRDs: selected product/workspace path, selected context file,
  and explicitly out-of-scope sibling workspaces when relevant.
- For orchestrator workspace PRDs: affected repos, each repo's role, and any
  repo-local implementation notes.

## Delivery Mode

- Delivery mode: `One Feature Branch` for single-repo or monorepo work, `One PR Per
  Repo` for true multi-repo work, `One PR Per Issue` only for isolated
  exceptions, or `Direct Commit` only with explicit authorization.
- Branch naming: default to `feature/<feature-slug>`; for `One PR Per Repo`,
  use that branch name in each affected repo unless repo policy differs.
- PR shape: one draft PR for the feature, one draft PR per affected repo, one
  PR per issue by exception, or no PR only for an authorized direct commit.
- Integration proof: validation or cross-repo proof required before generated
  issues close or move to `issues/done/`.
- Issue inheritance: generated issues link this PRD with `Source PRD`, copy the
  effective `Delivery mode` label as feature-level scheduling metadata, and
  carry issue-level ordering, dependencies, parallelization, closeout, and
  exceptions. `$to-issues` validates the generated issue graph before
  publication.

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

- For orchestrator workspace PRDs: proof required before a vertical issue can
  move to `issues/done/` or close in the coordination tracker.
- For single-repo or monorepo PRDs: validation or release proof that affects
  issue splitting, or `N/A` when no separate gate exists.
```
