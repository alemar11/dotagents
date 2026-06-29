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

## Orchestrator Handoff

- Source PRD: [same value as the header `Source PRD` line]
- Feature slug: [authoritative lowercase feature slug]
- Delivery mode: [same effective delivery mode and inheritance or override
  source as `## Delivery`]
- Affected repos or product scope: [repo slugs, workspace path, or current
  repository]
- Scope:
  - [Only this issue's implementation slice.]
- Start rule: [independent | depends-on <issue-id>[, <issue-id>] | blocks
  <issue-id>[, <issue-id>] | root-integrated]
- Dependencies: [generated issue IDs and reason, or `None`.]
- Validation: [commands, checks, or proof required for this issue.]
- Closeout: [feature-pr-closes-issue | repo-pr-closes-issue |
  issue-pr-closes-issue | direct-commit-closes-issue |
  local-done-move-after-proof]

Do not include worker authorization modes, worker surfaces, worker caps,
checkpoint approval, auto-approval policy, publication authority, or issue
mutation authority in this section. Do not copy values from
`project-memory/agents/orchestration-policy.md` into generated issues.
`$codex-orchestrator` resolves runtime authorization after registering the
issue as a workstream.

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant PRD and repo context using portable references only.]

## Cross-Repo Notes

[For orchestrator issues only: affected repos, interface contracts,
existing repo PR links, expected repo PR slots or pre-implementation
placeholders, and validation order. Use `N/A` for ordinary single-repo issues.
Placeholders are scheduling expectations, not completion proof; orchestrator
closeout records real PR links or equivalent integration proof.]

## Integration Gates

[For orchestrator issues only: named integration gates or a link to
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

- GitHub: close this implementation issue from the relevant PR body, following
  `## Delivery`. Use `Closes #<this-issue-number>` only when the PR lives in the
  same GitHub repository as the issue. For orchestrator or cross-repo closeout
  where the PR repository differs from the issue repository, use
  `Closes owner/repo#<this-issue-number>` only when that cross-repo closing path
  is intended and supported; otherwise use non-closing links and record the
  coordination closeout action separately. Final-commit closure requires
  `direct-commit` or another explicit authorization. Do not close the parent PRD
  unless the maintainer says the whole PRD is complete.
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
