# Implement Contract Repair Orchestration

Load the plugin contract at
[`../../../references/contract-repair.md`](../../../references/contract-repair.md)
when a bootstrapped worker reports a stable semantic conflict in the current
Feature Spec bundle. The worker stops at the conflict boundary. Root records
`blocked-contract-repair` while preserving the worker task, worktree, branch,
claim, bootstrap identity, current HEAD, and useful changes.

## Root Control Plane

The explicit `$se:implement` invocation already authorizes all Contract Repair
tasks required by the run. Root never asks again. Root describes the conflict
and evidence in the portable request but never proposes bodies or patches and
never edits a Spec, issue, relationship, repository, or implementation itself.

For each repair ID, root authorizes one logical `create-contract-repair-task`
operation. It resolves the authoritative project and host, creates one separate
non-worktree Feature task, and verifies its identity and structural state by
independent readback. The expected title is
`🧭 Contract Repair · <Feature Spec title>`. Missing or drifted title is a
warning; it is never identity and does not justify duplicate creation.

The task explicitly invokes `$se:feature` with only the portable request. It is
not a worker and does not consume worker capacity. On rejection, timeout, or
unknown creation/readback, root reconciles current task state before any replay.
One assignment may have only one open repair. Later stable conflicts may start
serial repairs with a new repair ID after the previous repair is closed.

## Accepting A Repair

Root accepts only the exact portable result for the active repair. For
`applied` or `no-op`, root independently rereads the complete authoritative
Spec set and issue graph and validates that readback before recording the
repair observation. `proposed` or `blocked` does not resume execution.

If source Spec identity, repository, target branch, worker claim, worktree, and
bootstrap identity remain compatible, root records and performs
`send-contract-revision` to the same worker. The revision carries the complete
stable contract, Feature result/readback refs, a new revision ID, and
`contract_generation=N+1`. Readback of worker acceptance completes the
operation and restores the pre-block state.

If any execution identity is incompatible, root marks the old assignment
superseded through `assignment contract-supersede`, recording the worker's exact
HEAD and authoritative bundle readback. The worker, not root, preserves useful
work. Run-state retains the old task/worktree evidence, advances the worker
generation, and prepares the retained claim for normal replacement bootstrap.
Root never opens, edits, rebases, or copies from the worker worktree.

## Worker And Recovery Rules

The worker accepts a revision only when bootstrap and execution identity remain
compatible, generation is exactly previous plus one, the revision ID is new,
and complete source readback matches the supplied result. Exact replay is
acknowledged idempotently; stale, skipped, conflicting, or identity-changing
revision fails closed.

Creation, title, revision, and archival are recorded operations. Recovery first
observes the existing Feature task or conversation and reuses the same logical
operation identity only when run-state explicitly authorizes replay. Serial
repairs receive distinct repair and revision IDs and monotonically increasing
contract generations.
