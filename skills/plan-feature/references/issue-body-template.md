# Issue Body Template

Use this shape unless the tracker has a stronger local template. Delete only
optional presentation fields whose bracketed instructions say to omit them;
never omit a verified Per-Issue Registry projection. Evidence references in
issue bodies must be portable: use repo-relative paths,
sibling-repo-relative paths, hosted issue or PR URLs, or descriptive references.
Do not include developer-machine absolute paths in returned bodies, local issue
files, hosted issue bodies, or draft publish commands.

`references/options.md` is the sole owner of delivery, scheduling, closeout,
integration, domain-closeout, source, and evidence values. This template owns
only their output placement and completion prose; project the complete verified
Per-Issue Registry rows without resolving or defaulting them here.

```markdown
# <feature-slug>: <NN> <vertical outcome>

issue_type: [canonical bug | feature | task]
workflow_state: [canonical state, usually ready-for-agent]
source_spec_ref: [path, issue number, or stable draft ref; draft refs are valid
only in non-mutating output before hosted mutation]

Affected Repos: [issue-local target repo slugs for workspace issues; otherwise omit]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repository issues, `current repository`; for workspace issues, use
`Affected Repos`]

## Option Resolution

issue_option_rows_fingerprint: [verified fingerprint over this issue's rows
below]

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `issue:<NN>:<field>` | `issue:<NN>` | [Per-Issue Registry field or `target_branch_name`] | [verified value or data] | [verified canonical source] | [verified portable evidence or `none` only when allowed] |

Expand the row above into exactly one row for every Per-Issue Registry field
plus the issue-effective `target_branch_name` row. Preserve the verified six-column
cells; do not infer or omit row metadata here.

## Delivery

- change_delivery_target: [verified `change_delivery_target` row value]
- change_delivery_permission: [verified `change_delivery_permission` row value]
- change_delivery_permission_evidence: [verified permission-source, scope, target, branch, and transfer evidence]
- delivery_decision_origin: [verified `delivery_decision_origin` row value]
- delivery_decision_origin_evidence: [verified delivery evidence data]
- repository_layout: [same feature/workspace graph value as the source Feature Spec]
- issue_repository_layout: [verified `issue_repository_layout` row value]
- issue_update_permission: [verified `issue_update_permission` row value]
- issue_update_permission_evidence: [verified independent mutation evidence data]
- codex_review_requirement: [verified `codex_review_requirement` row value]
- target_branch_name: [verified exact branch data]
- pull_request_count_strategy: [verified `pull_request_count_strategy` row value]
- parallelization: [verified `parallelization` row value]
- dependency_ids: [issue ids or none]
- blocked_issue_ids: [issue ids or none]
- issue_completion_method: [verified `issue_completion_method` row value]

## Orchestrator Handoff

- source_spec_ref: [same value as the header `source_spec_ref` line]
- feature_slug: [authoritative lowercase feature slug]
- change_delivery_target: [same effective value as `## Delivery`]
- change_delivery_permission: [same effective value as `## Delivery`]
- change_delivery_permission_evidence: [same evidence as `## Delivery`]
- delivery_decision_origin: [same canonical value as `## Delivery`]
- delivery_decision_origin_evidence: [same evidence as `## Delivery`]
- repository_layout: [same feature/workspace graph value as the source Feature Spec]
- issue_repository_layout: [same issue-effective value as `## Delivery`]
- workspace_context: [multi-repository-workspace or not-applicable]
- workspace_parent_source_ref: [parent/global Feature Spec ref or not-applicable]
- workspace_feature_repos: [complete feature-wide repo slug set or not-applicable]
- workspace_child_source_refs: [complete repo-to-Feature-Spec-ref mapping for `workspace_feature_repos`, or not-applicable]
- issue_update_permission: [same effective value as `## Delivery`]
- issue_update_permission_evidence: [same evidence as `## Delivery`]
- codex_review_requirement: [same effective value as `## Delivery`]
- target_branch_name: [same effective branch data as `## Delivery`]
- pull_request_count_strategy: [same effective value as `## Delivery`]
- affected_repos_or_product_scope: [repo slugs, workspace path, or current
  repository]
- scope:
  - [Only this issue's implementation slice.]
- parallelization: [same verified value as `## Delivery`]
- dependency_ids: [generated issue IDs or none]
- blocked_issue_ids: [generated issue IDs or none]
- dependency_reason: [reason or none]
- validation: [commands, checks, or proof required for this issue.]
- domain_closeout: [verified `domain_closeout` row value]
- domain_closeout_data: [when applicable, the exact
  decisions, target surfaces, evidence, `memory_slice=domain-memory`, and
  `domain_operation=implementation-closeout` required by
  `## Domain Knowledge Closeout` below]
- issue_completion_method: [same verified value as `## Delivery`]

Do not include worker action grants, worker surfaces, worker counts,
checkpoint approval, publication authority, or orchestration session settings
in this section. The source-contract `issue_update_permission` does not grant a
worker permission; `$codex-orchestrator` validates and projects it after
registering the issue as a workstream.

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant Feature Spec and repo context using portable references only.]

## Cross-Repo Notes

[Include only for workspace issues: affected repos, interface contracts,
existing repo PR links, expected repo PR slots or pre-implementation
placeholders, and validation order. Placeholders are scheduling expectations,
not completion proof; orchestrator closeout records real PR links or equivalent
integration proof.]

## Integration Gates

[Include only when separate validation, release, or cross-repo proof affects
completion.]

## Domain Knowledge Closeout

[Include only on the final integration task when the source_spec_ref carries a
required domain-knowledge handoff. This task must also prove integrated feature
behavior; never use this section to justify a docs-only issue.]

- Required workflow:
  - Invoke `$project-memory` with `memory_slice=domain-memory` and
    `domain_operation=implementation-closeout` after the integrated behavior is
    proven. Project Memory must run its internal domain-modeling workflow;
    reading `project-memory/config/domain.md` or editing the targets directly
    is not a substitute.

- Decisions:
  - [Accepted durable term, rule, boundary, or decision carried from the Feature Spec.]
- Target surfaces:
  - [`current-repository/<repo-relative-path>` or
    `<repo-slug>/<repo-relative-path>` destination.]
- Evidence:
  - [Portable current-repository, repo-slug-qualified, hosted, or accepted
    implementation evidence.]
- Closeout proof:
  - [Integration validation, `$project-memory domain-memory` completion,
    internal domain-modeling workflow completion, and documentation
    diff/consistency verification.]

## Requirements

- [Requirement this issue must satisfy.]

## Implementation Plan

Plan-hardening: $plan-harder issue-hardening pass completed for this issue only.

[Concise implementation approach synthesized from the $plan-harder hardening
brief. Do not duplicate acceptance criteria, validation, dependencies,
questions, or completion rules here; merge those details into their top-level
sections.]

## Acceptance Criteria

- [ ] [Specific, verifiable outcome.]

## Validation

- Preferred: [Command, test, or manual check.]
- Fallback: [Equivalent runner when the preferred command wrapper is
  unavailable, or `None`.]

## Completion

When all acceptance criteria pass and validation is complete:

- GitHub: close this implementation issue from the relevant PR body, following
  `issue_completion_method`. Use `Closes #<this-issue-number>` only when the PR lives in the
  same GitHub repository as the issue. For orchestrator or cross-repo closeout
  where the PR repository differs from the issue repository, use
  `Closes owner/repo#<this-issue-number>` only when that cross-repo closing path
  is intended and supported; otherwise use non-closing links and record the
  coordination closeout action separately. Final-commit closure requires
  `issue_completion_method=final-commit-closing-keyword`,
  `issue_update_permission=direct-issue-updates-explicitly-authorized`, and its exact scoped
  authorization evidence. Do not add the parent Feature Spec closing keyword from an individual child
  issue. For a whole Feature Spec final feature
  or integration PR, the root delivery orchestrator adds that parent keyword
  only after its resolved review policy and all Feature Spec closeout gates pass.
- Local markdown: move this file to `issues/done/<NN>-<slug>.md`, creating
  `issues/done/` on demand after validation and after the selected
  non-uncommitted delivery target has live proof. For orchestrator workspace
  issues, move it only
  after cross-repo integration proof is recorded. Do not delete the file or add
  a `done` status.

## Dependencies

- Depends on: [generated issue IDs and reason, or `None`.]
- Blocks: [generated issue IDs and reason, or `None`.]
```

Include a `## Questions` section only when
`partial_output=allow-non-agent-ready`, and put the concrete human/reporter
question there. Omit
the section entirely for `ready-for-agent` issues; never write `N/A` as a
placeholder question.
