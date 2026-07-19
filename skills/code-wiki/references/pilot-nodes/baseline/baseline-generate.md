# Baseline Wiki Generation

| Field | Value |
| --- | --- |
| `node_id` | `baseline-generate` |
| `node_kind` | `agent-baseline` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki`, `wiki/data/inventory.json`, `wiki/data/claim-matrix.json` |
| `output_artifacts` | `wiki`, `wiki/data/claim-matrix.json` |
| `repair_target` | `none` |

## Instructions

Execute the complete Code Wiki workflow supplied below in this one generation
context. Study the clean repository, replace every scaffold placeholder, fill
the claim matrix with unique source-backed ready claims, and produce the full
required static HTML wiki. Use deterministic local SVG diagrams only; this
pilot does not use image generation. All evidence chips must use real paths and
precise line ranges from the snapshot. Write only under the declared wiki
output. On a bounded second attempt, use the supplied strict-validation output
to repair the same wiki without broadening scope.
