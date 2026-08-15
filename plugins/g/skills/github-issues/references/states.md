# GitHub Issues State Contract

This reference owns the derived result of one native issue dependency
operation. The result is transient output. GitHub issue lifecycle and the
`blockedBy`/`blocking` relationship sets remain external provider state;
temporary body files are transport artifacts, not workflow state.

## Native dependency result

| Value | Meaning | Terminal |
| --- | --- | --- |
| `verified` | The authorized mutation completed and both reciprocal reads prove the requested edge state. | Yes |
| `no-op` | Both pre-reads already proved the exact requested edge state, so no mutation was attempted. | Yes |
| `failed` | GitHub definitively rejected the mutation. | Yes |
| `unavailable` | Capability, authentication, access, or target resolution prevented an operation attempt. | Yes |
| `unknown` | The mutation may have happened or reciprocal readback remains inconclusive after one bounded reread. | Yes |

Return exactly one value per invocation. Never replay an ambiguous mutation to
change `unknown`; the composing caller decides whether any non-success value
blocks its wider workflow.
