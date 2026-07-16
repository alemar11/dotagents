# Managed Multi-Repository App Workspace

Load this reference only for `repository_layout=multi-repository-workspace`.

## Ownership

The parent workspace owns the orchestration graph, shared ledger, cross-repo
dependencies and gates, parent closeout, and final status. Child repositories
own their code, project memory, validation, branches, commits, pull requests,
and tracker closeout.

## Managed Task Workspace

Create one visible App task per Feature Spec, not per repository. That task owns
every affected child implementation and repository PR. Before implementation,
prove that the App-managed task workspace exposes a distinct isolated checkout
for every required child repository and record repo id, path, branch, Git
top-level, and baseline.

If the App cannot supply the complete managed checkout map, abort the App run
as blocked before edits. Do not use owner checkouts, raw helper worktrees,
branch rotation, or one task per child repository as fallback.

## Scheduling And Closeout

The run-wide maximum remains three Feature Specs across the workspace. Safe
parallelism requires isolated managed checkout maps and no conflicting
repository/branch ownership. Dependencies, dirty or missing checkouts, absent
authority, and cross-repo gates override parallelism.

The task executes cross-repo integration validation, PR review/fix/CI loops,
and merge-ready preparation. Successful App completion requires one real,
non-draft, ready-to-merge PR per affected repository plus cross-repo integration
proof. The root reconciles proof, owns any authorized
merge, verifies child and parent issue closure, and closes the parent source
only after every child outcome and integration gate passes.
