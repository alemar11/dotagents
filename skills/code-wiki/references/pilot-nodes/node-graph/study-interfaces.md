# Interfaces Study

| Field | Value |
| --- | --- |
| `node_id` | `study-interfaces` |
| `node_kind` | `agent-study` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki/data/inventory.json` |
| `output_artifacts` | `artifacts/study-interfaces.md` |
| `repair_target` | `none` |

## Instructions

Study only public interfaces, entrypoints, dependencies, build/runtime
boundaries, and recurring code patterns. Produce concise Markdown for the
later synthesis node. Every factual claim must carry exact
repository-relative path and line-range evidence refs. Explain callers,
callees, compatibility surfaces, and intended extension points. Do not write
HTML or modify the wiki.
