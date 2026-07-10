# Agent Brief

Use this shape when an issue is marked `ready-for-agent`. `$plan-harder` must
first run in issue-hardening mode on its caller surface for this same issue.
Merge its structured result into this shape without duplicating issue sections.

The brief should be durable enough for a later agent to execute without
re-reading the whole discussion. Keep it concrete, evidence-backed, and scoped
to the issue. Do not include broad implementation doctrine, raw logs, secrets,
or rejected options unless the rejection prevents repeat mistakes.

## Required Qualities

- One issue, one outcome.
- Clear current behavior or starting state.
- Clear desired behavior or finished state.
- Explicit non-goals and dependency notes.
- Acceptance criteria that can be checked.
- Validation commands or manual checks when known.
- Open questions must be empty before the issue is `ready-for-agent`.
- Dependencies may be present; `ready-for-agent` means queue-ready, not
  start-now when listed dependencies are incomplete.

## Template

```markdown
## Agent Brief

Type: bug | feature | task
State: ready-for-agent

### Summary

[One or two sentences describing the work outcome.]

### Current Context

- [Relevant current behavior, code area, docs, PRD, or issue link.]

### Desired Outcome

- [What should be true after the issue is complete.]

### Scope

- [Included work.]
- [Excluded work.]

### Implementation Notes

- [Hardened plan from $plan-harder, preserving issue scope.]

### Acceptance Criteria

- [ ] [Specific verifiable result.]

### Validation

- [Command, test, or manual check.]

### Dependencies

- [Dependency or `None`.]
```

If `$plan-harder` identifies a blocker, do not publish this brief as
`ready-for-agent`. Move the issue to `needs-info` only when the next action is
a concrete question for the reporter/requester; otherwise move it to
`ready-for-human` when human judgment, authority, or access is required.
Summarize the blocker instead of publishing an agent brief.
