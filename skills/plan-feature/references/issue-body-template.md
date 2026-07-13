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
Source PRD: [path, issue number, or stable draft ref; use `draft-prd:<...>`
only for draft command output before hosted mutation, never for agent-ready
implementation issues]

Affected Repos: [include for workspace issues; otherwise omit]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repo issues, `current repository`; for workspace issues, use
`Affected Repos`]

## Delivery

- Delivery mode: [pull-request | direct-commit] ([feature-level, inherited from
  Source PRD] or [issue-level override with authorization reason])
- PR closeout: [merge-ready | draft-only] (feature-level, inherited from Source
  PRD; omit only for direct-commit)
- Parallelization: [independent | depends-on <issue-id>[, <issue-id>] | blocks
  <issue-id>[, <issue-id>] | root-integrated]
- Closeout: [feature-pr-closes-issue | repo-pr-closes-issue |
  direct-commit-closes-issue | local-done-move-after-proof; use
  local-done-move-after-proof for local markdown even with direct-commit
  delivery]
- Integration mode: [omitted when obvious from Source PRD; otherwise
  single-repo-pr | repo-pr | direct-commit]

## Orchestrator Handoff

- Source PRD: [same value as the header `Source PRD` line]
- Feature slug: [authoritative lowercase feature slug]
- Delivery mode: [same effective delivery mode and inheritance or override
  source as `## Delivery`]
- PR closeout: [same effective PR closeout as `## Delivery`, or not-applicable
  for direct-commit]
- Affected repos or product scope: [repo slugs, workspace path, or current
  repository]
- Scope:
  - [Only this issue's implementation slice.]
- Start rule: [independent | depends-on <issue-id>[, <issue-id>] | blocks
  <issue-id>[, <issue-id>] | root-integrated]
- Dependencies: [generated issue IDs and reason, or `None`.]
- Validation: [commands, checks, or proof required for this issue.]
- Domain closeout: [not-applicable | implementation-closeout with the exact
  decisions, target surfaces, evidence, and `$project-memory domain-memory`
  operation required by `## Domain Knowledge Closeout` below]
- Closeout: [feature-pr-closes-issue | repo-pr-closes-issue |
  direct-commit-closes-issue | local-done-move-after-proof; use
  local-done-move-after-proof for local markdown even with direct-commit
  delivery]

Do not include worker authorization modes, worker surfaces, worker counts,
checkpoint approval, publication authority, issue mutation authority, or
orchestration session settings in this section.
`$codex-orchestrator` resolves runtime authorization after registering the
issue as a workstream.

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

[Include only on the final integration task when the Source PRD carries a
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
  `## Delivery`. Use `Closes #<this-issue-number>` only when the PR lives in the
  same GitHub repository as the issue. For orchestrator or cross-repo closeout
  where the PR repository differs from the issue repository, use
  `Closes owner/repo#<this-issue-number>` only when that cross-repo closing path
  is intended and supported; otherwise use non-closing links and record the
  coordination closeout action separately. Final-commit closure requires
  `direct-commit` or another explicit authorization. Do not add the parent PRD
  closing keyword from an individual child issue. For a whole-PRD final feature
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

Include a `## Questions` section only for explicitly authorized partial
`needs-info` output, and put the concrete human/reporter question there. Omit
the section entirely for `ready-for-agent` issues; never write `N/A` as a
placeholder question.
