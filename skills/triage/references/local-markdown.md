# Local Markdown Issues

Use this format when `project-memory/agents/issue-tracker.md` says issues live
under `.scratch/`.

## Header Fields

Each issue file should have `Type:` and `Status:` lines near the top:

```markdown
# [Issue Title]

Type: bug | feature | task
Status: needs-triage | needs-info | ready-for-agent | ready-for-human | wontfix
Source PRD: [path, issue number, title, or `None`]
```

Use mapped values from `project-memory/agents/triage-labels.md` if the repo has
custom strings. Keep `Type:` for work kind and `Status:` for workflow state.
`needs-info` means waiting for reporter/requester input; when that input
arrives, re-triage the issue before marking it `ready-for-agent`.
Completion is represented by moving the file into `issues/done/`, not by
adding a `done` status.

## Update Rules

- Preserve existing body content unless the user asks for a rewrite.
- Update an existing `Type:` line in place; otherwise insert it under the
  title.
- Update an existing `Status:` line in place; otherwise insert it near
  `Type:`.
- Append new information under the most specific existing heading.
- If a heading does not exist, append it at the end of the file.
- Keep comments and triage notes summarized; do not paste raw session logs.
- Do not delete completed local issue files. Move them to the configured
  `issues/done/` folder after implementation and validation are complete.

## Standard Sections

```markdown
## Triage Notes

[Evidence and classification rationale.]

## Questions

- [Concrete question for requester or reporter. Required when `Status:
  needs-info`.]

## Agent Brief

[Only present when status is ready-for-agent.]

## Human Handoff

[Only present when status is ready-for-human.]

## Decision

[Only present for wontfix or other explicit decisions.]

## Comments

[Optional summarized conversation history.]
```

For generated feature work, `$to-issues` owns issue-file creation and should
still run `$plan-harder` once per issue. This skill updates or triages existing
local markdown issues.
