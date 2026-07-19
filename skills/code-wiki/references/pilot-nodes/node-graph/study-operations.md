# Maintainer Operations Study

| Field | Value |
| --- | --- |
| `node_id` | `study-operations` |
| `node_kind` | `agent-study` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki/data/inventory.json` |
| `output_artifacts` | `artifacts/study-operations.md` |
| `repair_target` | `none` |

## Instructions

Study only tests, CI and operator workflows, source-map ownership, common
change recipes, failure modes, risks, and rollback paths. Produce concise
Markdown for the later synthesis node. Every factual claim must carry exact
repository-relative path and line-range evidence refs. Include exact existing
validation commands and identify missing operational surfaces explicitly. Do
not write HTML or modify the wiki.
