# Triage Option Contract

Load this reference before classifying or mutating an issue. It is the
canonical registry for issue kind and workflow state.

## Registry

| Field | Allowed values | Notes |
| --- | --- | --- |
| `issue_type` | `bug`, `feature`, `task` | Describes the kind of work. |
| `workflow_state` | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` | Describes the issue lifecycle state. |

`source_spec_ref` is reference data, not an enum. Paths, issue numbers, titles,
classification rationale, labels, and comments are also data.

## Local Markdown Validation

Current local Markdown issues emit `issue_type`, `workflow_state`, and
`source_spec_ref` with canonical lower-kebab values for the two enums. Do not
add a schema-version field.

The header metadata region starts after the first H1 title and ends at the
first `##` heading. Require exactly one `issue_type`, `workflow_state`, and
`source_spec_ref` field in that region. Reject unknown aliases, missing fields,
or conflicting duplicate canonical fields. Never treat similarly named fields
inside `## Agent Brief` or other body sections as issue metadata.

GitHub display issue types and workflow labels remain tracker mappings. Branch
on the canonical `issue_type` and `workflow_state`, then translate at the
GitHub boundary.
