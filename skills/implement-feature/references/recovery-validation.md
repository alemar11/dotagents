# Recovery Validation

Load this reference only when resuming from a Recovery Packet.

## Runtime Surface Revalidation

Before reading the packet, ledger projection, or recorded task, verify visible
ChatGPT desktop app task creation, App-managed worktree binding, task-title mutation
through `codex_app__set_thread_title`, live task-title observation, and
`create_goal`, `get_goal`, and `update_goal` in the root plus general
visible-task Goal-tool support again. Prior evidence, generic subagents, and
filesystem access are insufficient. If any required general surface is absent
or unverifiable, abort as `unsupported-runtime` without asking permission or
touching existing runtime artifacts.

After that general gate, read only the packet and ledger fields needed to
resolve the recorded task refs and Goal evidence. Before any mutation, read
each exact task and require its runtime to expose the same Goal tools. A missing
task-local tool is an `unsupported-runtime` blocker on the existing task; never
create a replacement or objective fallback.

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
6. Call `get_goal` in the root. For `portfolio_goal_state=pending`, require the
   observed active Goal to match the recorded objective, or record that no
   active Goal exists. Do not persist adoption or call `create_goal` during the
   freshness pass. A different unfinished Goal blocks as `needs-owner`. For an
   `active` state, require the objective, fingerprint, and evidence to match;
   never recreate a missing Goal. For `portfolio_goal_state=complete`, require
   matching completed Goal evidence and continue the full freshness pass
   without resuming implementation. Read every current task and validate its recorded `task_title`,
   model, thinking value, profile decision reason, assignment Goal, App-managed checkouts,
   lifecycle, changes, PR revision tuples, review, CI, required domain-closeout
   evidence, and blockers. Use the recorded profile for every resume or steering
   message. Record task-title drift without mutating it during freshness
   validation. Require active matching Goal evidence for every nonterminal task
   and completed matching Goal evidence for every task already at the fixed
   terminal result. A terminal task may temporarily retain an active matching
   Goal only as an interrupted completion transition; do not resume its
   implementation. For a captured closeout, recompute the delta fingerprint,
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
succeed may the root complete `pending` Goal registration: persist a matching
observed Goal as `active`, or, if none existed during the pass, call
`create_goal` once with the recorded objective and atomically persist its
evidence as `active`. Then the root may repair recorded task-title drift through
`codex_app__set_thread_title` on the same task, observe the exact result, update
the ledger evidence, and resume implementation.

For `portfolio_goal_state=complete`, instead require every task Goal and fixed
terminal gate to be complete, verify the terminal release evidence or current
claim ownership, and never repair or resume implementation. If the claim is
still active, idempotently release it with `--release-reason terminal`; then
archive the ledger with that exact release evidence if it is not already
archived. A mismatch blocks without reopening the completed Goal.

For interrupted terminal closeout while `portfolio_goal_state=active`, first
require every fixed task and portfolio terminal gate to pass. For each terminal
task whose matching Goal is still active, call `update_goal` with
`status=complete` and persist the result; if it is already completed, persist
the matching completion evidence without calling the tool again. After every
task Goal is complete, apply the same rule to the portfolio Goal, persist
`portfolio_goal_state=complete`, and continue through the completed-state
release and archival path above. These are terminal-closeout recovery mutations,
not implementation resume.

## Task Recovery

Require the exact Feature Spec assignment, one task, an assignment-scoped Goal
created through `create_goal`, exact task display title, exact task model and
thinking profile, complete managed checkout map, and the fixed PR-ready flow.
The task calls `get_goal` and verifies its objective against the recorded
fingerprint before implementation resumes. A terminal task instead verifies
its completed Goal, or finishes only an interrupted completion transition, and
remains stopped. Missing or mismatched Goal evidence
blocks recovery; there is no unavailable-tool or objective-ledger fallback.
Resume only the original visible task when it is nonterminal, using its recorded
title and profile after recording stale or failure evidence. If that task or a
managed checkout cannot be recovered, abort as blocked; never create a
replacement for the same Spec or substitute root/background implementation or
raw worktree machinery.

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
source-provided option fingerprints. Also reject fallback-only portfolio or
dispatched-task Goal evidence. An undispatched `no-task` record may retain
`goal_evidence_ref: "none"`. Start a fresh compatible run only after the old
owner releases its claim.

The claim helper may report an exact schema-3 or schema-4 claim as `legacy`. Do
not load it as current runtime state or migrate it. A prepared schema-1 takeover
journal containing a schema-4 candidate is still recoverable: finalize its exact
snapshots into that schema-4 legacy ownership claim, but never infer the missing
task profile or resume it as current. After the legacy task is verified terminal
or a durable handoff exists, only that exact owner may run `claim retire-legacy`
with the stored fingerprint and evidence. Until then the legacy claim remains a
blocking owner.
