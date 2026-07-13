# Local Markdown Issues

Use this format when `project-memory/agents/issue-tracker.md` says issues live
as local markdown. Local issue roots may be repo-local `.scratch/<feature>/`
folders or orchestrator workspace
`projects/<project>/features/<feature>/` folders.

## Header Fields

Each issue file should have canonical metadata lines near the top:

```markdown
# [Issue Title]

issue_type: bug | feature | task
workflow_state: needs-triage | needs-info | ready-for-agent | ready-for-human | wontfix
source_prd_ref: [path, issue number, stable ref, or none]
```

Use the canonical values from `references/options.md`. GitHub display mappings
do not change local persisted values.
`needs-info` means waiting for reporter/requester input; when that input
arrives, re-triage the issue before marking it `ready-for-agent`.
`ready-for-agent` means queue-ready; listed dependencies still gate when work
can start.
Completion is represented by moving the file into `issues/done/`, not by
adding a `done` status.

For orchestrator workspace issues, preserve additional fields such as
`Affected Repos:` and sections such as `## Cross-Repo Notes` or
`## Integration Gates`.

## Update Rules

- Preserve existing body content unless the user asks for a rewrite.
- Update an existing `issue_type:` line in place; otherwise insert it under the
  title.
- Update an existing `workflow_state:` line in place; otherwise insert it near
  `issue_type:`.
- Preserve or add `source_prd_ref:` as reference data.
- Apply the header-region scope, canonical precedence, conflict stop, and
  authorized normalization rules from `references/options.md`. Do not read or
  rewrite similarly named fields inside issue-body sections.
- Append new information under the most specific existing heading.
- If a heading does not exist, append it at the end of the file.
- Keep comments and triage notes summarized; do not paste raw session logs.
- Do not delete completed local issue files. Move them to the configured
  `issues/done/` folder after implementation and validation are complete. For
  orchestrator workspace issues, move only after cross-repo integration proof
  is recorded. Create `issues/done/` on demand when completing the first issue.

## Standard Sections

```markdown
## Triage Notes

[Evidence and classification rationale.]

## Questions

- [Concrete question for requester or reporter. Required when
  `workflow_state: needs-info`.]

## Agent Brief

[Only present when `workflow_state: ready-for-agent`.]

## Human Handoff

[Only present when `workflow_state: ready-for-human`.]

## Decision

[Only present for wontfix or other explicit decisions.]

## Comments

[Optional summarized conversation history.]
```

For generated feature work, `$plan-feature` owns issue-file creation and should
still run `$plan-harder` once per issue. This skill updates or triages existing
local markdown issues.
