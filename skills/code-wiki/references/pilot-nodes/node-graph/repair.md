# Bounded Wiki Repair

| Field | Value |
| --- | --- |
| `node_id` | `repair` |
| `node_kind` | `agent-repair` |
| `dependencies` | `validate` |
| `input_artifacts` | `source`, `wiki`, `wiki/data/claim-matrix.json`, `artifacts/validation.json` |
| `output_artifacts` | `wiki`, `wiki/data/claim-matrix.json` |
| `repair_target` | `validate` |

## Instructions

Apply one bounded repair pass to the generated wiki using only the complete
strict-validation output supplied below and the existing source evidence. Fix
each concrete validator failure without broad rewrites, new scope, unsupported
claims, or source mutation. Update the claim matrix only when required by the
same validation failure. The runner will execute strict validation exactly one
more time and will not retry again.
