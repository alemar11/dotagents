# Recovery Validation

Load this reference on every manual resume, including prepared
takeover and embedded-adoption recovery before a candidate JSON state exists.

## Runtime Surface Revalidation

Before reading run state or a recorded task, verify visible ChatGPT desktop app
task creation, App-managed worktree binding, task-title mutation and
observation, and `create_goal`, `get_goal`, and `update_goal` in the root.
Require first-class targeted root Goal
`pending`/`active`/`complete` readback and updates. Goal pause/resume and App
heartbeat automation are not required. Prior evidence, background agents, and filesystem
access are insufficient. Missing support is `unsupported-runtime` without
asking permission or performing mutation.

Call `get_goal` once in the root. If `blocked`, return `new-root-required` before
authorization/run-state reads, require a fresh App task, preserve prior
artifacts, and never adopt/update that Goal.

Run and verify a freshly prepared `delivery-preflight` command manifest under
`execution-manifest.md` and require its pinned authenticated `gh` plus API
reachability before external freshness checks. Missing capability is
`unsupported-runtime`; do not reinterpret it as CI absence.

Read `ledger-cache ledger read --projection recovery` only after that gate.
Before any mutation, read each exact recorded task and require matching Goal
tools and never create a replacement or objective fallback.

Compact `wait_threads` snapshots are hints only: they never append
`task-observed` or update durable task state. Before a task lifecycle mutation,
worker steering, authority grant, completion acceptance, gate, terminal
decision, release, or takeover, read the same visible task directly with
`read_thread`. Read newest-first pages to EOF, or stop at an exact durable
anchor only when the normalized ID/hash chain is unbroken. A cursor reset or
expiry, missing/broken anchor, conflicting marker/hash, or takeover falls back
to EOF. Keep only the bounded full-read observation packet; never persist raw
history or pagination cursors. Reuse the exact `task_ref` and `host_id` on
reconnect. `wait_cursor` is an opaque resume hint and is never compared with a
`read_thread` pagination cursor.

The bounded proof has exactly `observation_kind`, `task_ref`, `host_id`,
optional `wait_cursor`, `read_scope` (`eof` or `anchored`), nullable
`anchor_observation_fingerprint`, nullable `anchor_marker_id`, latest
turn/message/tool-marker IDs, `observed_status`, content and page-chain
fingerprints, `observed_at`, `base_generation`, `base_head`, and
`observation_fingerprint`. An initial proof must be `eof` with null anchors;
an `eof` proof always has null anchors. An `anchored` proof must name the
previous accepted observation fingerprint and one of its marker IDs. These
fields are part of the proof fingerprint. It invents no App revision,
frontier, or gap fields. An exact proof replay is a no-op; marker/hash,
anchor, or identity conflict fails closed.

For `implementation_baseline=pending`, recovery is baseline-only. Require
internal Goal state `pending` and no external Goal, verify immutable bundle,
authorization and execution-scope fingerprints, exact managed checkout
revision/tree/status, and every manifest/receipt byte hash. Resume only the same
baseline-only tasks. Never recapture after source, tool, argv, adapter, policy,
or scope drift; return `authorization-stale` or execute the typed
preimplementation abort. Partial baseline evidence grants no implementation
authority.

## Complete Freshness Pass

Perform one complete read-only pass:

1. Revalidate authorization, `task-model-policy.md`, and every recorded per-Spec profile,
   including explicit no-task adoption entries. Unknown, unavailable, or
   substituted profiles block.
2. Recompute every source and generated-issue fingerprint plus every canonical
   claim/task source id. For local tracker sources, accept a missing active path
   only when the exact predeclared done ref exists in the registered delivery,
   the body fingerprint is unchanged, and Git proves the tracked move. Both
   paths, neither path, another destination, a GitHub source move, or changed
   body blocks.
3. Verify each registered repository and branch, then rerun the bounded
   delivery preflight for the complete registered set. Require the same GitHub
   repository/default-base identity and a definitive `configured` or
   `not-configured` result. An unknown result blocks without replacing prior
   state. Then verify the complete
   `deliveries[]` set for each task. Every delivery requires its exact
   App-managed checkout, Git top-level, baseline, current HEAD, isolation proof,
   and unique `(repository, checkout)` ownership. A partial, shared, symlinked,
   unmanaged, or non-isolated map blocks.
4. Verify the active claim still covers the same repositories and sources. For
   `takeover-prepared`, require the recorded grant, exact transaction id, and
   helper's idempotent `recover-takeover`; a changed replaced snapshot blocks.
5. Rebuild the complete implementation-eligible Spec registry. Derive the exact
   singular/plural root title. Require one task per Spec at most, one delivery
   per affected repository, and no more than three nonterminal tasks. Record
   live title drift without repairing it during this pass.
6. Rederive the portfolio objective from the bundle; require exact
   `CI when configured` and its fingerprint as a hard cut. Call `get_goal` in
   the root. Pending registration may
   observe a matching active Goal or no Goal; do not adopt or create it
   during this pass. An active root Goal must match its objective and fingerprint.
   Completed root Goal readback requires a matching portfolio verification.
7. Recompute each delivery's exact PR repository, number, URL,
   head/base/merge-base tuple, review request and deadline, configured CI or
   explicit `not-configured`, PR lifecycle,
   tracker state, mergeability and repository rules. Recompute the canonical
   complete task revision set, validation, AutoReview, integration, domain
   closeout, merged dependencies, path conflicts, ready order, review deadlines,
   blockers, and next stage.
8. For sealed tasks and a completed root Goal, independently reverify terminal truth.
   Record drift candidates; do not resume work or reopen the root Goal.

The recovery projection is derived guidance, not external truth. It reports
timestamps, not wall-clock `overdue` judgments. Callers compare review deadlines
with their observed clock. Do not patch JSON or manufacture an event from stale
prose.

## Applying Reconciled State

Only after the full pass succeeds may the root apply material events through
`ledger-cache ledger apply` at the observed generation. On CAS conflict,
discard the batch, reread, and recompute.

Late direct task evidence after a seal uses the existing `task-observed` packet
to record terminal drift only; it never replaces the sealed observation/result,
reopens the Goal, or regrants authority.

Before seal, apply a changed definitive capability observation through
`delivery-preflight-observed`; its new preflight key invalidates delivery and
task-set bindings. After seal, never apply that event: record the changed key
only through `post-terminal-drift-recorded` and block archive.

For `portfolio_goal_state=pending`, first repair and observe the root title,
then apply `root-title-observed`. Adopt a matching Goal observed in the pass or,
only when none exists, call `create_goal` once without `token_budget`; apply
`portfolio-goal-activated`. A different unfinished Goal is `needs-owner`; a
blocked root Goal never reaches this phase.

For a nonterminal task, require exact source assignment, task ref, derived display title,
profile, matching assignment fingerprint, and complete managed
checkout map. Repair title drift on that same task only after freshness passes,
then report it through `task-observed`. Resume only the original visible task
with its recorded profile.

If a local move is fully proven, apply `source-moved`; it is valid only when all
prerequisite current task-revision-set gates passed before it. It dirties its
owning delivery and invalidates old evidence. Establish the subsequent
committed/pushed tuple through delivery-keyed `revision-observed`, then apply
`delivery-observed` with the exact revision key and current lifecycle. Only a
newer committed and published observation clears tracker dirt. Rerun gates.

## Review Wait Recovery

Before replaying any review mutation, require the exact immutable reservation
packet, its ledger `review-provider-mutation-reserved` and
`review-provider-mutation-started` events, and the packet fingerprint bound to
the current generation/state/claim. The packet has no mutable attempt field.
The consumed marker is durable before provider dispatch; after it exists,
recovery may perform one read-only exact-artifact reconciliation only. A unique
marker-plus-target/body/actor artifact completes the journal. Missing,
conflicting, or ambiguous evidence records `failed-or-ambiguous` and
`needs-owner`; it never retries, resets the 45-minute deadline, deletes a
marker, or recreates a reservation.

Before any resumed provider-text mutation, reload the transport contract in
`worker.md`, recreate the opaque text file from current authorized data, and
take a fresh GitStack `repo snapshot` in the exact managed checkout. Require
the typed file flag and `--expected-worktree-fingerprint`; old snapshots and
old temporary files are not recovery authority. Preserve a confirmed provider
object/read-back as partial success, and never retry an ambiguous write. A
connector mutation is byte-verified only after an exact-target read-back.

Recompute the exact delivery revision before review work. Reuse a result only
for that tuple with all addressable findings dispositioned. Re-read stored
`finding_count` and `finding_comment_ids`; require equal cardinality. A
fix-required result with zero ids needs a fresh fix revision and review but no
thread receipt. For every nonzero id, preserve and revalidate the exact
GitStack reply and resolution receipts against their finding and resolution
revisions. Missing, conflicting, wrong-target, or stale receipts block; do not
replace them with raw GraphQL or a no-change disposition. A GitStack result
with `mutation_may_have_applied=true` remains blocked and is never retried.
Preserve an existing request's
original `wait_started_at` and deadline. Persist its single invocation before
the provider call with `max(0,floor(deadline-wait_invoked_at))`; zero is one immediate
check. A recorded invocation is never relaunched. Accept observations only for
the exact current request and revision while active-waiting.

If the waiter result remains pending, compare its observation time with the
immutable 45-minute deadline. Before the deadline, continue observing the
already-launched call; do not start another. At or after the deadline, require
the persistent PR warning, then record the one final
`waiting/timeout-accepted` observation with its `warning_ref`. The root Goal
remains active, the claim remains unchanged, and closeout continues. A
missing request, access or provider failure, findings, or missing warning is a
blocker. Never create a review schedule, pause a Goal, arm a heartbeat, or
relaunch the provider waiter. Old-revision waits remain inert history.

## Staged Closeout Recovery

Resume at the first incomplete closeout stage without requiring a later stage:

1. A task with all current proof but no seal may apply
   `task-terminal-sealed`.
2. An unchanged seal without terminal handoff may apply
   `terminal-handoff-recorded` from current delivery proof.
3. Once all tasks have terminal handoffs, independently reverify and apply
   `portfolio-terminal-verified`.
4. A verified portfolio with active root Goal may complete and read it back,
   then apply `portfolio-goal-completed`; already-completed matching evidence is
   adopted once and derives `portfolio_goal_state=complete`.
5. Only then run the complete terminal release/archive sequence from
   `cache-lifecycle.md`; an already
   released state may finish the same archive operation idempotently.

These are closeout transitions, not implementation resume. Never repair or
resume implementation during this interrupted completion transition. If any terminal fact
changed after a seal or root Goal completion, apply
`post-terminal-drift-recorded`. It preserves irreversible root Goal history, blocks
portfolio verification or archive, and requires owner action or a fresh run.

## Prepared Takeover Without Candidate State

When a recovered takeover claim has no candidate JSON because creation never
completed, initialize only from the current prepared journal and that
current claim's complete embedded adoption mappings. Verify each source, exact
task ref or explicit
no-task entry, Goal, immutable profile, title, and every delivery checkout. The
registration packet carries those mappings and ledger creation binds the
candidate claim. A resumed same-root run instead keeps its original claim; it
never rebinds state to a replacement fingerprint.

Do not infer identity from task titles, replaced-root prose, or archived state,
and do not create a task when the mapping records one. If candidate JSON exists,
validate it normally. Active Markdown or unsupported schemas block without
import, migration, rename, dual-read, retirement, or deletion.
