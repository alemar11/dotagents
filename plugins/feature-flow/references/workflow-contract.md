# Feature Flow Workflow Contract

This reference is the canonical owner of semantic GitHub metadata for Feature
Flow. GitStack owns GitHub transport, label administration, pagination,
mutation safety, and read-after-write verification. The bundled skills own when
metadata is read or changed and must not edit this contract at runtime.

## Canonical metadata

### Artifact marker

| Semantic value | GitHub transport | GitHub value | Meaning |
| --- | --- | --- | --- |
| `idea` | `label` | `idea` | The issue is a captured Idea. |

### Issue types

These provider mappings are retained for planning artifacts but are separate
from the workflow-state matrix.

| Semantic type | GitHub transport | GitHub value |
| --- | --- | --- |
| `bug` | native issue type or label | `bug` |
| `feature` | native issue type or label | `enhancement` |
| `task` | native issue type or label | `task` |

### Workflow states

| Label | Applied by | Read by | Removed by | Scope |
| --- | --- | --- | --- | --- |
| `needs-triage` | `idea`, `plan` | `idea`, `plan` | `plan` when lifecycle advances | Idea lifecycle |
| `needs-info` | `plan` | `plan` | `plan` when blockers are resolved | Idea lifecycle |
| `ready-for-agent` | `plan` | `plan` | executor-owned after planning | Implementation issue readiness |

## Lifecycle rules

- `idea` is applied to every durable Idea and is never applied to an
  implementation issue.
- `needs-triage` and `needs-info` are mutually exclusive.
- A captured Idea is dormant by default; `needs-triage` is added only when the
  user explicitly queues it for evaluation.
- `needs-info` is applied only when Plan has unresolved information required to
  continue planning.
- `ready-for-agent` belongs only to implementation issues after Plan has
  produced a complete, hardened issue contract.
- `implement-feature` currently does not read or enforce this contract.

## Ownership matrix

| Skill | Applies | Reads | Does not own |
| --- | --- | --- | --- |
| `idea` | `idea`, optional `needs-triage` | Idea marker and queue state | Feature Specs, implementation issues, planning transitions |
| `plan` | `needs-triage`, `needs-info`, `ready-for-agent` | All active metadata | GitHub transport |
| `implement-feature` | none | none currently | Feature metadata enforcement |
