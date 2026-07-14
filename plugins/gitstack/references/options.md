# GitStack Option Registry

Use these canonical fields for behavior-affecting choices shared by GitStack
skills and the plugin CLI. Field names are `snake_case`; assigned values are
lower-kebab. User phrases may explain or select an option, but consumers must
branch on the resolved value.

## GitStack-owned options

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | Whether an authorized GitHub operation executes or only returns a preview. |
| `issue_operation` | `create`, `edit`, `set-type`, `remove-type`, `create-label`, `add-label`, `remove-label`, `comment`, `attach-parent`, `remove-parent`, `add-sub-issue`, `remove-sub-issue`, `close`, `reopen` | none | The one issue lifecycle operation being requested. |
| `commit_operation` | `commit-only`, `commit-and-push`, `push-only` | none | The local Git operation owned by Git Commit. |
| `review_state` | `not-requested`, `acknowledged`, `pending`, `clean`, `findings`, `stale` | none | The current-head automated-review state returned by `gitstack reviews`. |
| `release_operation` | `inspect`, `create-tag`, `draft`, `publish`, `upload-asset`, `delete` | `inspect` | The requested tag or GitHub Release lifecycle operation. |
| `refactor_disposition` | `required`, `optional`, `not-required` | `not-required` | Whether a deep review recommends a larger refactor. |

Keep data separate from these values. For example, pair
`refactor_disposition` with `refactor_shape`, and pair an operation with its
issue, PR, release, label, or relationship reference in a separate field.

## Boundary normalization

| Input evidence | Canonical result |
| --- | --- |
| `commit`, `commit this`, or `create a commit` | `commit_operation=commit-only` |
| `commit and push` | `commit_operation=commit-and-push` |
| `push-only` | `commit_operation=push-only` |
| `dry run`, `draft only`, `local only`, or `do not mutate` | `mutation_mode=dry-run` |
| Explicit create, edit, publish, post, close, or reopen instruction for an exact target | `mutation_mode=apply` plus the matching operation |

Resolve natural-language instructions to canonical values. Structured callers
must use the registry directly; reject unknown fields or values.
Factual envelope fields such as `ok: true`, GitHub API fields, CLI flags, and
other externally owned syntax are not option values and remain unchanged.

## Caller-owned authorization

GitStack does not own planning or orchestration authority. When Codex
Orchestrator calls GitHub Review Threads, require
`change_delivery_permission=granted-for-selected-target`, the exact PR target,
and the requested operation in `delivery_allowed_actions` or
`worker_allowed_actions`. The caller remains the source of truth for those
fields.
