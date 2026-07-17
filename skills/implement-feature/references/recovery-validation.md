# Recovery Validation

Load this reference only when resuming from a Recovery Packet.

## Runtime Surface Revalidation

Before reading the packet, ledger projection, or recorded task, verify visible
Codex App task creation, App-managed worktree binding, task-title mutation
through `codex_app__set_thread_title`, and live task-title observation again.
Prior evidence, task readability, generic subagents, and filesystem access are
insufficient. If any required surface is absent or unverifiable, abort as
`unsupported-runtime` without asking permission or touching runtime artifacts.

## Freshness Validation

1. Revalidate the recorded run authorization, the canonical
   `task-model-policy.md` surface, and every recorded per-Spec task profile;
   this includes no-task Specs awaiting dispatch. Reject unknown fields, missing
   profile evidence, unavailable model or thinking values, and silent
   substitutions.
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
6. Read every current task and validate its recorded `task_title`, model,
   thinking value, profile decision reason, Goal, App-managed checkouts,
   lifecycle, changes, PR revision tuples, review, CI, required domain-closeout
   evidence, and blockers. Use the recorded profile for every resume or steering
   message. Record task-title drift without mutating it during freshness
   validation. For a captured closeout, recompute the delta fingerprint,
   verified destinations, documentation-diff fingerprint, and relevant
   implementation revision tuples.
7. Recompute merged dependencies, path conflicts, deterministic ready order,
   due checks, gates, and next action from live evidence. A material code,
   evidence, target, documentation, or revision-tuple change invalidates domain
   closeout and requires the exact Project Memory closeout again before terminal
   `merge-ready`.

Any mismatch invalidates the compact packet. Run full source and ledger
reconciliation before mutation; do not repair the packet in place.
Only after the complete freshness pass and any required full reconciliation
succeed may the root repair recorded task-title drift through
`codex_app__set_thread_title` on the same task, observe the exact result, update
the ledger evidence, and resume implementation.

## Task Recovery

Require the exact Feature Spec assignment, one task, an assignment-scoped Goal
or recorded unavailable fallback, exact task display title, exact task model and
thinking profile, complete managed checkout map, and the fixed PR-ready flow.
Resume only the original visible task with its recorded title and profile after
recording stale or failure evidence. If that task or a managed checkout cannot
be recovered, abort as blocked; never create a replacement for the same Spec or
substitute root/background implementation or raw worktree machinery.

For an otherwise current pre-title ledger, missing `task_title` is recoverable
derived UI evidence, not ownership evidence. Read the live task without using
its title as identity. Derive the canonical title from the validated Feature
Spec title and dominant user-facing goal using the same semantic rule and
mandatory `🛠️` fallback as first dispatch; never accept an arbitrary emoji
prefix as canonical. Compare the complete live value with that derived title.
After the complete freshness pass and any required reconciliation succeed,
record an exact match or rename that same task, observe the exact result, and
record it. Never use a title to discover, adopt, or replace a task.

For a taken-over root, validate the candidate claim's embedded full prior-claim
snapshots and per-Spec task-adoption mappings. Cross-check every available prior
ledger through its embedded `ledger_ref`. If the new ledger or registry was not
written before a crash, rebuild only that exact projection from the embedded
mapping after claim recovery; do not infer it from task titles or source prose.
For an embedded schema-5 no-task Spec, preserve the resolved profile and use it
unchanged when its deterministic dispatch wave creates the first task.
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

The claim helper may report an exact schema-3 or schema-4 claim as `legacy`. Do
not load it as current runtime state or migrate it. A prepared schema-1 takeover
journal containing a schema-4 candidate is still recoverable: finalize its exact
snapshots into that schema-4 legacy ownership claim, but never infer the missing
task profile or resume it as current. After the legacy task is verified terminal
or a durable handoff exists, only that exact owner may run `claim retire-legacy`
with the stored fingerprint and evidence. Until then the legacy claim remains a
blocking owner.
