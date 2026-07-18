# Issue Types And Workflow States

Project Memory is the sole reusable owner of the canonical `issue_type` and
`workflow_state` fields and values. The generated
`project-memory/config/triage-labels.md` file is the repository-specific source
of truth that maps those values to actual GitHub issue types and labels. Local
Markdown persists the canonical values directly.

Consumers such as `$plan-feature` may select or apply these values, but must
load the Project Memory mapping and must not define a competing registry,
aliases, or compatibility syntax.

## Issue Types

Issue type describes what kind of work this is. It should not change often
during an issue's lifetime.

Choose the tracker-specific values before writing this file. Do not copy the
GitHub examples into local markdown modes.

- GitHub backend: use native issue types when available, normally `Bug`,
  `Feature`, and `Task`.
- Local backend: emit canonical `bug`, `feature`, and `task`.

| Canonical type | Tracker value | Meaning |
| --- | --- | --- |
| `bug` | `Bug` | Something is broken or regressed |
| `feature` | `Feature` | New capability or product enhancement |
| `task` | `Task` | Maintenance, docs, refactor, follow-up, cleanup, or implementation work item |

The table above uses the default GitHub type names. Rewrite the right-hand
`Tracker value` cells only when the actual GitHub tracker uses different
values. When customized or conflicting values remain ambiguous after tracker
inspection, load [setup-questions.md](setup-questions.md) and use its issue-type
mapping prompt.

In GitHub issue-tracker mode, use `$gitstack:github-issues` to apply native GitHub
Issue Type values when available.

In local markdown mode, record the canonical value as an `issue_type:` line
near the top of the issue file.

## Workflow States

Workflow state describes where the issue is in the workflow. It can change as
information arrives or work becomes ready.

| Canonical state | Label or status in our tracker | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue |
| `needs-info` | `needs-info` | Waiting on reporter or requester |
| `ready-for-agent` | `ready-for-agent` | Fully specified and queue-ready; listed dependencies still gate start |
| `ready-for-human` | `ready-for-human` | Requires human implementation or judgment |
| `wontfix` | `wontfix` | Will not be actioned |

When a skill mentions a canonical state, use the corresponding GitHub label
from this table at the hosted boundary. In local markdown mode, record the
canonical value as a `workflow_state:` line near the top of the issue file.

`needs-info` is a waiting state, not an agent queue state. When the reporter or
requester answers, the issue should be re-evaluated as `needs-triage` before it
can move to `ready-for-agent`.

`ready-for-agent` can coexist with a `## Dependencies` section. It means the
issue is fully specified enough for the agent queue, not that a queue consumer
may start it before listed dependencies finish. Dependency graphs must stay
acyclic so completed work cannot be locked behind circular prerequisites.

Edit the right-hand columns to match the vocabulary actually used in this
repo's tracker. If GitHub issue types are disabled for the organization, record
the fallback labels or body-field convention here.
When customized or conflicting workflow values remain ambiguous after tracker
inspection, load [setup-questions.md](setup-questions.md) and use its
workflow-state mapping prompt.

## Local Markdown Validation

The header metadata region starts after the first H1 title and ends at the
first `##` heading. Require exactly one `issue_type` and one `workflow_state`
line in that region. Reject missing fields, unknown aliases, noncanonical
values, or conflicting duplicate canonical fields. Do not add a schema-version
field, and never treat similarly named fields in issue-body sections as header
metadata.

For a Plan-generated issue, keep `source_spec_ref` only in the canonical
`## Execution Contract` row. Never duplicate it in the header. A
`source_spec_ref` beginning with `proposed-spec:` is proposal-only and cannot
receive an applied `workflow_state: ready-for-agent` value.
