---
name: github-review-threads
description: "Inspect hosted review feedback and perform provider review request, wait, reply, and resolve operations. Posting replies or resolving threads requires authorization."
---

# GitHub Review Threads

Before remote `git`, `gh`, registry, or skill helper commands that contact the
network, use the runtime's narrowest network-enabled context for that command
family. Keep local-only git sandboxed. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

## Role

Own provider review operations for one pull request: inspect threads, request
or wait for reviews, reply, edit comments, submit reviews, and resolve threads
with explicit authority. The caller owns implementing code fixes, local
validation, and acceptance. This skill may require and verify caller-supplied
receipts, fingerprints, and worktree evidence before provider mutations; it
does not implement repository code changes.

For a one-shot hosted Codex review obtain-and-report path, prefer
`$review-pr`, which composes the request/wait operations from this skill.
Use this skill directly for inspect, reply, resolve, ready-check/wait, and
other provider review operations.

Load [references/states.md](references/states.md) before classifying feedback,
review observations, reconciliation, or resolution results.

## Transport and CLI

Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`. Use `<skill-root>/scripts/reviews` for typed review commands and
`<skill-root>/scripts/reviews --json snapshot` for worktree fingerprints, backed by
authenticated `gh`. Keep provider text file-backed and require exact readback.
Never place a title, body, description, reply, or review text in argv or a
shell string.

Before an operation, read the matching section of
[workflows.md](references/workflows.md): review inspection/waiting, thread
listing, replies, resolution, or other authorized discussion writes. Read
[script-summary.md](references/script-summary.md) when exact command/schema
fields or managed `reviews operation` orchestration are needed.

This skill owns immutable one-use mutation reservations and recovery. Preserve
returned identities, fingerprints, and complete receipts; do not reconstruct
thread hashes or substitute raw GraphQL. Preparation and validation do not
authorize execution, and a consumed marker alone never proves provider success.

## Invocation fields

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `review_operation` | `inspect`, `check`, `wait`, `ready-check`, `ready-wait`, `terminal-evidence`, `request`, `comment`, `edit-comment`, `submit-review`, `reply`, `resolve` | none | The one pull-request review operation. `ready-check` and `ready-wait` observe the provider review caused by one typed ready transition; they never post a request. |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | For write-shaped operations, whether to execute or preview. Omit for pure reads. |

Keep the operation separate from its repository and PR reference. Callers must
normalize authorization and phase policy before invocation; reject those
caller-owned fields instead of interpreting them here. Mutating operations
require `mutation_mode=apply`.

## Authorization

- Inspect, check, wait, ready-check, ready-wait, and terminal-evidence are
  read-shaped; they never authorize reply, resolve, or a new review request.
- Post replies, edit comments, submit reviews, or resolve threads only when the
  user explicitly authorizes publication or a calling workflow supplies exact
  PR/action authority.
- Reply only to one returned `finding_comment_ids` entry; resolve by passing the
  typed reply receipt unchanged. Never assemble a GraphQL thread id or
  substitute a top-level PR comment for a thread reply.
- Never accept review evidence from an older head. Preserve returned identities
  and fingerprints; do not blind-retry mutations.

## Workflow

Open [references/workflows.md](references/workflows.md) for the matching
`review_operation`. For a composed workflow, require the exact PR target and one
canonical `review_operation`.

## References

- `references/workflows.md`: inspection, reply, resolution, and direct-command flows.
- `references/states.md`: feedback, review, reconciliation, and resolution states.
- `references/script-summary.md`: `scripts/reviews` command and schema contract.
