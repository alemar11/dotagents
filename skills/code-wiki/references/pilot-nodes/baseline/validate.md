# Baseline Strict Validation

| Field | Value |
| --- | --- |
| `node_id` | `validate` |
| `node_kind` | `validate` |
| `dependencies` | `baseline-generate` |
| `input_artifacts` | `wiki` |
| `output_artifacts` | `artifacts/validation.json` |
| `repair_target` | `baseline-generate` |

## Instructions

Run the existing Code Wiki validator in strict mode, capture its canonical
result and complete output, and allow at most one bounded rerun of the baseline
generation node when validation fails.
