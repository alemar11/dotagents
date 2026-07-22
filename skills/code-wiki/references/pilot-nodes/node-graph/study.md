# Complete Repository Study

| Field | Value |
| --- | --- |
| `node_id` | `study` |
| `node_kind` | `agent-study` |
| `dependencies` | `prepare` |
| `input_artifacts` | `source`, `wiki/data/inventory.json` |
| `output_artifacts` | `artifacts/study.json` |
| `repair_target` | `none` |

## Instructions

Study the clean repository once and write `artifacts/study.json` with schema
`code-wiki-study`, schema version `1`, the complete ordered `fixed_pages`,
`deep_dives`, and `deep_dives_applicability`. Every page object must contain
only `output_path`, `title`, `purpose`, `claims`, `section_plan`,
`flows_and_lifecycles`, `operations_and_tests`, `failures_and_risks`,
`change_recipes`, `validation`, and `rollback`.
`section_plan` must be a JSON array containing at least two unique nonempty
section-title strings. It is not a topic record and must not contain `status`
or `details` fields.

Each claim contains only `text` and an `evidence` list. Every evidence record
contains only repository-relative POSIX `path`, one-based inclusive `start`,
and `end` integers. Include at least two unique claims and two distinct evidence
records per fixed page, and at least three claims per adaptive deep dive. Topic
records are either `{"status":"covered","details":[...]}` or
`{"status":"not-applicable","reason":"..."}`. Do not encode source evidence
inside prose, Markdown links, or backticks.

Fixed pages must exactly match the prepared page targets in order. When the
prepared scope requires deep dives, include two to five unique leaf HTML pages
under `pages/deep-dives/`, ordered by output path. In that case,
`deep_dives_applicability` must be exactly
`{"status":"applicable","reason":"..."}`. Otherwise use an empty list and
exactly `{"status":"not-applicable","reason":"..."}`. Never use the topic
record fields `covered` or `details` for applicability. Preserve exact source names,
commands, ownership boundaries, and branch conditions. Do not write HTML,
modify the wiki, or leave repository discovery for the render node.
