# Triage Option Contract

Load this reference before classifying or mutating an issue. It is the
canonical registry for issue kind and workflow state.

## Registry

| Field | Allowed values | Notes |
| --- | --- | --- |
| `issue_type` | `bug`, `feature`, `task` | Describes the kind of work. |
| `workflow_state` | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` | Describes the issue lifecycle state. |

`source_prd_ref` is reference data, not an enum. Paths, issue numbers, titles,
classification rationale, labels, and comments are also data.

## Local Markdown Compatibility

Current local Markdown issues emit `issue_type`, `workflow_state`, and
`source_prd_ref` with canonical lower-kebab values for the two enums. Do not
add a schema-version field.

The header metadata region starts after the first H1 title and ends at the
first `##` heading. Read legacy `Type:`, `Status:`, `State:`, and
`Source PRD:` fields only inside that region; never treat similarly named
fields inside `## Agent Brief` or other body sections as issue metadata.

Canonical fields take precedence over every legacy alias, even when the legacy
value disagrees. Stop and report a conflict only when duplicate canonical
fields disagree, or when no canonical field exists and the applicable legacy
aliases disagree. When no canonical `workflow_state` exists, `Status:` is the
first legacy alias and `State:` is the fallback; conflicting header-region
values stop normalization. Normalize in memory during read-only work. During
an authorized mutation, emit exactly one canonical field for each meaning and
remove its header-region legacy aliases; preserve the body and unrelated
metadata.

### Mixed-Field Compatibility Fixture

Given this legacy/canonical mixture:

```markdown
# Example

workflow_state: ready-for-agent
Status: needs-triage

## Agent Brief

State: ready-for-human
```

the canonical `workflow_state` wins over the conflicting header `Status:`.
The embedded `State:` is outside the metadata region and is ignored. A
read-only run returns `workflow_state=ready-for-agent` without editing. An
authorized mutation keeps one `workflow_state: ready-for-agent` line, removes
the header `Status:` alias, and preserves the Agent Brief body unchanged.

If the header instead contains two different `workflow_state:` values, stop.
If it contains no canonical field and has conflicting `Status:` and `State:`
values, stop. Do not rewrite either conflict until the owner resolves it.

GitHub display issue types and workflow labels remain tracker mappings. Branch
on the canonical `issue_type` and `workflow_state`, then translate at the
GitHub boundary.
