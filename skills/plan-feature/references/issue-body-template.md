# Issue Body Template

Use this shape unless the tracker has a stronger local template. Delete optional
delivery lines when they do not apply. Evidence references in issue bodies must
be portable: use repo-relative paths, sibling-repo-relative paths, hosted issue
or PR URLs, or descriptive references. Do not include developer-machine absolute
paths in returned bodies, local issue files, hosted issue bodies, or draft
publish commands.

```markdown
# <feature-slug>: <NN> <vertical outcome>

Type: [mapped issue type, e.g. GitHub `Task` or local `task`]
Status: [mapped triage state, usually `ready-for-agent`]
source_prd_ref: [path, issue number, or stable draft ref; draft refs are valid
only in non-mutating output before hosted mutation]

Affected Repos: [include for workspace issues; otherwise omit]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repo issues, `current repository`; for workspace issues, use
`Affected Repos`]

## Delivery

- delivery_mode: [pull-request | direct-commit]
- delivery_source: [feature-level-inherited | issue-level-override]
- delivery_source_evidence: [source_prd_ref for pull-request; every effective
  direct-commit issue uses
  owner-ref=<ref>;scope-ref=issue:<NN>;target-ref=<preserved-feature-or-source-ref>;target-branch=<branch_name>;
  inherited direct-commit also adds scope-transfer-ref=run]
- issue_mutation_authority: [none | pr-body-closeout-only |
  explicit-direct-mutation]
- issue_mutation_authority_evidence: [source PRD/ref or none; for
  explicit-direct-mutation, the same exact issue scope/target/branch/transfer
  tokens as delivery_source_evidence plus the independently preserved owner-ref
  that authorizes final-commit issue closure]
- branch_name: [inherited feature branch or exact authorized direct-commit
  target branch]
- pr_shape: [single-pr | per-repo-pr | none]
- pr_closeout: [merge-ready | draft-only | not-applicable]
- parallelization: [independent | depends-on | blocks | root-integrated]
- dependency_ids: [issue ids or none]
- blocked_issue_ids: [issue ids or none]
- closeout_mode: [feature-pr-closes-issue | repo-pr-closes-issue |
  direct-commit-closes-issue | local-done-move-after-proof; use
  local-done-move-after-proof for local markdown even with direct-commit
  delivery]
- integration_mode: [single-repo-pr | repo-pr | direct-commit | not-applicable]

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
- parallelization: [independent | depends-on | blocks | root-integrated]
- dependency_ids: [generated issue IDs or none]
- blocked_issue_ids: [generated issue IDs or none]
- dependency_reason: [reason or none]
- validation: [commands, checks, or proof required for this issue.]
- domain_closeout: [not-applicable | implementation-closeout]
- domain_closeout_data: [when applicable, the exact
  decisions, target surfaces, evidence, and `$project-memory domain-memory`
  operation required by `## Domain Knowledge Closeout` below]
- closeout_mode: [feature-pr-closes-issue | repo-pr-closes-issue |
  direct-commit-closes-issue | local-done-move-after-proof; use
  local-done-move-after-proof for local markdown even with direct-commit
  delivery]
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
  - Invoke `$project-memory` with the `domain-memory` slice after the integrated
    behavior is proven. Project Memory must run its internal domain-modeling
    workflow; reading `project-memory/agents/domain.md` or editing the targets
    directly is not a substitute.

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
  only after its final current-head review and all PRD closeout gates pass.
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
