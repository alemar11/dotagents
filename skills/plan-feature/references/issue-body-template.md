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
source_prd_ref: [path, issue number, or stable draft ref; draft refs are valid
only in non-mutating output before hosted mutation]

Affected Repos: [include for workspace issues; otherwise omit]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repo issues, `current repository`; for workspace issues, use
`Affected Repos`]

## Option Resolution

issue_option_rows_fingerprint: [verified fingerprint over this issue's rows
below]

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `issue:<NN>:<field>` | `issue:<NN>` | [Per-Issue Registry field or `branch_name`] | [verified value or data] | [verified canonical source] | [verified portable evidence or `none` only when allowed] |

Expand the row above into exactly one row for every Per-Issue Registry field
plus the issue-effective `branch_name` row. Preserve the verified six-column
cells; do not infer or omit row metadata here.

## Delivery

- delivery_mode: [verified `delivery_mode` row value]
- delivery_source: [verified `delivery_source` row value]
- delivery_source_evidence: [verified delivery evidence data]
- issue_mutation_authority: [verified `issue_mutation_authority` row value]
- issue_mutation_authority_evidence: [verified independent mutation evidence data]
- branch_name: [verified exact branch data]
- pr_shape: [verified `pr_shape` row value]
- pr_closeout: [verified `pr_closeout` row value]
- parallelization: [verified `parallelization` row value]
- dependency_ids: [issue ids or none]
- blocked_issue_ids: [issue ids or none]
- closeout_mode: [verified `closeout_mode` row value]
- integration_mode: [verified `integration_mode` row value]

## Orchestrator Handoff

- source_prd_ref: [same value as the header `source_prd_ref` line]
- feature_slug: [authoritative lowercase feature slug]
- delivery_mode: [same effective value as `## Delivery`]
- delivery_source: [same canonical value as `## Delivery`]
- delivery_source_evidence: [same evidence as `## Delivery`]
- issue_mutation_authority: [same effective value as `## Delivery`]
- issue_mutation_authority_evidence: [same evidence as `## Delivery`]
- branch_name: [same effective branch data as `## Delivery`]
- pr_shape: [same effective value as `## Delivery`]
- pr_closeout: [same effective value as `## Delivery`]
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
- closeout_mode: [same verified value as `## Delivery`]
- integration_mode: [same effective value as `## Delivery`]

Do not include worker authorization modes, worker surfaces, worker counts,
checkpoint approval, publication authority, or orchestration session settings
in this section. The source-contract `issue_mutation_authority` does not grant a
worker permission; `$codex-orchestrator` validates and projects it after
registering the issue as a workstream.

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant PRD and repo context using portable references only.]

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

[Include only on the final integration task when the source_prd_ref carries a
required domain-knowledge handoff. This task must also prove integrated feature
behavior; never use this section to justify a docs-only issue.]

- Required workflow:
  - Invoke `$project-memory` with `memory_slice=domain-memory` and
    `domain_operation=implementation-closeout` after the integrated behavior is
    proven. Project Memory must run its internal domain-modeling workflow;
    reading `project-memory/config/domain.md` or editing the targets directly
    is not a substitute.

- Decisions:
  - [Accepted durable term, rule, boundary, or decision carried from the PRD.]
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
  `closeout_mode`. Use `Closes #<this-issue-number>` only when the PR lives in the
  same GitHub repository as the issue. For orchestrator or cross-repo closeout
  where the PR repository differs from the issue repository, use
  `Closes owner/repo#<this-issue-number>` only when that cross-repo closing path
  is intended and supported; otherwise use non-closing links and record the
  coordination closeout action separately. Final-commit closure requires
  `closeout_mode=direct-commit-closes-issue`,
  `issue_mutation_authority=explicit-direct-mutation`, and its exact scoped
  authorization evidence. Do not add the parent PRD closing keyword from an individual child
  issue. For a whole-PRD final feature
  or integration PR, the root delivery orchestrator adds that parent keyword
  only after its resolved review policy and all PRD closeout gates pass.
- Local markdown: move this file to `issues/done/<NN>-<slug>.md`, creating
  `issues/done/` on demand after validation and, for `direct-commit`, after the
  commit/proof is recorded. For orchestrator workspace issues, move it only
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
