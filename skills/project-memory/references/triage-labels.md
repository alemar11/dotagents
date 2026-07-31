# Artifact Markers, Issue Types, And Workflow States

Project Memory is the sole reusable owner of the canonical `artifact_marker`,
`issue_type`, and `workflow_state` fields and values. These are orthogonal
dimensions: an artifact marker identifies a durable planning artifact, issue
type identifies a unit of work, and workflow state identifies its lifecycle
position. The generated
`project-memory/config/triage-labels.md` file is the repository-specific source
of truth that maps those values to actual GitHub labels, issue types, body
fields, and workflow labels. Every mapping row includes an explicit transport
so consumers never infer mutation mechanics from a tracker value.

Consumers such as `$plan-feature` may select or apply these values, but must
load the Project Memory mapping and must not define a competing registry,
aliases, or compatibility syntax.

## Artifact Markers

Artifact marker identifies a durable tracker artifact that is not itself an
implementation issue type.

| Canonical marker | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `idea` | `label` | `idea` | Tentative proposal saved for possible later planning |

Map `artifact_marker: idea` to the `idea` label and leave the native GitHub
Issue Type unset. Marker transport is `label`; reject every other value.

The repository's `project-memory/config/triage-labels.md` must include this
artifact-marker mapping before an Idea can be captured or consumed. A missing
mapping blocks only Idea capture and Idea-source consumption; it does not
invalidate existing issue-type or workflow-state mappings and must not block
unrelated planning or implementation workflows.

If the active GitHub tracker uses `idea` for a conflicting purpose or requires
a different label, load [setup-questions.md](setup-questions.md) and use its
artifact-marker mapping prompt. An unmodified GitHub `idea` label requires no
question.

## Issue Types

Issue type describes what kind of work this is. It should not change often
during an issue's lifetime.

Choose the tracker-specific values before writing this file.

- Use `native-type` when GitHub issue types are available, normally
  with values `Bug`, `Feature`, and `Task`. When they are disabled, use an
  evidence-backed `label` or `body-field` fallback and record its exact label
  or complete body field in each row.
| Canonical type | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `bug` | `native-type` | `Bug` | Something is broken or regressed |
| `feature` | `native-type` | `Feature` | New capability or product enhancement |
| `task` | `native-type` | `Task` | Maintenance, docs, refactor, follow-up, cleanup, or implementation work item |

The table above uses the default GitHub native type names. Rewrite both
`Transport` and `Tracker value` when the tracker uses another supported
representation. `body-field` requires the complete exact line to render, not a
field name or value fragment. Reject a missing transport column, a transport
outside `native-type`, `label`, or `body-field`. When customized or conflicting values remain ambiguous
after tracker inspection, load [setup-questions.md](setup-questions.md) and use
its issue-type mapping prompt.

Use `$gitstack:github-issues` to apply
`native-type` through the type operation, `label` through label mutation, or
`body-field` through the exact authorized final body contract.

## Workflow States

Workflow state describes where the issue is in the workflow. It can change as
information arrives or work becomes ready.

| Canonical state | Transport | Tracker value | Meaning |
| --- | --- | --- | --- |
| `needs-triage` | `label` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info` | `label` | `needs-info` | Waiting on reporter or requester |
| `ready-for-agent` | `label` | `ready-for-agent` | Fully specified and queue-ready; listed dependencies still gate start |
| `ready-for-human` | `label` | `ready-for-human` | Requires human implementation or judgment |
| `wontfix` | `label` | `wontfix` | Will not be actioned |

When a skill mentions a canonical state, require `label` at the GitHub
boundary. Reject missing transports or unsupported transports;
workflow-state body fields and native Issue Types are not supported.

`needs-info` is a waiting state, not an agent queue state. When the reporter or
requester answers, the issue should be re-evaluated as `needs-triage` before it
can move to `ready-for-agent`.

An Idea may have no workflow state when it is saved as a dormant proposal. If
it has a workflow state, the only valid values are `needs-triage` or
`needs-info`, and those states are mutually exclusive. Other workflow states
belong to work items, not Ideas.

`ready-for-agent` can coexist with a `## Dependencies` section. It means the
issue is fully specified enough for the agent queue, not that a queue consumer
may start it before listed dependencies finish. Dependency graphs must stay
acyclic so completed work cannot be locked behind circular prerequisites.

Edit the transport and tracker-value columns to match the vocabulary and
mechanism actually used in this repo's tracker. If GitHub issue types are
disabled for the organization, record the exact issue-type fallback labels or
body-field conventions in the issue-type table; workflow states remain labels.
When customized or conflicting workflow values remain ambiguous after tracker
inspection, load [setup-questions.md](setup-questions.md) and use its
workflow-state mapping prompt.
