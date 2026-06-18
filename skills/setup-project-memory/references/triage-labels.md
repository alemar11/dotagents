# Triage Labels

The skills speak in terms of canonical issue types and canonical triage states.
This file maps those canonical values to the actual GitHub issue types, labels,
or local markdown values used in this repo's issue tracker.

## Issue Types

Issue type describes what kind of work this is. It should not change often
during an issue's lifetime.

| Canonical type | Tracker value | Meaning |
| --- | --- | --- |
| `bug` | `Bug` | Something is broken or regressed |
| `feature` | `Feature` | New capability or product enhancement |
| `task` | `Task` | Maintenance, docs, refactor, follow-up, cleanup, or implementation work item |

The table above uses the default GitHub type names. For local markdown
tracking, prefer lowercase tracker values (`bug`, `feature`, `task`) unless the
repo already uses title case.

In GitHub issue-tracker mode, use native GitHub Issue Type when available:
`gh issue edit <number> --type "<Tracker value>"`.

In local markdown mode, record the mapped value as a `Type:` line near the top
of the issue file.

## Triage States

Triage state describes where the issue is in the workflow. It can change as
information arrives or work becomes ready.

| Canonical state | Label or status in our tracker | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info` | `needs-info` | Waiting on reporter or requester |
| `ready-for-agent` | `ready-for-agent` | Fully specified, ready for an agent |
| `ready-for-human` | `ready-for-human` | Requires human implementation or judgment |
| `wontfix` | `wontfix` | Will not be actioned |

When a skill mentions a canonical state, use the corresponding tracker label or
status from this table. In GitHub mode, these are usually labels. In local
markdown mode, record the mapped value as a `Status:` line near the top of the
issue file.

`needs-info` is a waiting state, not an agent queue state. When the reporter or
requester answers, the issue should be re-evaluated as `needs-triage` before it
can move to `ready-for-agent`.

Edit the right-hand columns to match the vocabulary actually used in this
repo's tracker. If GitHub issue types are disabled for the organization, record
the fallback labels or body-field convention here.
