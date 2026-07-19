# Complete Repository Study

| Field | Value |
| --- | --- |
| `node_id` | `study` |
| `node_kind` | `agent-study` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki/data/inventory.json` |
| `output_artifacts` | `artifacts/study.md` |
| `repair_target` | `none` |

## Instructions

Study the clean repository once and write the complete page-by-page evidence
brief that the render node will use without another repository study. Include
exactly one `## Page: `<repo-relative-wiki-page>`` section for every required
page listed in the scaffold inventory, in scaffold order. Each page section
must contain at least 120 words, at least two distinct repository-relative
evidence references in bracketed `[path:start-end]` form, and concrete coverage of architecture,
interfaces, lifecycle and state, call flows, operations, tests, failure modes,
change recipes, risks, validation, and rollback as they apply. State explicit
not-applicable findings when the repository has no evidence for a topic.

Preserve exact source names, paths, line ranges, commands, ownership boundaries,
and branch conditions. Explain how the evidence supports each proposed claim
and identify at least two unique ready claims per page. Do not write HTML,
modify the wiki, or leave repository discovery for the render node.
