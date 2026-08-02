# Implement Codex Task Orchestration

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
effect, not exactly-once delivery. The protected task-creation, title-
initialization, and archive actions may replay only from `failed` with readback
that authoritatively proves that launch had no effect.
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

## App Task API And Title Initialization

Use the current ChatGPT App tool declarations as the runtime capability
contract. Inspect the exact signatures of `codex_app__create_thread`,
`codex_app__set_thread_title`, and `codex_app__set_thread_archived` before any
startup mutation, and pass only fields present in those declarations. The
creation declaration may expose an optional `title`; this protocol intentionally
keeps canonical title initialization in its separately recorded title operation,
so it must not claim that `title` is unsupported or add it without verification.
The title operation must use the real `threadId`, the requested `title`, and no
other field unless the inspected declaration explicitly exposes it. The
cleanup operation is likewise valid only with its declared fields. If title
initialization, cleanup, or any required argument is unavailable or unverifiable,
stop as `unsupported-runtime` before beginning a task operation or creating any
task.
A `create_thread` response is usable only when it yields or can be reconciled
to the real `threadId`; a client-only identifier is not sufficient for title
initialization or bootstrap.

The title mutation below is the normal initialization step immediately after
creation. The prompt is never title evidence, and a `create_thread` response is
not evidence that an undocumented field was accepted. Do not pass undocumented
fields to any App operation.

## Root Title And Worker Creation

This section is reachable only after the worker-project preflight and any
explicitly authorized project setup have passed for every selected repository.
After at least one assignment owns its Feature Spec and head-branch claim:

1. Begin `set-root-title`, call `codex_app__set_thread_title` for the root, and
   independently read back the exact immutable title once. For one assignment
   use `🤖 Implement Feature · 1 Spec`. For two or more use
   `🤖 Implement Feature · N Specs`, where `N` is the immutable total
   assignment count, including waiting or blocked assignments. Never update the
   root title as assignments progress. The title is UI evidence, never identity
   or durable state.
2. For each claimed assignment allowed by path and dependency serialization,
   create one visible Codex worker task with `environment=worktree` in the
   selected local Git project in the ChatGPT App. Pass
   `model=gpt-5.6-sol` and the assignment's resolved
   `thinking=medium|high|xhigh` from `task-model-policy.md`. Keep the canonical
   title in the separately recorded title operation; if the implementation ever
   passes `title` at creation, do so only after verifying that exact argument in
   the live declaration. Use this exact no-authority
   preparation prompt: `This visible task is being prepared as an Implement
   Feature worker. Do not inspect, edit, branch, test, publish, or mutate
   anything yet. Wait for the controller's full bootstrap envelope.` Do not
   impose a numeric worker limit. The ChatGPT App creates the worktree and
   assigns it to the task; root never runs `git worktree add`.
3. Independently verify the stable task ID, checkout directory, Git common
   directory, and literal task state `active|idle` in the `create-worker`
   observation. The initial title is not part of the creation proof. Both task
   states mean that the exact task binding exists, not that implementation
   progress has begun.
4. Begin `set-worker-title` for the recorded worker, call
   `codex_app__set_thread_title` exactly once with the recorded `threadId` and
   exact canonical title, using no additional field unless the live declaration
   exposes it, and independently read back that exact title before finishing the
   operation. A missing or
   normalized-to-different title returns `effect_warning=worker-title-drift`
   with `cleanup_required=archive-worker`; bootstrap remains forbidden. Do not
   repair drift with another title operation. The successful creation and
   title receipts remain recorded so root can archive the pre-bootstrap task,
   independently prove the exact recorded checkout path is absent, call
   `assignment abort`, and release only that claim. If the checkout still exists
   as a file, directory, or symlink, retain the claim and block cleanup. Treat
   permission, I/O, or any other inspection error as unknown presence and retain
   the claim; only `ENOENT` or `ENOTDIR` proves absence. If no assignment
   started, finish an all-aborted run as `preimplementation-aborted`. If a
   sibling already started, wait until every sibling is terminal and finish the
   mixed run as `abandoned`, never as a successful delivery.
5. Begin `send-bootstrap` and copy its returned `bootstrap_id` into the full
   envelope with the GitHub Issue source ref, Feature ID, repository key,
   repository, branch, allowed paths, issue graph, acceptance and validation
   budgets, safety,
   worker autonomy, checklist rules, final evidence, and every known peer's
   exact task, repository, branch, role, and checkout identity.
6. Verify the message was delivered to that exact task and that the worker
   accepted the same `bootstrap_id`. This starts complete implementation
   authority. The creation prompt is transport-only and grants no implementation
   authority; there is no baseline-only implementation phase or later GO.

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
   GitHub PR delivery. Each worker remains solely responsible for repairs in its own
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
`scope-repair-orchestration.md`, or an authoritative final-verification
mismatch. A new
peer-identity follow-up carries identity only; it does not introduce technical
instructions or relay peer discussion. For a repairable mismatch, send only the
missing or inconsistent evidence and exact HEAD, tracker, task, or provider
refs when applicable.

The worker sends the native `codex review` result summary and evidence refs
bound to the exact reviewed HEAD. Root may read and relay those facts as
coordination evidence, but never launches review, adds diagnosis, or supplies
repair strategy. The worker owns finding acceptance, repair, validation, and
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

Outside the worker's verbatim native review result, root provides no diagnosis,
commands, implementation guidance, checklist judgment, or repair strategy.
Diagnosis, repair, validation, and replacement evidence remain worker-owned.
Durable-contract drift is different: record the assignment as blocked instead
of suggesting repair.

Before its worker-owned review, the worker builds the review handoff with:

```bash
<implement-skill-root>/scripts/verify-ready --json review-candidate \
  --checkout <managed-checkout> \
  --branch <target-branch> \
  --base-sha <startup-base-sha>
```

The worker forwards the returned `base_sha` and `head_sha` without shortening,
expanding, or reconstructing either value to its native review invocation.
`codex review --base <base-branch>` reviews the complete branch delta. The
worker reruns it after every accepted fix and binds the final result to the
current HEAD. Root only verifies the resulting evidence and never edits or
reviews the candidate.

Before root sends a controller message, record `send-worker-message` in SQLite. After sending, verify
the immediate response and independently read the exact task conversation,
then finish the recorded operation. Controller follow-ups are not replayable;
an unresolved follow-up remains unresolved rather than being resent under
another operation. Store no message body, hash, or worker technical state.
Omit `model` and `thinking` from every `send_message_to_thread` call so the
worker keeps the exact profile selected at creation; never override or
reclassify it during follow-up.
