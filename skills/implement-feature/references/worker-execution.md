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

Resolve the bootstrap's `review_owner=worker|root` before editing
implementation files. With worker ownership, run
`<autoreview-skill-root>/scripts/autoreview --json doctor` immediately after
read-only checkout identity preflight and before branch selection. Continue
only when it succeeds. On
`recovery=reroute-to-capable-root`, send the structured result to root and wait
for its evidence-only owner readback; do not retry with escalation or copy
credentials. Root ownership changes only the later review executor. The worker
retains design, implementation, finding verification, fixes, validation,
tracker, and delivery authority.

Before accepting implementation authority, deduplicate the bootstrap envelope
by its opaque `bootstrap_id`:

- accept the first valid ID and bind it to the exact stable Feature Spec and
  issue contract received with it;
- for the same ID and the same stable contract, acknowledge the replay and
  resume the already accepted work without applying bootstrap initialization a
  second time;
- reject the same ID with a different stable contract;
- after one ID has been accepted, reject every different bootstrap ID.

These checks make the logical bootstrap effect exactly once even though
delivery itself may be retried. Root may increment its recorded `launch_count`
for a transport replay, but every generation of that logical bootstrap carries
the same `bootstrap_id`; the worker deduplicates the stable ID, not the
controller's launch generation. A missing ID is not an accepted bootstrap.

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

Before a worker-owned review or a root reroute, run:

```bash
<implement-feature-skill-root>/scripts/verify-ready --json review-candidate \
  --checkout <managed-checkout> \
  --branch <target-branch> \
  --base-sha <startup-base-sha>
```

Use its exact `head_sha` and `base_sha` fields verbatim. Never expand a short
SHA manually. The review executor repeats this readback immediately before
launch. A root reroute always starts structured AutoReview in branch mode with
the exact base, `review_phase=full`, and an evidence output so accepted fixes
can continue in one evidence chain; it never substitutes commit mode.

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
