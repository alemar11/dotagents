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
- Use the authoritative feature slug in this order: explicit slug from a
  composing skill, PRD file path directory, configured tracker path, then PRD
  title-derived slug as a fallback only.
- Inherit delivery mode from the PRD. The PRD is the canonical place for the
  full branch and PR strategy, but every generated issue must copy the effective
  feature-level `Delivery mode` label for cross-session scheduling. Mark it as
  inherited from `Source PRD` unless the issue has an explicit owner-authorized
  issue-level exception.
- Build and persist a feature-level `execution-plan.md` for execution sequencing.
  It should own issue-level ordering, dependency waves, and unlock conditions so
  issues can stay implementation-focused. Keep this file at feature scope (e.g.
  `.scratch/<feature-slug>/` or `projects/<project>/features/<feature>/`), not
  under `issues/`.
- Treat local file write authorization and external issue-tracker mutation
  authorization as separate permissions.

## Boundaries

- Do not implement the issues.
- Do not rewrite the PRD unless the user explicitly asks for a PRD update.
- Do not create horizontal layer tickets such as "backend only", "frontend
  only", or "tests only" when a vertical slice is practical.
- Ask for confirmation before writing local issue files or publishing to a
  hosted issue tracker unless the user explicitly asked to write/publish or a
  composing skill passes explicit run authorization after resolving gates.

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

Resolve and carry the planning identity before splitting:

- `feature_slug`: explicit handoff value first, then the PRD directory slug,
  then title-derived fallback only when no accepted path exists.
- For multi-context repos or monorepos: `product_slug`, `workspace_path`, and
  `context_file`.
- For orchestrator workspaces: `project_slug` and affected repos.
- `delivery_mode`: inherit from the PRD `## Delivery Mode` section. If
  the PRD lacks it, infer `One Feature Branch` only for unambiguous single-repo
  or monorepo work and `One PR Per Repo` only for unambiguous orchestrator or
  cross-repo work; otherwise stop and require the PRD delivery mode to be resolved.

If a multi-context local-markdown repo lacks an accepted product/context or the
feature slug can collide with another product according to tracker
conventions, stop and resolve that identity before writing issues.

Review PRD open questions before splitting. If any open question affects
scope, acceptance criteria, dependencies, validation, publication target,
permissions, data contracts, or cross-repo contracts, treat it as a blocker
instead of creating `ready-for-agent` issues.

### 2. Split into vertical issues

Use `references/vertical-slices.md` to create a proposed issue list.
Apply vertical slicing whenever practical. Order issues for sequential agentic
implementation, and make dependencies explicit rather than relying on issue
numbering.

Before hardening, build one `execution-plan.md` for the feature from the proposed
issue list:

- `delivery-mode`: inherited from the PRD and copied in each issue.
- ordered issue map with `<NN>` and short intent.
- dependency graph plus `blocks` / `depends on` intent.
- wave gates and unblock conditions.
- repo-level boundaries and integration proof requirements (for orchestrator work).

Write this plan as a local artifact when local file writes are permitted:

- local-markdown: `.scratch/<feature-slug>/execution-plan.md`
- orchestrator-local: `projects/<project-slug>/features/<feature-slug>/execution-plan.md`
- if local writes are disallowed, return the equivalent execution plan in-chat and
  include the intended path for the next run.

Every issue should:

- deliver a user-visible or system-verifiable increment,
- include enough context to be implemented without rereading the whole PRD,
- include product/workspace/context scope for monorepo work, or affected repos
  and integration gates for orchestrator work,
- include a durable `Source PRD` pointer, copied feature-level delivery mode,
  issue-level parallelization, dependencies, closeout, and any delivery or
  integration exception,
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

- `Tracker mode: github`: create issues through `$github-issues`, attach them
  to the PRD parent when the PRD source is a GitHub issue, set the mapped
  `task` issue type when available, then apply mapped labels.
- `Tracker mode: orchestrator-github`: create vertical feature issues in the
  configured coordination repo through `$github-issues`, using the PRD parent
  relationship and the required `<project-slug>` label. Derive
  `<project-slug>` from the PRD/project context or ask for it, ensure the label
  exists in the coordination repo, and apply it to every generated vertical
  feature issue. Repo-local implementation PRs or child issues are linked from
  the coordination issue; repo-local child issues are optional in v1.
- `Tracker mode: local-markdown`: write to the configured repo-local issue
  path, normally `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, with `Type:`
  and `Status:` lines near the top and a heading that follows the local issue
  title convention `<feature-slug>: <NN> <vertical outcome>`. Use the
  authoritative feature slug from the handoff or PRD path; derive it from the
  PRD title only when no accepted slug/path exists.
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
issue is created before the parent relationship is set, use `$github-issues` to
attach it afterward. Keep `Source PRD: #<prd-number>` in the issue body as
well.

For GitHub coordination PRDs, every generated vertical feature issue must share
the same project label as the PRD parent issue, named exactly `<project-slug>`.
This label is separate from issue type and workflow-state labels.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

For orchestrator workspace issues, include affected repos, cross-repo contract
notes, integration gates by name or link, repo-local PR or implementation issue
links, and the proof required before the issue can move to `done` or close.
Repo PR links may be placeholders before implementation when the issue is
otherwise agent-ready, but completion must require replacing them with real PR
links or recording equivalent integration proof.

Every published or returned issue must preserve cross-session scheduling
metadata without duplicating the full PRD branch and PR details:

- `Execution plan`: required when local artifacts are written; path to
  `execution-plan.md` in the feature artifact folder.
  If local writes are disallowed, include the inline execution plan in the
  completion summary and a target plan path for the next run.
- `Source PRD`: required. Prefer a stable GitHub issue number or local PRD path.
- `Delivery mode`: required. Copy the effective value from the PRD and mark it
  as feature-level, such as `One Feature Branch (feature-level, inherited from
  Source PRD)`. Feature-level means the mode applies to the whole Source PRD
  feature, not only this generated issue. For an exception, record the
  issue-level override and authorization reason, such as `One PR Per Issue
  (issue-level override, authorized by <owner/date>)`.
- `Parallelization`: required. Use `independent`, `depends on <issue>`,
  `blocks <issue>`, or `root-integrated`.
- `Closeout`: required. State the concrete completion path, such as `feature PR
  closes issue`, `repo PR closes issue`, `issue PR closes issue`, `direct commit
  closes issue`, or `local done move after proof`.
- `Integration mode`: optional for ordinary issues that inherit from the PRD.
  Include it when the issue is cross-repo, exceptional, or otherwise not obvious
  from the PRD delivery mode.

For ordinary single-repo or monorepo `One Feature Branch` issues, the
`## Delivery` section can be as small as:

```markdown
## Delivery

- Delivery mode: One Feature Branch (feature-level, inherited from Source PRD)
- Parallelization: independent
- Closeout: feature PR closes issue
```

Every published or returned issue must also say what happens when the work is
complete:

- GitHub: when all acceptance criteria pass and validation is complete, close
  the implementation issue from the relevant PR body with a GitHub closing
  keyword such as `Closes #<this-issue-number>`. For `One Feature Branch`, the
  feature PR closes the issue; for `One PR Per Repo`, the relevant repo PR
  closes the repo-local issue, while coordination issues close only after repo
  PR links or equivalent integration proof are recorded; for `One PR Per
  Issue`, the issue PR closes the issue. Use final-commit closure only when the
  Source PRD or this issue's `## Delivery` section records `Direct Commit` or
  another explicit maintainer authorization for final-commit closeout. Do not
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

- `<feature-slug>` is the authoritative lowercase kebab-case slug from the
  composing skill, PRD path, or configured tracker target. Derive it from the
  PRD title without the `PRD:` prefix only as a fallback.
- `<NN>` is the two-digit sequence from the vertical issue ordering.
- `<vertical outcome>` is a short imperative or outcome phrase, without a
  trailing period.

Example: `team-invitations: 02 Accept invitation into team`.

If the user did not ask to publish and no composing skill passed explicit run
authorization, return the hardened issue bodies in chat.
If a composing skill such as `$plan-feature` passes explicit run
authorization, use the effective target from that handoff without re-asking
unless this skill finds a new blocker or unresolved question. Do not treat
"local file writes allowed" as permission to mutate GitHub or another hosted
tracker.
If the configured target is GitHub or GitHub coordination but external mutation
is not authorized for the current run, do not mutate GitHub. Ask
`$github-issues` for exact draft publish commands and return them with the
hardened issue bodies, or use the configured local dry-run target if
`project-memory/agents/issue-tracker.md` records one.
When a blocker or unresolved question appears under `$plan-feature`, return it
as an issue-splitting gate instead of publishing a `needs-info` issue by
default.

### 6. Report completion

Summarize:

- source PRD,
- authoritative `feature_slug`,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- delivery mode inherited,
- execution-plan file path when written, or inline plan summary when not persisted,
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

Use this shape unless the tracker has a stronger local template. Delete optional
delivery lines when they do not apply.

```markdown
# <feature-slug>: <NN> <vertical outcome>

Type: [mapped issue type, usually task]
Status: [mapped triage state]
Source PRD: [path, issue number, or title]
Execution plan: [path to execution-plan.md or inline plan reference]

Affected Repos: [for orchestrator issues, repo slugs or `N/A`]

Product Scope: [for monorepos, workspace path and selected context file; for
single-repo issues, `current repository`; for orchestrator issues, use
`Affected Repos`]

## Delivery

- Delivery mode: [One Feature Branch | One PR Per Repo | One PR Per Issue |
  Direct Commit] ([feature-level, inherited from Source PRD] or [issue-level
  override with authorization reason])
- Parallelization: [independent | depends on <issue> | blocks <issue> |
  root-integrated]
- Closeout: [feature PR closes issue | repo PR closes issue | issue PR closes
  issue | direct commit closes issue | local done move after proof]
- Integration mode: [omit when obvious from Source PRD; otherwise shared
  feature branch | repo PR | issue PR | direct commit with authorization reason]

## Execution Plan

- Reference: `execution-plan.md`
- If local files are written, keep full sequencing and unlock conditions there; the
  issue needs only dependency and parallelization fields.
- If files are not written in this run, include the same plan in the final report and
  keep this section as the pointer to that inline execution plan.

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
  `Closes #<this-issue-number>`, following the closeout path in `## Delivery`.
  Final-commit closure is allowed only when the Source PRD or `## Delivery`
  records `Direct Commit` or another explicit maintainer authorization. Do not
  close the parent PRD issue unless the maintainer explicitly says the whole PRD
  is complete. The closing keyword takes effect when the PR or authorized commit
  reaches the default branch.
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
