# End-To-End Worker Execution

The worker executes one assigned Feature Spec end to end in the
ChatGPT-created worktree assigned to its visible Codex task. It owns issue
sequence, technical design, implementation and rewrites,
repairs, tests, validation, commits, the AutoReview-owned review gate, tracker
progress, and final evidence. With `github-pr` it also owns push, PR creation
and updates, CI, and provider review fixes. With `local-branch` it performs none of those
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
GitStack workflows only for required GitHub operations. Finish implementation,
focused validation, tracker checkbox/readback work, and the coherent committed
candidate HEAD before invoking `$autoreview`. AutoReview owns
`review_profile=standard|high-risk`; only its `high-risk` path adds one native
current-head Codex review. Verify and aggregate findings before fixing them,
then revalidate changed evidence and use AutoReview fix verification. Never
force-push published history, merge, enqueue, deploy, release, or perform
post-merge closure.

Follow `tracker-checklists.md` for every issue and parent checkbox. If later work
invalidates proof, uncheck it and read back the correction. Restore and commit
that proof before the next AutoReview fix verification; do not create a
tracker-only post-review HEAD.

The successful result must match `delivery_type`. `github-pr` returns
`pr-ready-for-merge-but-not-merged` with PR/provider/CI and mergeability proof.
`local-branch` returns `local-branch-ready` with exact repository and checkout
identity, named target branch and HEAD, base branch and base SHA ancestry, clean
worktree, current-head validation and reviews, committed tracker readback, no
unresolved recorded task changes, warnings, and changed paths. Coherent progress
needs no root intervention.

## Peer Collaboration And Combined Proof

There is no dedicated integration worker. For a multi-repository bundle, the
ordinary repository workers communicate directly using the exact peer task,
repository, branch, HEAD, and checkout identities supplied by root. Workers may
exchange interface clarifications, exact revisions, test endpoints, and factual
mismatch evidence while the durable contract remains unchanged. They do not
delegate their repository implementation or expand another worker's scope.

Each combined boundary has an existing worker as its proof owner. For example,
the web worker may prove web-to-backend behavior while the mobile worker proves
mobile-to-backend behavior against the same backend HEAD. A bundle-wide scenario
must likewise name one existing worker capable of executing it within that
worker's accepted scope. If no ordinary worker can own the required proof, the
bundle is not execution-ready; do not synthesize another task as a fallback.

Before combined validation, the ordinary workers test the distributed execution
topology described by the Spec. Every worker remains isolated to its own
worktree. Each peer starts and cleans up its own component, sends the proof
owner its exact pre-start HEAD plus endpoint and health evidence, and sends its
post-cleanup HEAD readback afterward. The proof owner runs the combined scenario
through those exposed component boundaries and records the exact SHA vector.

The proof owner must not infer a peer HEAD from an earlier message, read or
execute inside a peer worktree, or take ownership of a peer component. Any peer
HEAD change makes prior proof stale. A worker sends an upstream-owned mismatch
directly to the owning peer as evidence only; that peer owns diagnosis, repair,
validation, and a replacement HEAD. The proof owner then reruns the affected
complete proof. If the distributed topology cannot execute, report
`blocked-app-capability` without asking the user or falling back to root
execution.
