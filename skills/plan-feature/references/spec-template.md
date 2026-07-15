# Feature Spec Template

Use this shape unless the project already has a stronger local Feature Spec format.

## Structured Value Projection

`references/options.md` is the sole owner of option names, values, defaults,
sources, evidence, and cross-field constraints. This template only projects an
already verified option snapshot into the Feature Spec; do not resolve or override
options here.
Render each field and its evidence exactly from that verified snapshot; keep
derived paths, fingerprints, and integration proof as separate data.

```markdown
# Feature Spec: [Feature Name]

## Source

- Conversation, issue, doc, or repo evidence used to create this Feature Spec.
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

- Concrete outcome this Feature Spec should deliver.

## Non-Goals

- Explicitly excluded work.

## Users and Use Cases

- Target user, actor, or system.
- Primary workflow.

## Requirements

- Functional requirement.
- Behavior, data, permission, API, or integration requirement when relevant.

## Product / Repository Scope

- For single-repository Feature Specs: say `current repository` and name any relevant module
  or package.
- For monorepo Feature Specs: selected product/workspace path, selected context file,
  and explicitly out-of-scope sibling workspaces when relevant.
- For orchestrator workspace Feature Specs: affected repos, each repo's role, and any
  repo-local implementation notes.

## Change Delivery Target

- change_delivery_target: [verified `change_delivery_target` row value].
- change_delivery_target_evidence: [verified target option-row source and evidence].
- change_delivery_permission: [verified `change_delivery_permission` row value].
- change_delivery_permission_evidence: [verified `permission-source-ref`, scope, target, branch, and transfer evidence].
- repository_layout: [verified `repository_layout` row value].
- child_repository_layout: [child repo durable topology for repo-scoped workspace partials, or not-applicable].
- workspace_context: [multi-repository-workspace or not-applicable].
- workspace_parent_source_ref: [parent/global Feature Spec ref or not-applicable].
- workspace_feature_repos: [complete feature-wide repo slug set or not-applicable].
- workspace_child_source_refs: [complete repo-to-child Feature Spec mapping before issue generation, `unresolved-first-pass` during first-pass workspace child publication, or not-applicable outside workspace flows].
- issue_update_permission: [verified `issue_update_permission` row value].
- issue_update_permission_evidence: [verified independent option-row source and evidence].
- codex_review_requirement: [verified `codex_review_requirement` row value].
- target_branch_name: [verified exact branch data].
- pull_request_count_strategy: [verified `pull_request_count_strategy` row value].
- integration_proof: validation or cross-repo proof required before generated
  issues close or move to `issues/done/`.
- issue_inheritance: generated issues link this Feature Spec with `source_spec_ref`, copy
  the effective `change_delivery_target`, `change_delivery_permission`,
  `codex_review_requirement`, feature/workspace `repository_layout`, and
  `pull_request_count_strategy` values as feature-level metadata, derive
  `issue_repository_layout` from `child_repository_layout` or target repo evidence,
  and carry issue-level ordering, dependencies, parallelization, closeout, and
  exceptions. The issue phase validates the generated issue graph before
  publication.

## Feature Dependencies

| upstream_feature_spec_ref | dependency_start_condition | dependency_reason |
| --- | --- | --- |
| [durable Feature Spec ref] | [upstream-merged or upstream-merge-ready-head] | [concrete non-empty reason] |

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
  - `current-repository/<repo-relative-path>` for single-repository work, or
    `<repo-slug>/<repo-relative-path>` for multi-repo context, project doc, or
    ADR destinations.
- Evidence:
  - Portable current-repository, repo-slug-qualified, hosted, or accepted
    conversation evidence.
- Closeout proof:
  - Update the target surfaces after implementation and verify they describe
    the integrated behavior that actually landed.
```

The `## Feature Dependencies` section is mandatory for every newly produced
Feature Spec. Emit exactly one data row per authored upstream edge. When there
are no edges, retain the heading and table header but omit the placeholder data
row. Resolve the default `upstream-merged` value before rendering a row; never
persist a blank start condition.
