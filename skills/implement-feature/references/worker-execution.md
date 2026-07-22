# End-To-End Worker Execution

The worker executes one assigned Feature Spec end to end in the
ChatGPT-created worktree assigned to its visible Codex task. It owns issue
sequence, technical design, implementation and rewrites,
repairs, tests, validation, commits, AutoReview, Codex review, tracker progress,
and final evidence. With `github-pr` it also owns push, PR creation and updates,
CI, and provider review fixes. With `local-branch` it performs none of those
provider operations.

Before implementation, verify or create/select the declared named branch in the
managed worktree. Detached HEAD, another branch, or a dirty baseline blocks
until the worker safely establishes the contract inside its own worktree. Never
switch the original/main worktree and never treat the managed worktree alone as
durable delivery.

Before each issue, after recovery, and before final verification:

1. read the current Feature Spec and complete issue graph;
2. compare the stable fields from `feature-spec-contract.md` directly;
3. accept compatible operational changes and continue autonomously;
4. stop declaratively as `blocked-durable-contract` if a stable field changed.

Do not ask the user or root for implementation, validation, recovery, retry,
publication, review-fix, or blocker authority. The startup grant already covers
in-contract work. Choose safe, maintainable approaches and coherent rewrites.
Respect the accepted material attempt budget and required validation result.

Use target-repository instructions for commits and validation. Use current
GitStack workflows only for required GitHub operations. Run `$autoreview`
after focused validation, verify every finding in the real code, fix accepted
findings, and revalidate changed evidence. Run the required current-head Codex
review and resolve actionable feedback. Never force-push published history,
merge, enqueue, deploy, release, or perform post-merge closure.

Follow `tracker-checklists.md` for every issue and parent checkbox. If later work
invalidates proof, uncheck it and read back the correction.

The successful result must match `delivery_type`. `github-pr` returns
`pr-ready-for-merge-but-not-merged` with PR/provider/CI and mergeability proof.
`local-branch` returns `local-branch-ready` with exact repository and checkout
identity, named target branch and HEAD, base branch and base SHA ancestry, clean
worktree, current-head validation and reviews, committed tracker readback, no
unresolved recorded task/Goal changes, warnings, and changed paths. Coherent progress needs
no root intervention.

## Dedicated Integration Worker

This is another visible Codex task only when Plan Feature produced a dedicated
integration Feature Spec. Its bootstrap supplies every prerequisite repository,
branch, HEAD, and authoritative managed-worktree path plus the complete start,
wiring, port, health, E2E, budget, evidence, cleanup, and terminal contract. The
worker launches and cleans up components itself, rereads every input HEAD before
and after validation, and proves the exact complete SHA vector. Any drift makes
all prior integration proof stale. It returns an upstream-owned defect as
evidence to root for routing; root never selects or implements the fix. After a
partial worker produces a new HEAD, rerun the complete integration proof.
