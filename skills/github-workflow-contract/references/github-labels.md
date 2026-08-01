# GitHub Feature Workflow Metadata

This contract is the current metadata surface for the GitHub feature workflow
in this repository. All rows use GitHub labels because the repository does not
expose a native GitHub Issue Type surface.

## Artifact Marker

| Canonical value | GitHub transport | GitHub value | Meaning |
| --- | --- | --- | --- |
| `idea` | `label` | `idea` | Tentative proposal saved for later planning. |

An Idea is an open, untyped issue titled `Idea: <Name>`. It retains the `idea`
label when later planning closes it after verified full coverage.

## Issue Types

| Canonical value | GitHub transport | GitHub value | Meaning |
| --- | --- | --- | --- |
| `bug` | `label` | `bug` | Broken or regressed behavior. |
| `feature` | `label` | `enhancement` | New capability or product enhancement. |
| `task` | `label` | `task` | Implementation, maintenance, documentation, refactor, or follow-up work. |

Issue-type labels describe the work kind. They are independent from workflow
state labels and must not be copied into issue bodies as substitute metadata.

## Workflow States

| Canonical value | GitHub transport | GitHub value | Meaning |
| --- | --- | --- | --- |
| `needs-triage` | `label` | `needs-triage` | Maintainer evaluation is required. |
| `needs-info` | `label` | `needs-info` | Requester information is required. |
| `ready-for-agent` | `label` | `ready-for-agent` | Fully specified and queue-ready after dependencies complete. |
| `ready-for-human` | `label` | `ready-for-human` | Human implementation or judgment is required. |
| `wontfix` | `label` | `wontfix` | The issue will not be actioned. |

`needs-triage` and `needs-info` are mutually exclusive on Ideas. A dormant
Idea has neither workflow state. An Idea may enter `needs-triage` only when the
user explicitly queues it; open questions in the body do not imply
`needs-info`.

`ready-for-agent` belongs to implementation issues, not Ideas. It can coexist
with unfinished dependencies, but a worker must wait for those dependencies
before starting.

## Lifecycle Ownership

| Workflow | Reads or writes |
| --- | --- |
| Capture Idea | `idea`; optional `needs-triage`. |
| Plan Feature | `idea`, `needs-triage`, `needs-info`, `feature`, `task`, `ready-for-agent`. |
| Implement Feature | None currently; see the companion skill boundary. |

These values are feature-workflow data, not Project Context configuration. If a
future repository or plugin needs a different GitHub contract, it must provide
an explicit replacement contract to its consuming skills rather than restoring
a Project Context metadata registry.
