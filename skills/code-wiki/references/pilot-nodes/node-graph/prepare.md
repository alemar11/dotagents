# Node-Graph Preparation

| Field | Value |
| --- | --- |
| `node_id` | `prepare` |
| `node_kind` | `prepare` |
| `dependencies` | `none` |
| `input_artifacts` | `source` |
| `output_artifacts` | `wiki`, `wiki/data/inventory.json`, `wiki/data/claim-matrix.json` |
| `repair_target` | `none` |

## Instructions

Create the deterministic repository inventory, claim-matrix scaffold, and HTML
wiki scaffold. This node is implemented by the allowlisted Python preparation
handler and never invokes a model.
