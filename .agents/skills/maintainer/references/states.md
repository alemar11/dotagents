# Maintainer State Contract

Load this reference before routing a request or producing a maintenance
closeout. It is the canonical registry for Maintainer-owned route and derived
result state. These values are transient workflow facts: Maintainer does not
persist them, and Git, validation, or publication state remains external
evidence.

## Route mode

| Value | Meaning |
| --- | --- |
| `maintain` | Run conservative general maintenance, a targeted package upgrade, or metadata alignment according to the matched scope. |
| `audit` | Inspect skill or repository health, policy, structure, or pre-release evidence read-only. |
| `instruction-density` | Review behavior-preserving compaction opportunities and stop for approval before edits. |
| `description-review` | Review discovery descriptions or metadata wording. |
| `workflow-hardening` | Repair a connected workflow defect established by runtime or cross-skill evidence. |
| `package-lifecycle` | Merge, rename, move, bundle, replace, or retire a package. |
| `codex-deps` | Audit Codex dependency and portability boundaries. |
| `codex-tool-surface` | Compare live Codex orchestration capabilities with the semantic runtime contracts. |
| `refresh` | Run one explicitly selected domain refresh workflow. |
| `okf-spec` | Compare or explicitly refresh the bundled OKF specification. |

Select one or more route modes from the request using
`maintenance-router.md`. Mixed requests preserve that router's canonical
execution order; route selection never widens mutation authority.

## Closeout result

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `result` | `pass`, `fail` | Derived from required validation gates | `pass` means no required gate failed; findings and failure explanations remain separate data. |
| `change_state` | `changed`, `no-change` | Derived from the persistent diff | `changed` means the authorized workflow left a persistent edit; `no-change` means it did not. |

Emit both fields. A successful no-op is `result=pass` plus
`change_state=no-change`; a successful maintenance update is `result=pass`
plus `change_state=changed`. Human output may capitalize a display label, but
callers branch only on the assigned canonical values.
