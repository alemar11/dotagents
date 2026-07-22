# ChatGPT Task Orchestration

Root alone creates or changes visible Codex tasks, titles, messages, archives,
and the lifecycle Goal through the ChatGPT desktop app. Workers never create
tasks or manage the Goal.

For every such change, root follows one crash-safe sequence:

1. record the intended operation in SQLite before changing the ChatGPT desktop
   task or Goal;
2. perform the change through the ChatGPT desktop app tools only when
   `app-operation begin` returns `launch_authorized=true`;
3. use both the immediate tool response and an independent reading of the
   actual task or Goal to finish the recorded operation;
4. after an interruption, inspect the actual object first and record whether
   the change already happened;
5. repeat the change only when authoritative evidence proves it had no effect.

A pending or unknown change is never launched again under another key. SQLite
stores only identity and reconciliation references, never prompts, message
bodies, or hashes. `references/run-state.md` owns the exact `app-operation`,
`receipt_ref`, and `readback_ref` machine fields.

## Goal And Worker Creation

After at least one assignment owns its Feature Spec and head-branch claim:

1. Create the root lifecycle Goal and independently verify that it is active.
2. Set and verify the exact root title. For one assignment use
   `👨🏻‍💻 Feature Orchestrator`. For two or more use
   `👨🏻‍💻 Multi-Feature Orchestrator (R/N)`, where `N` is the immutable total
   and `R` counts assignments in `pr-ready` or `local-branch-ready`. Start at
   `0/N`; input-ready, blocked, active, and waiting assignments do not increment
   it. The title is UI evidence, never identity or durable state.
3. Keep Goal progress coarse: scheduling, worker count, blocked, and final
   verification. Do not mirror issue phases.
4. For each claimed, dependency-ready, path-disjoint assignment up to three,
   create one visible Codex worker task with `environment=worktree` in the
   selected ChatGPT desktop project. The ChatGPT desktop app creates the
   worktree and assigns it to the task; root never runs `git worktree add`.
5. Independently verify the stable task ID, checkout directory, and Git common
   directory, then set and verify `🛠️ <Feature Spec title>`.
6. Send one full bootstrap naming tracker backend, delivery type, source ref,
   repository, branch, allowed paths, issue graph, acceptance and validation
   budgets, safety, worker autonomy, checklist rules, and final evidence.
7. Verify the message was delivered to that exact task. This starts complete
   implementation authority; there is no baseline-only prompt or later GO.

After recovery, read the accepted bootstrap from the task conversation and
compare its stable Spec and issue sections with the current durable sources.
If the baseline cannot be recovered exactly, fail closed; never replace it with
a packet or message hash.

## Scheduling And Monitoring

At most three workers may be live. Inside one root, same-repository Specs run
concurrently only when paths are disjoint and no dependency orders them.
Missing path evidence conflicts. Different roots may own distinct Specs and
head branches in one repository; delivery verification exposes later conflicts.
A delivery-ready worker releases its claim and frees a slot.

A dedicated integration Spec counts as another visible Codex worker task.
Dispatch it only after every prerequisite has stable input-ready repository,
branch, HEAD, and ChatGPT-created worktree evidence and a slot is free. Its
bootstrap includes the exact vector and executable integration prose. Root
never launches components or tests the combined system itself.

Read visible tasks at bounded intervals for coarse progress. Do not choose
design, issue order, rewrites, tests, validation, review fixes, or checklist
judgments for a coherent worker.

## Allowed Follow-Up Messages

Root may send a follow-up only for recovered task/Goal facts, an authoritative
durable-source change, or an authoritative final-verification mismatch. For a
repairable mismatch, send only the missing or inconsistent evidence and exact
HEAD, tracker, task, or provider refs when applicable.

Allowed example: “Final verification shows PR HEAD `def`, while validation
evidence is bound to `abc`.”

Forbidden example: “Rerun test X and modify file Y.”

Root provides no diagnosis, commands, implementation guidance, checklist
judgment, or repair strategy. Diagnosis, repair, validation, and replacement
evidence remain worker-owned. Durable-contract drift is different: record the
assignment as blocked instead of suggesting repair.

Before sending, record `send-worker-message` in SQLite. After sending, verify
the immediate response and independently read the exact task conversation,
then finish the recorded operation. Store no message body, hash, or worker
technical state.
