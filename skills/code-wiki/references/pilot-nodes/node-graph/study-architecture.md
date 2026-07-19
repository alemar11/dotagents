# Architecture Study

| Field | Value |
| --- | --- |
| `node_id` | `study-architecture` |
| `node_kind` | `agent-study` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki/data/inventory.json` |
| `output_artifacts` | `artifacts/study-architecture.md` |
| `repair_target` | `none` |

## Instructions

Study only repository scope, architecture, module ownership, runtime state,
lifecycles, and basic and advanced call flows. Produce concise Markdown for the
later synthesis node. Every factual claim must carry one or more exact
repository-relative path and line-range evidence refs. Identify public versus
internal boundaries and concrete state or cleanup owners. Do not write HTML or
modify the wiki.
