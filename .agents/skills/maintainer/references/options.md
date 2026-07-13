# Maintainer Option Contract

Load this reference before producing a maintenance closeout. It is the
canonical registry for result choices that control downstream closeout.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `result` | `pass`, `fail` | Derived from required validation gates | Findings and failure explanations remain separate data. |
| `change_state` | `changed`, `no-change` | Derived from the persistent diff | `no-change` represents a run with no persistent edits. |

Emit both fields. A successful no-op is `result=pass` plus
`change_state=no-change`; a successful maintenance update is `result=pass`
plus `change_state=changed`. Human output may capitalize a display label, but
callers branch only on the assigned canonical values.
