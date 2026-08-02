# SE Workflow Contract

This reference is the canonical owner of semantic GitHub metadata for Software
Project. G owns GitHub transport, label administration, pagination,
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
| `bug` | `label` | `bug` |
| `feature` | `label` | `enhancement` |
| `task` | `label` | `task` |

### Workflow states

| Label | Applied by | Read by | Removed by | Scope |
| --- | --- | --- | --- | --- |
| `needs-info` | `plan` | `plan` | `plan` when blockers are resolved | Idea lifecycle |
| `ready-for-agent` | `plan` | `plan`, `implement` | executor-owned after planning | Implementation issue readiness |

## Lifecycle rules

- `idea` is applied to every durable Idea and is never applied to an
  implementation issue.
- A captured Idea has no workflow-state label by default.
- `needs-info` is the only workflow-state label allowed on an Idea and is
  applied only when Feature has unresolved information required to continue
  planning.
- `ready-for-agent` belongs only to implementation issues after Feature has
  produced a complete, hardened issue contract.
- Every final implementation issue must carry `ready-for-agent` before
  `implement` may claim or schedule the Feature Spec.
- `implement` reads and enforces the gate but never applies or repairs the
  label.

## Ownership matrix

| Skill | Applies | Reads | Does not own |
| --- | --- | --- | --- |
| `idea` | `idea` | Idea marker | Feature Specs, implementation issues, planning transitions |
| `plan` | `needs-info`, `ready-for-agent` | All active metadata | GitHub transport |
| `implement` | none | `ready-for-agent` as the execution gate | Label application and taxonomy |
