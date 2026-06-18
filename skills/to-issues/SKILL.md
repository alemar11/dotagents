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
- Embed the returned `$plan-harder` brief into that issue body.
- Do not publish or return an issue as ready for execution until it includes
  the hardened implementation brief.
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
- pasted PRD text,
- another project document that clearly acts as the PRD.

Also inspect:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `CONTEXT.md` or `CONTEXT-MAP.md`,
- `project-memory/adr/`,
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
- list dependencies on earlier issues only when truly needed.

### 3. Harden every issue with `$plan-harder`

For each issue, call `$plan-harder` in issue-hardening mode with only that
issue's draft body and the minimum relevant PRD context.

After `$plan-harder` returns:

- insert its brief under `## Implementation Plan`,
- resolve any blocker it identifies before marking the issue agent-ready,
- keep the issue scoped to the original vertical slice,
- repeat for the next issue.

Do not batch multiple issues into one `$plan-harder` call.

### 4. Apply issue type and triage state

Read `project-memory/agents/triage-labels.md` and map canonical issue types
and triage states to the repo's tracker values.

- Use the canonical `task` type for generated implementation issues unless the
  repo's mapping says otherwise.
- Use `ready-for-agent` only when the issue contains a hardened implementation
  brief, acceptance criteria, validation, and no unresolved blocker.
- Use `needs-info` when an issue has unresolved product or technical questions.
- Use `ready-for-human` when the PRD requires human judgment before an agent can
  proceed.

### 5. Publish or return issues

Use `project-memory/agents/issue-tracker.md` for the target:

- GitHub: create issues with `gh issue create --parent <prd-number>` when the
  PRD source is a GitHub issue, set the mapped `task` issue type when
  available, then apply mapped labels.
- Local markdown: write
  `.scratch/<feature-slug>/issues/<NN>-<slug>.md` with `Type:` and `Status:`
  lines near the top.
- Other tracker: follow the repo-specific instructions.

For GitHub PRDs, every implementation issue must be attached to the PRD issue
as a sub-issue. If an implementation issue is created before the parent
relationship is set, attach it afterward with
`gh issue edit <prd-number> --add-sub-issue <issue-number>`. Keep
`Source PRD: #<prd-number>` in the issue body as well.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

Use this GitHub implementation issue title format:

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

### 6. Report completion

Summarize:

- source PRD,
- number of issues produced,
- GitHub PRD parent issue and sub-issues attached, when applicable,
- where issues were published or that output stayed in chat,
- issue types and labels/statuses assigned,
- any blocked issues and why,
- confirmation that `$plan-harder` was run once per issue.

## Issue Body Shape

Use this shape unless the tracker has a stronger local template:

```markdown
# [Issue Title]

Type: [mapped issue type, usually task]
Status: [mapped triage state]
Source PRD: [path, issue number, or title]

## Goal

[One vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant PRD and repo context.]

## Requirements

- [Requirement this issue must satisfy.]

## Implementation Plan

[Paste the $plan-harder issue-hardening brief here.]

## Acceptance Criteria

- [ ] [Specific, verifiable outcome.]

## Validation

- [Command, test, or manual check.]

## Dependencies

- [Issue dependency or `None`.]
```

## References

- `references/vertical-slices.md`: issue splitting rules.
