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
- issue/source closeout proof;
- no active task, due check, or ready-next action.

## Authorization

Commit, push, PR creation/readiness, issue mutation, review skip, merge, release,
deployment, and target-repo instruction changes each require their canonical
permission and exact scope evidence. Permissions are independent. Read access
and one mutation never imply another.

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

## Merge And Source Closeout

Merge is root-owned and unavailable by default. It requires permission for the
named PR and the configured confirmation behavior. Parent Feature Spec closure
is prepared before merge but verified only after merge and actual tracker
closure. `armed` is not closed.

Multi-repo completion requires every child delivery plus cross-repo integration
proof. Release/deployment gates require their separate authority, artifacts,
credentials, and live proof.
