# PRD Template

Use this shape unless the project already has a stronger local PRD format.

## Structured Values

Use these `delivery_mode` values in every PRD:

- `pull-request`: feature branch plus PR delivery. In a single repo or monorepo,
  use one feature branch and PR. In multi-repo work, every involved repo uses
  the same branch name and opens its own PR.
- `direct-commit`: direct commit path, only with explicit maintainer
  authorization.

For `pull-request`, use these `pr_closeout` values:

- `merge-ready`: default. The PR opens as draft initially and progresses
  through validation, ready-for-review transition, Codex review, and
  merge-ready closeout without authorizing merge.
- `draft-only`: terminal draft state, only when the current user explicitly
  asks to keep or leave the PR in draft.

Do not infer `draft-only` from prose such as `draft PR`, `open a draft PR`, or
`do not merge automatically`.

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
- PR closeout: `merge-ready` by default for `pull-request`; use `draft-only`
  only after an explicit current-user request or when preserving an existing
  structured `PR closeout: draft-only` decision.
- Branch naming: default to `feature/<feature-slug>`; for multi-repo work, use
  that same branch name in each affected repo unless repo policy differs.
- PR shape: one PR opened as draft initially for the feature in a single repo
  or monorepo; one PR per affected repo opened as draft initially in multi-repo
  work; no PR only for an authorized direct commit.
- Integration proof: validation or cross-repo proof required before generated
  issues close or move to `issues/done/`.
- Issue inheritance: generated issues link this PRD with `Source PRD`, copy the
  effective `Delivery mode` and `PR closeout` labels as feature-level metadata,
  and carry issue-level ordering, dependencies, parallelization, closeout, and
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

## Domain Knowledge Handoff

Include only when planning resolved new durable project knowledge. This is a
deferred handoff for the final implementation task, not completed capture.

- Decisions:
  - Accepted durable term, rule, boundary, or decision.
- Target surfaces:
  - `current-repository/<repo-relative-path>` for single-repo work, or
    `<repo-slug>/<repo-relative-path>` for multi-repo context, project doc, or
    ADR destinations.
- Evidence:
  - Portable current-repository, repo-slug-qualified, hosted, or accepted
    conversation evidence.
- Closeout proof:
  - Update the target surfaces after implementation and verify they describe
    the integrated behavior that actually landed.
```
