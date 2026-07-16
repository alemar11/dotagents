# Recovery Validation

Load this reference only when resuming from a Recovery Packet.

## Runtime Surface Revalidation

Before reading the packet, ledger projection, or recorded task, verify visible
Codex App task creation and App-managed worktree binding again. Prior evidence,
task readability, generic subagents, and filesystem access are insufficient. If
either surface is absent or unverifiable, abort as `unsupported-runtime`
without asking permission or touching runtime artifacts.

## Freshness Validation

1. Revalidate the recorded run authorization and reject unknown fields.
2. Recompute every authoritative source and issue fingerprint and rederive every
   canonical claim/task source id. A verified GitHub
   `owner/repository#N` must still map to
   `https://github.com/owner/repository/issues/N`; a mismatch blocks recovery.
   For a local issue, accept a missing active path only when its exact
   predeclared `planned_done_ref` exists inside the same managed checkout, the
   body fingerprint is unchanged, substantive closeout evidence exists, and the
   Git state proves the planned tracked rename. Atomically finish or verify that
   one ledger transition to `source_state=done`; do not classify it as external
   drift. Both paths, neither path, a different destination, or any unapproved
   body change blocks recovery.
3. Verify repository identity, HEAD, branch, and tracked status.
4. Verify that the atomic claim still covers the same repositories and sources
   with the recorded acquire-time fingerprint.
   If `claim status` reports `takeover-prepared`, require the recorded grant and
   exact transaction id, then run the helper's idempotent `recover-takeover`
   path against the reported candidate recovery root before any other mutation.
   A status query by a replaced root must still expose that prepared transaction
   after its original claim was deleted. A mismatched replaced snapshot blocks.
5. Require at most one live task per Feature Spec and three nonterminal tasks
   across the portfolio.
6. Read every current task and validate its Goal, App-managed checkouts,
   lifecycle, changes, PR revision tuples, review, CI, required domain-closeout
   evidence, and blockers. For a captured closeout, recompute the delta
   fingerprint, verified destinations, documentation-diff fingerprint, and
   relevant implementation revision tuples.
7. Recompute merged dependencies, path conflicts, deterministic ready order,
   due checks, gates, and next action from live evidence. A material code,
   evidence, target, documentation, or revision-tuple change invalidates domain
   closeout and requires the exact Project Memory closeout again before terminal
   `merge-ready`.

Any mismatch invalidates the compact packet. Run full source and ledger
reconciliation before mutation; do not repair the packet in place.

## Task Recovery

Require the exact Feature Spec assignment, one task, an assignment-scoped Goal
or recorded unavailable fallback, complete managed checkout map, and the fixed
PR-ready flow. Resume only the original visible task after recording stale or
failure evidence. If that task or a managed checkout cannot be recovered, abort
as blocked; never create a replacement for the same Spec or substitute
root/background implementation or raw worktree machinery.

For a taken-over root, validate the candidate claim's embedded full prior-claim
snapshots and per-Spec task-adoption mappings. Cross-check every available prior
ledger through its embedded `ledger_ref`. If the new ledger or registry was not
written before a crash, rebuild only that exact projection from the embedded
mapping after claim recovery; do not infer it from task titles or source prose.
Require one owner per recorded task ref and managed checkout, then revalidate
each checkout's repository, target branch, and baseline commit before resuming
those exact visible tasks. Missing, contradictory,
terminal-unresumable, or unadoptable task evidence blocks; it never opens a
replacement slot.

## Hard Cut

Reject and do not migrate ledgers or packets containing delivery or issue
permissions, review skips, worker action options, parallelization, repository
layout copies, checkout strategies, adapter or lifecycle-owner fields, stacked
states, PR-count strategies, completion methods, closeout enums, or
source-provided option fingerprints. Start a fresh compatible run only after
the old owner releases its claim.

The claim helper may report an exact schema-3 claim as `legacy`. Do not load it
as current runtime state or migrate it. After the legacy task is verified
terminal or a durable handoff exists, only that exact owner may run
`claim retire-legacy` with the stored fingerprint and evidence. Until then the
legacy claim remains a blocking owner.
