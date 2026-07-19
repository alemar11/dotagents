# Wiki Rendering

| Field | Value |
| --- | --- |
| `node_id` | `render` |
| `node_kind` | `agent-render` |
| `dependencies` | `prepare`, `synthesize` |
| `input_artifacts` | `source`, `wiki`, `wiki/data/inventory.json`, `wiki/data/claim-matrix.json`, `artifacts/synthesis.md` |
| `output_artifacts` | `wiki`, `wiki/data/claim-matrix.json` |
| `repair_target` | `none` |

## Instructions

Render the supplied synthesis into the existing Code Wiki scaffold. Replace
all placeholders, write developer-grade source-backed content for every
required page, fill the claim matrix with unique ready claims, preserve the
shipped CSS and JavaScript contract, and add deterministic local SVG diagrams
when useful. Use only evidence from the synthesis and clean snapshot. Do not
invoke image generation. Ensure all local links and evidence chips are valid.
