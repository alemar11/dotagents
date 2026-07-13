# PRD Template

Use this shape unless the project already has a stronger local PRD format.

## Structured Values

Use these `delivery_mode` values in every PRD:

- `pull-request`: feature branch plus PR delivery. In a single repo or monorepo,
  use one feature branch and PR. In multi-repo work, every involved repo uses
  the same branch name and opens its own PR.
- `direct-commit`: direct commit path. The `delivery_mode` option row must use
  `source=owner-instruction` and its evidence must name the exact owner
  instruction, feature scope, and authorized target branch. A migrated
  `source-prd` row is valid only when it preserves that same evidence.

For `pull-request`, use these `pr_closeout` values:

- `merge-ready`: default. The PR opens as draft initially and progresses
  through validation, ready-for-review transition, Codex review, and
  merge-ready closeout without authorizing merge.
- `draft-only`: terminal draft state, only when the current user explicitly
  selects `pr_closeout=draft-only` or an option-resolution row records that
  canonical value with accepted owner/source evidence.

Do not select `draft-only` by comparing free-form prose. Normalize an accepted
instruction once in the option-resolution record, then read only
`pr_closeout`.

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

- delivery_mode: `pull-request` or `direct-commit`.
- delivery_mode_evidence: option-resolution source/ref; for `direct-commit`,
  use `owner-ref=<ref>;scope-ref=run;target-ref=<feature-or-source-ref>;target-branch=<branch_name>`
  to name the exact owner instruction, feature scope, and authorized target
  branch.
- issue_mutation_authority: `none`, `pr-body-closeout-only`, or
  `explicit-direct-mutation`. Use `none` for local trackers,
  `pr-body-closeout-only` for GitHub pull-request delivery, and
  `explicit-direct-mutation` for GitHub direct-commit delivery only when a
  separate option row records explicit final-commit closure authority.
- issue_mutation_authority_evidence: option-resolution source/ref; for
  `explicit-direct-mutation`, use the same scope/target/branch tokens as
  direct-commit delivery, preserve its independent `owner-ref`, and require
  that ref to identify an instruction
  that explicitly authorizes final-commit issue closure.
- pr_closeout: `merge-ready`, `draft-only`, or `not-applicable`.
- pr_closeout_evidence: option-resolution source/ref; required for
  `draft-only`.
- branch_name: for `pull-request`, default to `feature/<feature-slug>` and use
  that same branch name in each affected repo unless repo policy differs; for
  `direct-commit`, use the exact target branch named by
  `delivery_mode_evidence`.
- pr_shape: `single-pr`, `per-repo-pr`, or `none`.
- integration_proof: validation or cross-repo proof required before generated
  issues close or move to `issues/done/`.
- issue_inheritance: generated issues link this PRD with `source_prd_ref`, copy
  the effective `delivery_mode` and `pr_closeout` values as feature-level metadata,
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

- `knowledge_delta=required`
- `capture_outcome=deferred`
- `memory_slice=domain-memory`
- `domain_operation=implementation-closeout`
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
