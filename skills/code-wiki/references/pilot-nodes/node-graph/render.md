# Wiki Rendering

| Field | Value |
| --- | --- |
| `node_id` | `render` |
| `node_kind` | `agent-render` |
| `dependencies` | `prepare`, `study` |
| `input_artifacts` | `wiki`, `wiki/data/inventory.json`, `wiki/data/claim-matrix.json`, `artifacts/study.md` |
| `output_artifacts` | `wiki`, `wiki/data/claim-matrix.json` |
| `repair_target` | `none` |

## Instructions

Render the supplied page-by-page study brief into the existing Code Wiki scaffold. Replace
all placeholders, write developer-grade source-backed content for every
required page, fill the claim matrix with unique ready claims, preserve the
shipped CSS and JavaScript contract, and add deterministic local SVG diagrams
when useful. Use only claims and exact evidence already present in the study
brief; the source snapshot is deliberately not a declared input, so do not
rediscover or restudy the repository or introduce unsupported claims. Do not
invoke image generation. Ensure all local links and evidence chips are valid.
