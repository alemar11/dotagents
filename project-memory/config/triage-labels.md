# Artifact Markers, Issue Types, And Workflow States

## Artifact Markers

| Canonical marker | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `idea` | `label` | `idea` | Tentative proposal saved for possible later planning. |

## Issue Types

| Canonical type | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `bug` | `label` | `bug` | Something is broken or regressed. |
| `feature` | `label` | `enhancement` | New capability or product enhancement. |
| `task` | `label` | `task` | Implementation, maintenance, documentation, refactor, or follow-up work. |

## Workflow States

| Canonical state | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `needs-triage` | `label` | `needs-triage` | Maintainer evaluation is required. |
| `needs-info` | `label` | `needs-info` | Requester information is required. |
| `ready-for-agent` | `label` | `ready-for-agent` | Fully specified and queue-ready after dependencies complete. |
| `ready-for-human` | `label` | `ready-for-human` | Human implementation or judgment is required. |
| `wontfix` | `label` | `wontfix` | The issue will not be actioned. |

All mappings use GitHub labels because this user-owned repository has no
repository-native Issue Type surface. Missing mapped labels are provisioned
only by an explicitly authorized consuming workflow.
