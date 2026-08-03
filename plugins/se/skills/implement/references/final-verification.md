# Implement Final Verification

The worker first reports the terminal observation `pr-ready-for-merge`.
Root then performs read-only verification; it does not edit code, rerun implementation,
check boxes, uncheck boxes, or judge acceptance criteria.

The worker-facing `pr-ready-for-merge` result is also the
`implement-feature/delivery-ready-observation` `4.0.0` status value. It maps to
assignment state `pr-ready` and aggregate outcome `pr-ready`.

Collect the terminal reports and immutable current-head evidence for every
ready candidate before mutating assignment state. Reuse that snapshot while its
tracker, task, checkout, branch, and HEAD identities remain unchanged. If any
identity or authoritative artifact changes, discard the affected snapshot and
verify that assignment again.

The review candidate identity must originate from `scripts/verify-ready --json
review-candidate`, not from a manually expanded short SHA. Worker and root
repeat that read-only command against the managed checkout before the
worker-owned review and require identical full `base_sha`, `head_sha`, branch,
cleanliness, and ancestry fields.

For each assignment, root rereads:

- the current Feature Spec and issue graph, including final checkbox state;
- the visible Codex task and ChatGPT-created checkout identity;
- exact target branch and head SHA;
- base branch, base SHA, and proven ancestry;
- current-head validation evidence;
- when the issue contains `## Domain Knowledge Closeout`, the exact accepted
  `knowledge_delta`, `capture_outcome=captured`, named destinations, reconciled
  item/target evidence, and the verified documentation diff on the same HEAD;
- current-head native review evidence with its worker-derived
  `review_profile=standard|high-risk`; both profiles require native review on
  the candidate, and its final `codex_review_head_sha` must bind the current
  HEAD after all accepted fixes;
- exact Send publication evidence for the PR head and draft-state read-back;
- the typed ready-transition observation proving the exact draft-to-ready
  event for that PR and HEAD;
- the typed ready-triggered provider-review observation, with provider, result,
  artifact timestamp, exact SHA, and finding/thread identities. Any review
  performed while the PR was draft is consultative and cannot satisfy this
  requirement;
- actionable feedback resolution;
- committed tracker readback and a clean managed worktree;
- open non-draft PR identity, provider default-branch base, configured CI,
  mergeability, conflicts, rules, approvals, and zero unresolved review threads.

If authoritative final evidence agrees, use `assignment ready-observation
create --readiness-mode terminal` to build the private typed payload from that
snapshot, then pass the unchanged file and expected revision to plain
`assignment ready`. The builder is read-only; `ready` derives the terminal
mutation from the payload, revalidates it in the sole state-mutating
transaction, and releases only this Feature Spec claim. If evidence does not
agree, report coarse mismatch to the same worker and let the worker own repair.
Missing or non-captured domain closeout evidence is durable-contract drift and
must not produce a terminal readiness observation.
If stable durable contract drift caused the mismatch, record `assignment block`
and retain claims.

A repairable follow-up contains evidence only. For example, “Final verification
shows PR HEAD `def`, while validation evidence is bound to `abc`.” It must not
say “Rerun test X and modify file Y,” diagnose the defect, judge a checklist, or
prescribe a repair. The worker owns diagnosis, repair, validation, and new
evidence. Record `send-worker-message` before sending, then verify both the
immediate tool response and the exact visible task conversation before marking
that send complete.

After every assignment is ready, call `run finish --outcome pr-ready`. Run finish
verifies that task operations are reconciled and assignment-level release
already occurred; it does not perform a repository-wide release. No terminal
result merges.

After the root reaches any terminal boundary, it sends the same Markdown
closeout report only to the parent identity whose provenance was verified at
entry and returns that report as its own final response. If that identity can no
longer be verified, retain the root result, report the relay blocker, and do not
guess another destination. The parent relays the root report without adding a
second readiness judgment, and the root task remains unarchived.

For a linked multi-repository feature, require exactly one independently
verified GitHub PR for every Feature Spec Set member. Report one
exact final vector of
`feature_id, repository_identity, source_spec_ref, target_branch_name,
head_sha, pr_url`; every row must come from that member's
unchanged terminal snapshot. The vector is aggregate evidence only and does not
replace any member's assignment, claim, review, tracker, or delivery proof.

An ordinary worker may first be recorded as `peer-input-ready`; its task and
claim stay available while its exact HEAD becomes available to dependent peers
and the worker parks for later peer repair. Build that observation with
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

## Verification CLI Maintenance

Normal runtime execution stays on `scripts/verify-ready`, whose
`CLI_VERSION = "1.0.0"` is its SemVer source of truth. It is read-only: neither
`doctor` nor `review-candidate` writes repository or run state. Use a major bump
for a breaking command removal and a patch bump for a compatible correction.
Re-run `--help`, `--version`, `--json doctor`, and the review-candidate fixture
after changes.
