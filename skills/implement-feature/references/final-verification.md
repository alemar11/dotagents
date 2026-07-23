# Final Verification

The worker first reports the terminal observation required by its stable
`delivery_type`: `pr-ready-for-merge-but-not-merged` or `local-branch-ready`.
Root then performs read-only verification; it does not edit code, rerun implementation,
check boxes, uncheck boxes, or judge acceptance criteria.

For `github-pr`, the worker-facing
`pr-ready-for-merge-but-not-merged` result is also the
`implement-feature/delivery-ready-observation` `2.0.0` status
value. It maps to assignment state `pr-ready` and aggregate outcome `pr-ready`;
all three names describe the same unmerged delivery boundary.

Collect the terminal reports and immutable current-head evidence for every
ready candidate before mutating assignment state. Reuse that snapshot while its
tracker, task, checkout, branch, and HEAD identities remain unchanged. If any
identity or authoritative artifact changes, discard the affected snapshot and
verify that assignment again.

For each assignment, root rereads:

- the current Feature Spec and issue graph, including final checkbox state;
- the visible Codex task and ChatGPT-created checkout identity;
- exact target branch and head SHA;
- base branch, base SHA, and proven ancestry;
- current-head validation evidence;
- current-head AutoReview evidence with its derived
  `review_profile=standard|high-risk`; `standard` requires no native Codex
  review, while `high-risk` requires the single native Codex review on that
  same initial `review_candidate_head_sha` and an AutoReview evidence chain
  that closes its findings on the current HEAD;
- actionable feedback resolution;
- committed tracker readback and a clean managed worktree;
- for `github-pr` only: open non-draft PR identity, provider default-branch
  base, configured CI, mergeability, conflicts, rules, and approvals;
- for `local-branch`: absence of push/PR/provider operations and an exact named
  local branch plus HEAD.

For each `local-branch` candidate, run `scripts/verify-ready --json
local-branch` once with the managed and original checkout identities, declared
base and delivery branch/SHAs, repository-relative Feature Spec and completed
issue paths, and each issue's canonical startup `workflow_state`, passing one
`--issue path=state` argument for every issue in the graph. Its passing
snapshot replaces ad hoc shell composition for branch identity, original
checkout preservation, ancestry, cleanliness, `git diff --check`, tracked
artifacts, completed-issue placement, final checkboxes, and workflow-state
preservation. Root still verifies worker task, review, validation, peer, and
no-provider evidence from their authoritative owners.

If authoritative final evidence agrees, use `assignment ready-observation
create --readiness-mode terminal` to build the private typed payload from that
snapshot, then pass the unchanged file and expected revision to plain
`assignment ready`. The builder is read-only; `ready` derives the terminal
mutation from the payload, revalidates it in the sole state-mutating
transaction, and releases only this Feature Spec claim. If evidence does not
agree, report coarse mismatch to the same worker and let the worker own repair.
If stable durable contract drift caused the mismatch, record `assignment block`
and retain claims.

A repairable follow-up contains evidence only. For example, “Final verification
shows PR HEAD `def`, while validation evidence is bound to `abc`.” It must not
say “Rerun test X and modify file Y,” diagnose the defect, judge a checklist, or
prescribe a repair. The worker owns diagnosis, repair, validation, and new
evidence. Record `send-worker-message` before sending, then verify both the
immediate tool response and the exact visible task conversation before marking
that send complete.

After every assignment is ready, call `run finish` with `pr-ready`,
`local-branch-ready`, or `delivery-ready` for a mixed vector. Run finish
verifies that task operations are reconciled and assignment-level release
already occurred; it does not perform a repository-wide release. No terminal
result merges.

An ordinary worker may first be recorded as `peer-input-ready`; its task and
claim stay available while its exact HEAD becomes available to dependent peers
and its execution slot becomes free.
Build that observation with
`ready-observation create --readiness-mode peer-input`, then consume it with
plain `assignment ready`; the consumer derives and revalidates the retained
claim mutation from the payload. Both stages must use the same authoritative
snapshot and expected revision.
Final readiness for a worker that owns combined proof must contain the exact
current prerequisite HEAD vector. A changed prerequisite HEAD invalidates prior
proof. The proof owner sends the mismatch directly to the owning peer, that peer
repairs its own repository, and the proof owner reruns the affected validation.
Root observes and reconciles the resulting coarse evidence but does not relay
routine technical messages or choose the fix.

Verify each owning peer's task contains matching pre-start and post-cleanup HEAD
reads plus endpoint, health, and cleanup evidence, and that the proof owner's
combined result names the same SHA vector. The proof owner must not access a
peer worktree; it validates only through the component boundary exposed by that
peer.

Before one assignment's bootstrap authority, a verified abort may archive its
exact created worker, reconcile its recorded task changes, and call
`assignment abort`
to release only its claim. A whole run that never started implementation may
then call `run finish --outcome preimplementation-aborted`. After an assignment's
bootstrap authority, ordinary abort is forbidden; terminal owner recovery
follows `claim-waits-and-recovery.md`.

If post-bootstrap owner recovery proves a worker terminal or missing and its
checkout released or absent, `assignment recover` may mark that assignment
`abandoned` and release only its claim. After every sibling is terminal and all
task operations are reconciled, `run finish --outcome abandoned` terminalizes
the owning run without claiming delivery success.
