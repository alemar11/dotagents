# Issue Body Template

Use this shape unless the tracker has a stronger local template. Delete optional
delivery lines when they do not apply.

```markdown
# <feature-slug>: <NN> <vertical outcome>

Type: [mapped issue type, e.g. GitHub `Task` or local `task`]
Status: [mapped triage state, usually `ready-for-agent`]
Source PRD: [path, issue number, or stable draft ref]

Affected Repos: [for orchestrator issues, repo slugs or `N/A`]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repo issues, `current repository`; for orchestrator issues, use
`Affected Repos`]

## Delivery

- Delivery mode: [one-feature-branch | one-pr-per-repo | one-pr-per-issue |
  direct-commit] ([feature-level, inherited from Source PRD] or [issue-level
  override with authorization reason])
- Parallelization: [independent | depends-on <issue-id>[, <issue-id>] | blocks
  <issue-id>[, <issue-id>] | root-integrated]
- Closeout: [feature-pr-closes-issue | repo-pr-closes-issue |
  issue-pr-closes-issue | direct-commit-closes-issue |
  local-done-move-after-proof]
- Integration mode: [omitted when obvious from Source PRD; otherwise
  shared-feature-branch | repo-pr | issue-pr | direct-commit | inspect-only]

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant PRD and repo context.]

## Cross-Repo Notes

[For orchestrator issues only: affected repos, interface contracts,
repo PR links or placeholders, and validation order. Use `N/A` for ordinary
single-repo issues.]

## Integration Gates

[For orchestrator issues only: named gates or a link to
`integration-gates.md`, plus proof required before completion. Use `N/A` for
ordinary single-repo issues.]

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

- [Command, test, or manual check.]

## Completion

When all acceptance criteria pass and validation is complete:

- GitHub: close this implementation issue from the relevant PR body with
  `Closes #<this-issue-number>`, following `## Delivery`. Final-commit closure
  requires `direct-commit` or another explicit authorization. Do not close the
  parent PRD unless the maintainer says the whole PRD is complete.
- Local markdown: move this file to `issues/done/<NN>-<slug>.md`, creating
  `issues/done/` on demand. For orchestrator workspace issues, move it only
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
