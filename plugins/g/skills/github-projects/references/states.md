# GitHub Projects State Contract

GitHub Project lifecycle, visibility, template state, fields, values, linked
repositories or teams, item content, and archival state remain external
provider state. This skill persists no G-owned state.

Each Projects mutation returns exactly one transient
`project_operation_result`:

| Value | Meaning |
| --- | --- |
| `previewed` | Exact target and input were resolved without a provider mutation. |
| `no-op` | The pre-read already proved the requested state. |
| `verified` | Exact readback proved the requested state after mutation. |
| `failed` | The provider definitively rejected the attempted mutation. |
| `unavailable` | Capability, scope, access, or exact target resolution prevented an attempt. |
| `unknown` | The mutation may have applied or exact readback remained inconclusive. |

A multi-item request returns one result per authorized operation rather than
one aggregate state.
