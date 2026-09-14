---
name: github-review-threads
description: "Inspect PR review feedback or request, wait for, reply to, and resolve hosted reviews."
---

# GitHub Review Threads

Manage hosted review operations for one exact repository and PR using
GitHub CLI directly. This skill ships no CLI. The caller owns code changes,
local testing, publication, and acceptance of findings. For a one-shot hosted
Codex review request and result, prefer `$review-pr`, which composes this skill.

## Scope and authorization

Resolve the repository, PR, current full HEAD SHA, and requested operation.
Read-only inspection never authorizes posting, requesting a review, changing
review state, or resolving threads. An explicit request for one of those actions
authorizes that action within its stated scope; retain caller authorization
without another confirmation. Preview requests prepare text and targets only.

For composed calls, retain `review_operation` (`inspect`, `check`, `wait`,
`ready-check`, `ready-wait`, `terminal-evidence`, `request`, `comment`,
`edit-comment`, `submit-review`, `reply`, or `resolve`). Write-shaped operations
use `mutation_mode=apply` when authorized and `dry-run` otherwise; omit it for
pure reads. These are caller inputs, not saved configuration.

Use authenticated `gh` in an execution context with the required network access.
Check its availability and active account before hosted operations. Do not
install, upgrade, or change credentials incidentally. Report unavailable access
without treating it as evidence about the PR.

## Execution

Read the applicable section of [workflows.md](references/workflows.md) for
inspection, review requests and waits, or discussion writes. Use
[states.md](references/states.md) for review states and the resumable review
record shared with callers.

Keep free-form text in UTF-8 files or serialized JSON request files passed to
`gh api --input`. Never interpolate provider text into shell commands. Inspect
the final text before writing and read the exact provider object afterward.

Use only IDs returned by GitHub for the verified PR. A review thread, inline
comment, conversation comment, and formal review are different objects.
Recheck the expected PR HEAD immediately before and after mutations. Stop and
report drift rather than applying old evidence to a new commit. If a write
may already have applied, reconcile the exact target before any retry; an
unconfirmed result never authorizes a duplicate write.

Return the PR and full observed HEAD, operation performed, exact object links,
verified result or remaining uncertainty, and the review record when waiting
or resuming. Review completion is not proof of CI, merge readiness, or code
acceptance.
