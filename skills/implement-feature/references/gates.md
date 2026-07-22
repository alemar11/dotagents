# Final Gates

The worker must first report `pr-ready-for-merge-but-not-merged`. Root then
performs read-only verification; it does not edit code, rerun implementation,
check boxes, uncheck boxes, or judge acceptance criteria.

For each assignment, root rereads:

- the current Feature Spec and issue graph, including final checkbox state;
- the App thread and managed checkout identity;
- exact target branch and head SHA;
- open, non-draft PR identity and default-branch base;
- current-head validation evidence;
- terminal AutoReview and current-head Codex review evidence;
- actionable feedback resolution;
- configured CI success or authoritative not-configured evidence;
- tracker readback, mergeability, conflicts, rules, and required approvals.

If authoritative final evidence agrees, record `assignment ready`; that same
transaction releases only this Feature Spec claim. If it does not, report
coarse mismatch to the same worker and let the worker own repair.
If stable durable contract drift caused the mismatch, record `assignment block`
and retain claims.

After every assignment is ready, journal root Goal completion, read the same
Goal back as completed, finish that App operation, and call
`run finish --outcome pr-ready`. Run finish verifies that assignment-level
release already occurred; it does not perform a repository-wide release. The
terminal result is PR-ready for merge, never merged.

Before one assignment's bootstrap authority, a verified abort may archive its
exact created worker, reconcile its App operations, and call `assignment abort`
to release only its claim. A whole run that never started implementation may
then complete any created Goal and call
`run finish --outcome preimplementation-aborted`. After an assignment's
bootstrap authority, ordinary abort is forbidden; terminal owner recovery
follows `recovery-validation.md`.
