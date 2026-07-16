# Codex App Orchestration Gates

## Universal Gates

Before owner-ready or terminal status require:

- scope and acceptance evidence;
- exact mutation authority;
- preserved owner changes and App-managed checkout ownership;
- current diff and focused validation;
- non-trivial `$autoreview` with actionable findings resolved;
- dependency and integration proof;
- merge-ready pull-request proof;
- parent-closeout preparation and external handoff proof;
- no active task, due check, or ready-next action.

## Authorization

Commit, push, PR creation/readiness, issue mutation, review skip, release,
deployment, and target-repo instruction changes each require their canonical
permission and exact scope evidence. Permissions are independent. Read access
and one mutation never imply another. Merge cannot be authorized inside this
skill.

## Managed Checkout Gate

Require App-managed isolated checkout evidence for every repository in the
Feature Spec. Missing checkout proof blocks the run. Do not create raw Git
worktrees, rotate the caller checkout, or transfer implementation to the root.

## Pull Request Gate

The only delivery gate is a merge-ready pull request. Every affected repository
must have a real non-draft PR URL at its current head, all required checks must
pass, current-revision review must be dispositioned, actionable feedback must
be resolved, safe PR metadata and parent-closeout preparation must be complete,
and the PR must be ready to merge. Draft publication is intermediate evidence,
never App completion.

## Review And CI

Current-revision Codex review is required unless the authorized user explicitly
selects `codex_review_requirement=explicitly-skipped-by-authorized-user`. That
skip does not bypass autoreview, CI, issue, integration, or publication gates.

Material diff changes, base-ref changes, or merge-base changes invalidate older
review evidence. Failed CI or actionable review feedback returns the task to
fixing and revalidation.

## Terminal Handoff

Ready-to-merge is terminal for the final portfolio conclusion. Prepare the
parent Feature Spec closing keyword and record it as `armed`, then report the
exact PR, revision, checks, and closeout vehicle. Do not merge, wait for the
final merge, or verify post-merge tracker closure after the terminal report. A
later GitHub workflow owns those actions; `armed` is not closed. During an
unfinished two-Spec stack, let the downstream publish its pre-promotion draft
against the merge-ready upstream branch, then emit the upstream external merge
handoff before waiting. Keep the run nonterminal and observe the externally
completed merge only as dependency evidence for the downstream task.

Multi-repo completion requires every child delivery plus cross-repo integration
proof before this handoff. Release/deployment gates require their separate
authority, artifacts, credentials, and live proof.
