# Codex Task Orchestration

Root alone creates or changes visible Codex tasks, titles, and archives through
the ChatGPT App. Root owns only controller bootstrap and the explicitly
allowed controller follow-ups below. Workers never create tasks; they send the
bounded direct peer messages defined below without routing routine
collaboration through root.

For every such change, root follows one crash-safe sequence:

1. call `app-operation begin` to record the intended operation in SQLite before
   changing the Codex task in the ChatGPT App, then retain its generated opaque
   `operation_id`; for `send-bootstrap`, also retain the deterministically
   derived `bootstrap_id`; retain the returned `launch_count` for every action;
2. perform the change through the ChatGPT App tools only when
   `app-operation begin` returns `launch_authorized=true`;
3. use both the immediate tool response and an independent reading of the
   actual task to build the typed observation for that exact `launch_count` and
   finish the recorded operation;
4. after an interruption, inspect the actual object first and record whether
   the change already happened;
5. never begin another logical operation to retry the same effect. Call
   `app-operation replay` only when `finish` reports
   `replay_authorized=true`; retain the same `operation_id`, use the incremented
   `launch_count`, and for bootstrap retain the same `bootstrap_id`.

Bootstrap may replay after `unknown` or `failed` readback because the worker
deduplicates its stable `bootstrap_id`; this provides exactly-once bootstrap
effect, not exactly-once delivery. The protected `create-worker`,
`set-worker-title`, `set-review-owner`, `set-root-title`, and `archive-worker`
actions may replay
only from `failed` with readback that authoritatively proves that launch had no
effect. A successful `set-review-owner` history permits one initial
`worker|root` selection and at most one `worker` to `root` reroute; the same
logical operation is idempotent and a conflicting new owner fails closed.
`send-worker-message` has no replay path. A pending operation is never
replayable, an immediate tool error is not proof of no effect, and no operation
is relaunched under a new logical identifier. SQLite stores only identity and
reconciliation references, never prompts, message bodies, or hashes.
`references/run-state.md` owns the exact operation lifecycle, observation
protocols, `launch_count`, `receipt_ref`, and `readback_ref` machine fields.
`create-scope-repair-task` and `send-scope-revision` follow the additional
identity and generation rules in `scope-repair-orchestration.md`.

If a terminal or reconciled `finish` response is lost, submit the identical
observation again with the same `launch_count`. The idempotent readback uses
the already normalized evidence, even when a previously verified checkout
directory has since disappeared, and reports the same replay authorization
implied by that action, status, and launch generation. When refining an
`unknown` observation, carry every previously recorded fact forward unchanged
and add only newly authoritative evidence.

## Root Title And Worker Creation

This section is reachable only after the worker-project preflight and any
explicitly authorized project setup have passed for every selected repository.
After at least one assignment owns its Feature Spec and head-branch claim:

1. Set and verify the exact immutable root title once. For one assignment use
   `🤖 Orchestrator · 1 Feature`. For two or more use
   `🤖 Orchestrator · N Features`, where `N` is the immutable total
   assignment count, including waiting or blocked assignments. Never update the
   root title as assignments progress. The title is UI evidence, never identity
   or durable state.
2. For each claimed assignment allowed by path and dependency serialization,
   create one visible Codex worker task with `environment=worktree` in the
   selected local Git project in the ChatGPT App. Pass
   `model=gpt-5.6-sol` and the assignment's resolved
   `thinking=medium|high|xhigh` from `task-model-policy.md`. Do not impose a
   numeric worker limit. The ChatGPT App creates the worktree and assigns it to
   the task; root never runs `git worktree add`. The successful creation
   observation records the literal task state `active` or `idle`; both mean
   that the exact task binding exists, not that implementation progress has
   begun.
3. Independently verify the stable task ID, checkout directory, and Git common
   directory, then set and verify `🛠️ Woker · <Feature Spec title>`.
4. Begin `send-bootstrap --review-owner worker|root` and copy only its returned
   canonical `review_owner=worker|root` into the full envelope with the recorded
   `bootstrap_id`, tracker backend, delivery type, source ref, validated local
   `repository_relative_spec_path` when applicable, Feature ID, repository key,
   repository, branch, allowed paths, issue graph, acceptance and validation
   budgets, safety,
   worker autonomy, checklist rules, final evidence, and every known peer's
   exact task, repository, branch, role, and checkout identity.
5. Verify the message was delivered to that exact task and that the worker
   accepted the same `bootstrap_id`. This starts complete implementation
   authority; there is no baseline-only prompt or later GO.

After recovery, read the accepted bootstrap from the task conversation and
compare its `bootstrap_id` and stable Spec and issue sections with the current
durable sources. The worker deduplication rules in `worker-execution.md` decide
whether a replay is the same logical bootstrap. If the accepted baseline cannot
be recovered exactly, fail closed; never replace it with a packet or message
hash.

## Scheduling And Monitoring

Do not impose a numeric worker limit. A worker recorded as `peer-input-ready`
is parked: its visible task and claim remain available for direct peer
follow-up. A proof owner that wakes a parked peer with mismatch evidence pauses
its own affected proof until that peer returns a replacement HEAD. Inside one
root, same-repository Specs run concurrently only when paths are disjoint and
no dependency orders them. Missing path evidence conflicts. Different roots
may own distinct Specs and head branches in one repository; delivery
verification exposes later conflicts. A delivery-ready worker releases its
claim.

There is no dedicated integration worker or reserved integration slot. Root may
create ordinary peer workers before their prerequisite HEADs are stable so they
can collaborate during implementation. When a later peer task is created, root
sends the missing exact peer identity to already-running workers through the
same recorded and verified message flow. Root does not relay routine technical
discussion, launch components, or test the combined system itself.

Workers communicate directly with their named peers. Before sending, a worker
reads the target conversation so it does not duplicate an already-delivered
fact. Peer messages may contain compatible interface clarifications, exact HEADs,
environment wiring, or factual mismatch evidence. They may not change outcome,
scope, dependencies, acceptance text or order, safety, validation budget, or
delivery type. Each worker remains solely responsible for repairs in its own
repository.

Read visible tasks at bounded intervals for coarse progress. Do not choose
design, issue order, rewrites, tests, validation, review fixes, or checklist
judgments for a coherent worker.

While runnable workers remain nonterminal, root keeps the current turn open and
uses bounded task waits. Worker progress or completion wakes that existing
wait. Root returns a final response only for a delivery-ready,
preimplementation-aborted, owner-abandoned, or declaratively blocked run. After a crash,
ChatGPT App restart, or premature task completion, continuation is
manual in the exact same root task; recovery reads the unfinished run and
authoritative SQLite, task, tracker, and repository state before taking action.
Never create a replacement root, heartbeat, worker-to-root wake, or synthetic
lifecycle for an unfinished run.

A declaratively blocked response does not call `run finish`. The blocked run
and its claims remain unfinished and exclusively bound to the same root task
until authoritative recovery or contract change permits that root to continue.

When a worker reports a valid out-of-envelope path, root follows
`scope-repair-orchestration.md`. It starts the separate planner task immediately
when authorized, may monitor an overlapping peer in parallel, and recomputes
the complete path overlap before restarting the original worker. This does not
create dynamic per-file claims: the durable envelopes and ordinary scheduling
gate remain authoritative.

## Allowed Follow-Up Messages

Root may send a follow-up only for recovered task facts, a newly created
peer's exact task/repository/branch/role/checkout identity, an authoritative
durable-source change already authored outside the active run and independently
read back, a reconciled scope revision from
`scope-repair-orchestration.md`, an early AutoReview capability reroute, a root-owned
AutoReview result, or an authoritative final-verification mismatch. An early
review-owner follow-up is the external effect of the recorded
`set-review-owner` operation and contains only the structured doctor result and
`review_owner=root`; it occurs before implementation, is reconciled by exact
operation ID/readback, and grants root review execution, not implementation
authority. A new
peer-identity follow-up carries identity only; it does not introduce technical
instructions or relay peer discussion. For a repairable mismatch, send only the
missing or inconsistent evidence and exact HEAD, tracker, task, or provider
refs when applicable.

A root-owned AutoReview result follow-up contains only the structured findings
and evidence refs returned by AutoReview, bound to the exact reviewed HEAD. It
may report that the review is clean or identify review findings, but it must not
add root-authored diagnosis, commands, implementation guidance, or repair
strategy. The worker owns finding acceptance, repair, validation, and
replacement evidence.

The stable-source mutation ownership table in `feature-spec-contract.md` is
binding here. Root never edits a stable Feature Spec or issue field, asks the
worker to edit one, or converts a direct user request into a planning mutation.
It blocks the assignment and retains its claim while an external planning owner
corrects the source. Root may resume through `assignment resume` only after
rereading the complete authoritative source and proving that it restores the
exact stable contract already accepted by the run. The separate scope-revision
operation is the sole way to rebind the planner-authored monotonic path
expansion. Any other changed stable contract cannot be rebound onto
the retained assignment or claim and requires a new run after existing-owner
reconciliation. The recovery follow-up contains the exact source and readback
refs only.

Allowed example: “Final verification shows PR HEAD `def`, while validation
evidence is bound to `abc`.”

Forbidden example: “Rerun test X and modify file Y.”

Outside the verbatim structured AutoReview result, root provides no diagnosis,
commands, implementation guidance, checklist judgment, or repair strategy.
Diagnosis, repair, validation, and replacement evidence remain worker-owned.
Durable-contract drift is different: record the assignment as blocked instead
of suggesting repair.

For a root-owned review, require the worker to build the review handoff with:

```bash
<implement-feature-skill-root>/scripts/verify-ready --json review-candidate \
  --checkout <managed-checkout> \
  --branch <target-branch> \
  --base-sha <startup-base-sha>
```

The worker forwards the returned `base_sha` and `head_sha` without shortening,
expanding, or reconstructing either value. Root reruns the same command against
the same checkout and requires exact JSON identity before review. It then uses
AutoReview branch mode with that exact base, `--review-phase full`, and
`--evidence-output`; commit mode is not a reroute substitute because it cannot
open the branch evidence chain needed after accepted fixes. Root returns only
findings and evidence to the worker and never edits the candidate.

Before root sends a controller message, record `send-worker-message` in SQLite. After sending, verify
the immediate response and independently read the exact task conversation,
then finish the recorded operation. Controller follow-ups are not replayable;
an unresolved follow-up remains unresolved rather than being resent under
another operation. Store no message body, hash, or worker technical state.
Omit `model` and `thinking` from every `send_message_to_thread` call so the
worker keeps the exact profile selected at creation; never override or
reclassify it during follow-up.
