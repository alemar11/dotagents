---
name: github-projects
description: "Manage GitHub Projects, fields, items, links, and lifecycle for users or organizations."
---

# GitHub Projects

Before remote `gh` commands, use the runtime's narrowest network-enabled
context. Verify `gh` is runnable (`command -v gh`, `gh --version`) and
authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Before Projects work,
also verify `gh project --help` and `gh project <required-command> --help`.
A pure Projects read requires `read:project` or `project`; a mutation requires
`project`. Treat restricted-environment network failures as inconclusive. Do
not install or refresh `gh` without explicit authorization. Network permission
is not mutation authority.

Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`. Use authenticated `gh project` directly; do not route through a
shared multi-domain CLI.

## Invocation fields

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | For write-shaped operations, whether to execute or preview. Omit for pure reads. |
| `project_operation` | `create`, `copy`, `edit`, `close`, `reopen`, `delete`, `mark-template`, `unmark-template`, `link-repository`, `unlink-repository`, `link-team`, `unlink-team`, `create-field`, `delete-field`, `add-item`, `create-draft-item`, `edit-draft-item`, `set-item-field`, `clear-item-field`, `archive-item`, `unarchive-item`, `delete-item` | none | The one GitHub Projects mutation. Pure project, field, and item reads omit it. |

| Input evidence | Canonical invocation |
| --- | --- |
| List, view, or filter GitHub Projects, fields, or items | Omit `project_operation` and `mutation_mode` |
| Explicit GitHub Projects mutation with an exact owner and target or complete creation input | Matching `project_operation` plus `mutation_mode=apply` |
| `dry run`, `preview only`, `local only`, or `do not mutate` | `mutation_mode=dry-run` |

Accept a canonical user or organization Project URL or an explicit owner plus
project number. Keep free-form provider fields file-backed. Independently read
mutations back and reconcile uncertain effects before retrying.

Read [references/workflows.md](references/workflows.md) for operations and
[references/states.md](references/states.md) when interpreting results.
Callers must normalize planning policy before invocation; reject caller-owned
planning, tracker, orchestration, delivery, permission, or phase fields.
