# PRD Template

Use this shape unless the project already has a stronger local PRD format.

## Structured Values

Use these `delivery_mode` values in every PRD:

- `pull-request`: feature branch plus PR delivery. In a single repo or monorepo,
  use one feature branch and PR. In multi-repo work, every involved repo uses
  the same branch name and opens its own PR.
- `direct-commit`: direct commit path, only with explicit maintainer
  authorization.

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

```markdown
# PRD: [Feature Name]

## Source

- Conversation, issue, doc, or repo evidence used to create this PRD.
- Use portable evidence references only: repo-relative paths for current-repo
  files, `<repo-name>/<repo-relative-path>` for sibling repos, hosted URLs, or
  descriptive labels for local-only references. Do not include
  developer-machine absolute paths.

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

- Delivery mode: `pull-request` by default, or `direct-commit` only with
  explicit authorization.
- Branch naming: default to `feature/<feature-slug>`; for multi-repo work, use
  that same branch name in each affected repo unless repo policy differs.
- PR shape: one draft PR for the feature in a single repo or monorepo; one draft
  PR per affected repo in multi-repo work; no PR only for an authorized direct
  commit.
- Integration proof: validation or cross-repo proof required before generated
  issues close or move to `issues/done/`.
- Issue inheritance: generated issues link this PRD with `Source PRD`, copy the
  effective `Delivery mode` label as feature-level scheduling metadata, and
  carry issue-level ordering, dependencies, parallelization, closeout, and
  exceptions. The issue phase validates the generated issue graph before
  publication.

## Cross-Repo Contracts

Include only when multiple repositories or packages must remain compatible:
API shape, schema, version, migration, fixture, deploy, or compatibility
contracts that issue splitting must preserve.

## Acceptance Criteria

- [ ] Specific, testable product or system outcome.

## Risks

- Risk, tradeoff, or compatibility concern.

## Open Questions

- Question that must be resolved before or during issue splitting.

## Issue-Splitting Notes

- Suggested vertical slices, sequencing constraints, or dependencies for
  the issue phase.

## Integration Gates

Include only when separate validation, release, or cross-repo proof affects issue
splitting or closeout.
```
