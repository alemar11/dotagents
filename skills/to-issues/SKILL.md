---
name: to-issues
description: Split a PRD into vertical, agent-ready implementation issues. Use when the user asks to turn a PRD into issues, create vertical slices, or prepare issue-tracker work from a PRD; this skill must use $plan-harder for every issue before returning or publishing it.
---

# To Issues

## Goal

Turn a PRD into vertical implementation issues that can be assigned to agents or
humans. Every generated issue must be hardened with `$plan-harder` before it is
returned or published.

## Hard Requirements

- Load and follow `$plan-harder` for every issue.
- Pass exactly one issue at a time to `$plan-harder` in issue-hardening mode.
- Use the returned `$plan-harder` brief to enrich agent-ready issue bodies:
  synthesize implementation guidance under `## Implementation Plan` and merge
  acceptance, validation, dependency, and blocker details into the matching
  top-level sections. If `$plan-harder` identifies an unresolved blocker,
  preserve that blocker in the withheld result or explicitly authorized
  partial issue instead.
- Do not publish or return an issue as ready for execution until it includes
  the hardened implementation guidance and provenance line.
- Include a `## Completion` section in every generated implementation issue.
- Do not use `needs-info` as a normal output state for generated
  implementation issues. Treat unresolved product, domain, dependency, or
  acceptance-criteria questions as blockers to resolve before publishing,
  unless the user explicitly asks for partial non-agent-ready backlog output.
- Remember that `$plan-harder` is chat-output-only. It must not write files;
  this skill owns any issue tracker or local markdown writes.

## Boundaries

- Do not implement the issues.
- Do not rewrite the PRD unless the user explicitly asks for a PRD update.
- Do not create horizontal layer tickets such as "backend only", "frontend
  only", or "tests only" when a vertical slice is practical.
- Ask for confirmation before writing local issue files or publishing to a
  hosted issue tracker unless the user explicitly asked to write/publish or a
  composing skill passes explicit write authorization after resolving gates.

## Workflow

### 1. Load inputs

Find or ask for the PRD source:

- `.scratch/<feature-slug>/PRD.md`,
- a GitHub PRD issue,
- `projects/<project-slug>/features/<feature-slug>/PRD.md`,
- a GitHub coordination-repo PRD issue,
- pasted PRD text,
- another project document that clearly acts as the PRD.

Also inspect:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `CONTEXT.md` or `CONTEXT-MAP.md`,
- `project-memory/adr/`,
- orchestrator workspace docs such as `projects/<project>/PROJECT.md`,
  `projects/<project>/repos/*.md`, and feature `integration-gates.md` when
  the tracker config uses orchestrator mode,
- nearby source files, tests, and docs relevant to the PRD.

If there is no PRD-quality source, stop and ask the user to provide one or run
`$to-prd` first.

### 2. Split into vertical issues

Use `references/vertical-slices.md` to create a proposed issue list.
Apply vertical slicing whenever practical. Order issues for sequential agentic
implementation, and make dependencies explicit rather than relying on issue
numbering.

Each issue should:

- deliver a user-visible or system-verifiable increment,
- include enough context to be implemented without rereading the whole PRD,
- have clear non-goals,
- include acceptance criteria and validation,
- list dependencies on earlier issues only when truly needed,
- avoid circular dependencies that can lock the queue.

### 3. Harden every issue with `$plan-harder`

For each issue, call `$plan-harder` in issue-hardening mode with only that
issue's draft body and the minimum relevant PRD context.

After `$plan-harder` returns:

- add concise implementation guidance under `## Implementation Plan` only when
  the issue is ready for the queue,
- add the first line under that heading as:
  `Plan-hardening: $plan-harder issue-hardening pass completed for this issue only.`,
- merge non-duplicative details from the hardening brief into the issue's
  top-level acceptance criteria, validation, dependencies, context, and
  blocker sections as appropriate,
- resolve any blocker it identifies before marking the issue agent-ready,
- keep the issue scoped to the original vertical slice,
- repeat for the next issue.

Do not paste the `$plan-harder` output wholesale when it would create nested or
duplicated sections such as a second acceptance-criteria list.
Do not batch multiple issues into one `$plan-harder` call.
If a blocker cannot be resolved from the PRD, repo evidence, or project memory,
stop and return the blocker instead of publishing an agent-ready issue.

### 4. Apply issue type and triage state

Read `project-memory/agents/triage-labels.md` and map canonical issue types
and triage states to the repo's tracker values.

- Use the canonical `task` type for generated implementation issues unless the
  repo's mapping says otherwise.
- Use `ready-for-agent` only when the issue contains hardened implementation
  guidance, acceptance criteria, validation, and no unresolved blocker.
  Dependencies may still be listed; in that case, the issue is queue-ready but
  must not be started until its dependencies are complete.
- Do not create dependency cycles. Every dependency graph must be acyclic so a
  set of ready issues cannot retain-cycle itself into a locked queue.
- Use `needs-info` only for explicitly requested partial backlog output where
  the next action is a concrete question for a human/reporter. Do not count
  `needs-info` issues as agent-ready, and do not publish them from a composing
  skill such as `$plan-feature` unless that composing skill explicitly permits
  partial output.
- Use `ready-for-human` when the PRD requires human judgment before an agent can
  proceed.

### 5. Publish or return issues

Use `project-memory/agents/issue-tracker.md` for the target:

- `Tracker mode: github`: create issues with
  `gh issue create --parent <prd-number>` when the PRD source is a GitHub
  issue, set the mapped `task` issue type when available, then apply mapped
  labels.
- `Tracker mode: orchestrator-github`: create vertical feature issues in the
  configured coordination repo with
  `gh issue create --repo <owner>/<repo> --parent <prd-number> --label "<project-slug>"`.
  Derive `<project-slug>` from the PRD/project context or ask for it, ensure
  the label exists in the coordination repo, and apply it to every generated
  vertical feature issue. Repo-local implementation PRs or child issues are
  linked from the coordination issue; repo-local child issues are optional in
  v1.
- `Tracker mode: local-markdown`: write to the configured repo-local issue
  path, normally `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, with `Type:`
  and `Status:` lines near the top and a heading that follows the local issue
  title convention `<feature-slug>: <NN> <vertical outcome>`.
- `Tracker mode: orchestrator-local`: write to
  `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md`
  with `Type:` and `Status:` lines near the top and a heading that follows the
  local issue title convention `<feature-slug>: <NN> <vertical outcome>`.
  Create the project/feature directories only when writing the actual feature
  artifacts, not during setup.
  `$to-issues` owns the issue files and reads `PROJECT.md`, `repos/*.md`, and
  `integration-gates.md`; it does not create or refresh those supporting files
  unless the user explicitly asks for that broader orchestrator artifact update.
- Other tracker: follow the repo-specific instructions.

For GitHub PRDs and GitHub coordination PRDs, every generated implementation or
vertical feature issue must be attached to the PRD issue as a sub-issue. If an
issue is created before the parent relationship is set, attach it afterward
with `gh issue edit <prd-number> --add-sub-issue <issue-number-or-url>`. Keep
`Source PRD: #<prd-number>` in the issue body as well.

For GitHub coordination PRDs, every generated vertical feature issue must share
the same project label as the PRD parent issue, named exactly `<project-slug>`.
This label is separate from issue type and workflow-state labels.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

For orchestrator workspace issues, include affected repos, cross-repo contract
notes, integration gates, repo-local PR or implementation issue links, and the
proof required before the issue can move to `done` or close.

Every published or returned issue must also say what happens when the work is
complete:

- GitHub: when all acceptance criteria pass and validation is complete, close
  the implementation issue from the implementation PR body or final commit
  message with a GitHub closing keyword such as `Closes #<this-issue-number>`.
  The issue closes when that PR or commit reaches the default branch. Do not
  close the parent PRD issue from an implementation issue unless the maintainer
  explicitly says the whole PRD is complete.
- Local markdown: when all acceptance criteria pass and validation is complete,
  create `issues/done/` on demand if needed, then move the issue file to the
  configured `issues/done/<NN>-<slug>.md` path. For orchestrator workspace
  issues, do this only after cross-repo integration proof is recorded. Do not
  delete the file and do not add a `done` status.

Use this implementation issue title format for both GitHub issue titles and
local markdown issue headings:

```text
<feature-slug>: <NN> <vertical outcome>
```

- `<feature-slug>` is lowercase kebab-case derived from the PRD title without
  the `PRD:` prefix.
- `<NN>` is the two-digit sequence from the vertical issue ordering.
- `<vertical outcome>` is a short imperative or outcome phrase, without a
  trailing period.

Example: `team-invitations: 02 Accept invitation into team`.

If the user did not ask to publish and no composing skill passed explicit write
authorization, return the hardened issue bodies in chat.
If a composing skill such as `$plan-feature` passes explicit write
authorization, use the configured target without re-asking unless this skill
finds a new blocker or unresolved question.
If the configured target is GitHub or GitHub coordination but external mutation
is not authorized for the current run, do not call `gh` mutation commands.
Return the hardened issue bodies and exact publish commands in chat, or use the
configured local dry-run target if `project-memory/agents/issue-tracker.md`
records one.
When a blocker or unresolved question appears under `$plan-feature`, return it
as an issue-splitting gate instead of publishing a `needs-info` issue by
default.

### 6. Report completion

Summarize:

- source PRD,
- number of issues produced,
- GitHub PRD parent issue and sub-issues attached, when applicable,
- where issues were published or that output stayed in chat,
- issue types and labels/statuses assigned,
- completion instruction included,
- any blocked issues and why,
- whether any non-agent-ready partial issues were withheld or explicitly
  published as `needs-info` / `ready-for-human`,
- confirmation that `$plan-harder` was run once per issue, that each issue
  includes the standard plan-hardening provenance line, and that the hardening
  output was merged into the issue without duplicated sections.

## Issue Body Shape

Use this shape unless the tracker has a stronger local template:

```markdown
# <feature-slug>: <NN> <vertical outcome>

Type: [mapped issue type, usually task]
Status: [mapped triage state]
Source PRD: [path, issue number, or title]

Affected Repos: [for orchestrator issues, repo slugs or `N/A`]

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant PRD and repo context.]

## Cross-Repo Notes

[For orchestrator issues only: affected repos, interface contracts,
integration gates, repo PR links, and validation order. Use `N/A` for ordinary
single-repo issues.]

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

When implementation and validation are complete:

- GitHub: close this implementation issue from the implementation PR body or
  final commit message with `Closes #<this-issue-number>`. Do not close the
  parent PRD issue unless the maintainer explicitly says the whole PRD is
  complete. The closing keyword takes effect when the PR or commit reaches the
  default branch.
- Local markdown: move this file to
  the configured `issues/done/<NN>-<slug>.md` path, creating `issues/done/` on
  demand if needed. For orchestrator workspace issues, move it only after
  cross-repo integration proof is recorded. Do not delete the file and do not
  add a `done` status.

## Dependencies

- [Issue dependency or `None`.]
```

Include a `## Questions` section only for explicitly authorized partial
`needs-info` output, and put the concrete human/reporter question there. Omit
the section entirely for `ready-for-agent` issues; never write `N/A` as a
placeholder question.

## References

- `references/vertical-slices.md`: issue splitting rules.
