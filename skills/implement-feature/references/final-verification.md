# Final Verification

The worker first reports the terminal observation required by its stable
`delivery_type`: `pr-ready-for-merge-but-not-merged` or `local-branch-ready`.
Root then performs read-only verification; it does not edit code, rerun implementation,
check boxes, uncheck boxes, or judge acceptance criteria.

For each assignment, root rereads:

- the current Feature Spec and issue graph, including final checkbox state;
- the visible Codex task and ChatGPT-created checkout identity;
- exact target branch and head SHA;
- base branch, base SHA, and proven ancestry;
- current-head validation evidence;
- terminal AutoReview and current-head Codex review evidence;
- actionable feedback resolution;
- committed tracker readback and a clean managed worktree;
- for `github-pr` only: open non-draft PR identity, provider default-branch
  base, configured CI, mergeability, conflicts, rules, and approvals;
- for `local-branch`: absence of push/PR/provider operations and an exact named
  local branch plus HEAD.

If authoritative final evidence agrees, record `assignment ready`; that same
transaction releases only this Feature Spec claim. If it does not, report
coarse mismatch to the same worker and let the worker own repair.
If stable durable contract drift caused the mismatch, record `assignment block`
and retain claims.

A repairable follow-up contains evidence only. For example, “Final verification
shows PR HEAD `def`, while validation evidence is bound to `abc`.” It must not
say “Rerun test X and modify file Y,” diagnose the defect, judge a checklist, or
prescribe a repair. The worker owns diagnosis, repair, validation, and new
evidence. Record `send-worker-message` before sending, then verify both the
immediate tool response and the exact visible task conversation before marking
that send complete.

After every assignment is ready, record the intended Goal completion in SQLite,
perform it through the ChatGPT desktop app, read the same
Goal back as completed, finish that recorded operation, and call
`run finish` with `pr-ready`, `local-branch-ready`, or `delivery-ready` for a
mixed vector. Run finish verifies assignment-level release already occurred;
it does not perform a repository-wide release. No terminal result merges.

For a dedicated integration assignment, root may first record each prerequisite
as `integration-input-ready`; its task and claim stay active and its exact HEAD
is available to the integration bootstrap. Dispatch the visible integration
task only after every prerequisite is in that state and a worker slot is free.
Final integration readiness must contain the exact current prerequisite HEAD
vector. A changed prerequisite HEAD invalidates prior proof; root routes the
coarse failure or rerun request while workers retain technical ownership.

Before one assignment's bootstrap authority, a verified abort may archive its
exact created worker, reconcile its recorded task changes, and call
`assignment abort`
to release only its claim. A whole run that never started implementation may
then complete any created Goal and call
`run finish --outcome preimplementation-aborted`. After an assignment's
bootstrap authority, ordinary abort is forbidden; terminal owner recovery
follows `claim-waits-and-recovery.md`.
