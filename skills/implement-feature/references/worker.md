# Visible ChatGPT Desktop App Feature Spec Task

## Assignment

Create exactly one visible App task per implementation-eligible Feature Spec.
Record Spec/task/title/profile/assignment/lifecycle/results. Keep one `deliveries[]`
entry per affected repository for checkout, paths, commits, PR/revision,
review, CI availability and configured-CI results, tracker closeout, and mergeability.

Task ids, managed checkouts, assignment fingerprints, PR count, and internal subagent topology are
derived runtime evidence. They are not user options.

## Task Model Profile

Use the exact per-Spec profile resolved under `task-model-policy.md`. Pass its
model and thinking value to `codex_app__create_thread` when creating the visible
task and to every `codex_app__send_message_to_thread` call used to steer or
resume it. Never omit, substitute, or recompute either value after task
creation. Recovery and takeover preserve the recorded profile on the original
task; they never create a replacement to change it.

This profile governs the root-owned visible task. It does not create a separate
model-selection contract for the task's bounded internal subagents.

## Task Display Title

Give every created task exactly one root-owned display-title prefix. Resolve one
semantically relevant emoji from the validated Feature Spec title and its
dominant user-facing goal, use `🛠️` when no clearer choice exists, then
format `task_title` as `<emoji> <exact authored Feature Spec title>`. The prefix
is one emoji grapheme followed by one space; preserve the authored title
unchanged even when it already contains emoji. This is fixed derived UI
evidence, not a user option, Feature Spec field, source fingerprint, claim key,
scheduling key, branch component, or recovery identity.

Resolve and persist `task_title` once after the Spec enters the selected
DISPATCH set and before calling `codex_app__create_thread`. Reuse that exact
value for the task's lifetime; never recompute it during monitoring, steering,
recovery, or takeover. Apply the title through the root-owned App surface, not
through the worker prompt:

1. Create the managed visible task with `codex_app__create_thread` and its exact
   task profile.
2. If worktree setup returns only `clientThreadId`, record that creation evidence
   and wait for the existing managed-creation flow to expose the concrete
   `threadId`; never create another task.
3. Record the concrete task ref, call `codex_app__set_thread_title` with the
   persisted `task_title`, and observe the exact live title.
4. Advance beyond `created` only after both the title and assignment fingerprint are
   verified.

On delayed/ambiguous creation or title overwrite, load
`app-control-plane-delays.md`; preserve creation, never replace the task or let
the worker rename itself.

## Fixed Actions

Every task receives the same action set:

```text
inspect, edit, validate, complete-domain-closeout, move-local-issues-to-done,
commit, push, publish-or-update-pull-request, run-autoreview,
mark-ready-for-review, request-review, poll-review, fix-review, run-ci,
prepare-tracker-closeout, check-mergeability, report
```

Allowed paths narrow edit scope; they do not alter this action set or grant
scope expansion. The run authorization disclosed and covers these actions for
the accepted bundle. The task may not edit the orchestration run state, manage
sibling or root tasks, change branch or PR strategy, merge, release, deploy,
perform post-merge closure, or change target-repository instructions.

The action set is dormant during `baseline-only`. In that phase the worker may
only verify assignment/title/managed-checkout identity and prepare/run/verify
the registered `baseline-validation` manifests. It remains `created`; it cannot
edit source, commit, push, reserve provider mutation, reserve/call AutoReview,
emit gates, mutate trackers, or call Goal tools. The root sends one explicit
`baseline-accepted` continuation only after the atomic CAS and Goal activation;
that continuation enables the fixed action set without changing scope.

For a local Markdown issue, the move action is legal only when its tracker-owning
repository and exact active plus derived `done/` paths are already present in
the Execution Contract and exposed by the App-managed checkout.

Give GitStack only exact PR, `review_operation`, and `mutation_mode=apply` for an
authorized mutation. Before `poll-review`, report tuple/request evidence and
require root-issued `revision_key`, `wait_started_at`, and `wait_deadline`.
Before launch set `wait_invoked_at=now`, compute
`provider_timeout=max(0,floor(wait_deadline-wait_invoked_at))`, and report both to the root.
Start GitStack only after the root persists `review-wait-invoked`; that event is
single-launch authority. Use 10s/30s bounds when positive and one immediate
no-wait check at zero. Never relaunch, default, or segment it. Bind each result
to the persisted receipt and exact revision. Binding failure exits 4, not stale
or timeout-eligible; pending at 45 minutes requires the PR warning and
`timeout-accepted`.

## Provider Text Transport

Treat every provider-owned title, body, description, comment, reply, review,
release note, and warning as opaque UTF-8 bytes. Never place that text in argv,
an environment variable, a shell command string, command substitution, logs,
dry-run output, or errors. This boundary is global and required; the earlier
shell execution incident is evidence of the general risk, not a one-off review
special case.

For every GitStack provider-text mutation other than the typed review request:

1. Write each text field without interpolation to its own absolute regular
   non-symlink file outside the managed checkout. Use a literal file-write tool
   such as `apply_patch`; do not use `echo`, an interpolating heredoc, or a shell
   variable containing the text.
2. From the exact managed checkout, run GitStack `--json repo snapshot` and
   retain its SHA-256 `fingerprint` as the immediate pre-call worktree proof.
3. Invoke only the typed operation with `--title-file`, `--body-file`, or the
   operation's other file field plus
   `--expected-worktree-fingerprint <fingerprint>`. Inline text flags, parser
   aliases, generic API writes, and shell-built command lines are forbidden.
4. Require the result to prove the exact repository/PR/comment target,
   provider object id and URL, UTF-8 byte count and SHA-256, and unchanged
   worktree fingerprint. Do not print or persist the text itself as transport
   proof.

Use `reviews request --request-key --reservation-file --ledger-file` for Codex; load
`review-mutation-authority.md`; it owns the body and receipt. Use
`reviews comment`, exact-head one-target `reviews reply`, receipt-bound
`reviews resolve`, `reviews edit-comment`, and `reviews submit-review` for their
matching operations. `reviews address` is
read-only. Open a new PR with `publish open --title-file --body-file`; existing
PR text edits require the structured GitHub connector because GitStack has no
`publish edit` command. Issue and release text follows the GitStack skill's
connector-or-genuinely-file-backed rules; if no safe surface exists, stop.

On a failed or unreadable mutation, accept only GitStack's one exact-target
read-back result and never retry blindly. Preserve confirmed provider identity
as partial-success evidence when the subsequent worktree check fails. A
connector response alone is not byte verification: claim exact bytes only
after an exact-target read-back proves them.

This transport does not define Codex review-request content, exact-head
correlation, acknowledgment, request state, or waiting. The typed GitStack
request operation remains the sole owner of those semantics. It also
does not run through or extend `execution-manifest`; validation and AutoReview
retain their existing command-manifest boundary.

For local commit actions, use `$gitstack:git-commit` and keep
`commit_kind=regular` unless target-repository instructions require a targeted
fixup. Review or `$autoreview` feedback alone never selects a fixup. A required
`commit_kind=fixup|amend-fixup` must name one exact `target_commit`; ambiguous or
cross-commit corrections stop for owner direction. Never autosquash or rewrite
the published branch. Any resulting head change invalidates current-revision
review and CI evidence and repeats the fixed final gates.

## Managed Deliveries And Checkouts

Create the task through the App-managed worktree target before implementation.
Record one complete `managed-checkouts-observed` map of delivery key,
repository, checkout, branch, Git top-level, baseline revision/tree,
clean-status and execution-scope fingerprints, and isolation. A
multi-repository Spec remains one task. No task-level checkout/PR/revision exists.

If any checkout is missing or not isolated, stop as blocked. Never create,
remove, or repair raw Git worktrees, rotate the caller checkout, or fall back to
root or background implementation.

## Assignment And Dependency-Wait Contract

The root binds each newly created task to an immutable assignment fingerprint
covering the exact Feature Spec,
repositories and allowed paths, acceptance criteria, validation, and
gates including AutoReview, current-revision Codex review, CI when configured,
integration, and fixed terminal result
`pull-request-ready-for-merge-but-not-merged`. Derive it anew; never reuse a
prior assignment or fingerprint. Workers do not call Goal tools.

On recovery, verify the recorded assignment fingerprint and exact live task
title before advancing beyond `created` or resuming nonterminal work. A task
already recorded at the fixed terminal result reports without resuming
implementation. Never create a replacement task.

When the worker must wait for a root-owned transition, the root applies
`task-dependency-wait-started`. Its `resume_state` must equal the task's exact
current active phase. Resolution applies `task-dependency-wait-resolved` with
that same phase; it cannot jump to a different phase. The wait remains
nonterminal and never becomes `blocked` from elapsed turns. Authority tokens,
deadlines, leases, and host recovery are outside this contract.

## Execution

During baseline-only execution, run only the registered read-only projections
and report exact manifest/receipt byte fingerprints and complete canonical
diagnostic/content fingerprints. If the projection cannot be proven read-only,
diagnostics are ambiguous, or identity drifts, report `planning-required` or
`authorization-stale` and stop without source mutation.

After the root reports atomic acceptance and Goal activation, implement only the accepted bundle and prove substantive acceptance and
integration. Read the root-prepared canonical bundle manifest, verify its
digest, and execute only the assigned worker-owned `validation` and `autoreview`
command ids through `scripts/execution-manifest`; verify each receipt and report
its fingerprint. Never reconstruct cwd, argv, tool paths, finding ids, or hash
recipes from prose. Other fixed actions retain their existing owners and
contracts. For a nonempty final-issue `knowledge_delta`, complete the exact
Project Memory implementation-closeout after integration and require
`capture_outcome=captured`, every supplied accepted item and required named
target reconciled, named verified destinations, and complete documentation-diff
verification. `deferred`, `no-durable-change`, or a rejected or contradicted
accepted item blocks the task pending an owner decision or separately authorized
planning/implementation correction. For local tracker artifacts, after current
task-set substantive/integration/domain proof report the predeclared tracked
move and unchanged body for `source-moved`. It dirties/invalidates the delivery;
commit/push, report the new `revision-observed`, then current committed/published
`delivery-observed` before final gates. Publish/update each PR against the
discovered default branch through the provider-text contract above. Outside
the ready mutation's shell chain, record its exact number and URL plus the
returned target/text/worktree proofs. Run validation and `$autoreview`; when it or PR review
returns accepted findings, load `autoreview-fix-loop.md` and follow its typed
delta chain. Then convert any draft
to ready-for-review only by exact identity; a `gh` fallback is
`gh pr ready <number> --repo <owner/repo>`. Selectorless or branch inference is
forbidden. Re-read the same number; require unchanged URL and `isDraft=false`.
After that nonterminal transition, request mandatory current-revision review
through Codex, fix actionable findings, pass configured CI or report the
registered `not-configured` state without polling, prepare derived tracker
closeout, and check current GitHub mergeability. Declare terminal merge-ready
only while each PR lifecycle is `OPEN`, mergeability is conflict-free, and every
required base update, approval, and merge-queue eligibility condition passes.
Unknown or pending mergeability blocks; never enqueue or merge. A later head
change continues the evidence chain when the helper proves the same scope; a
base, merge-base, repository, or path-set expansion starts a new full lineage.
Follow the generated issues' dependency order inside the task; do not create a
task per issue.

Canonical states are `created`, `implementing`, `validating`, `draft-pr`,
`marking-ready-for-review`, `review-polling`, `fixing-review`, `ci`,
`preparing-tracker-closeout`, `checking-mergeability`, `dependency-wait`, `terminal-sealed`,
`merge-ready`, `blocked`, `needs-owner`, and `failed`. Post-terminal drift is a
separate closeout record, not a task state.

The root reads current task evidence before steering. A correction names the
observed drift, expected next state, and preserved scope. A stale or failed task
is resumed in the same visible task only after evidence is recorded. Restore
the recorded `task_title` on that same task when its live title drifts. If it
cannot be resumed, stop as blocked; never create a replacement task for that
Spec.

After takeover, initialize missing state only from the candidate claim's
validated embedded adoption mapping. Adopt each original task after verifying
its assignment fingerprint and complete delivery checkouts. No task ref or managed
`(repository, checkout)` pair may belong to two Specs. An explicit embedded
no-task entry with the exact pre-CLAIM profile is required before first creation,
and that first creation must use the embedded profile without reclassification.
Do not create a task when embedded, prior-state, or live App evidence records
one for the Spec;
inability to adopt or resume it is a blocker.

## Internal Subagents

The task may use bounded internal subagents when useful. They inherit its paths
and fixed flow, remain inside the same Feature Spec slot, and report through the
visible task. They never receive separate portfolio or tracker authority.

## Prompt

```text
Own this Feature Spec through pull-request-ready-for-merge-but-not-merged.

Assignment: <canonical source id; authored Feature Spec ref/title; feature slug>
Managed scope: <delivery, repository, checkout, branch, baseline, allowed paths>
Execution scope: <bundle, authorization, and execution-scope fingerprints>
Scope and acceptance: <exact requirements and acceptance refs>
Dependencies: <verified merged cross-Spec dependencies>
Validation/integration: <requirements, proof refs, command ids/manifests/digests>
Knowledge closeout: <exact final-issue delta or none>
Canonical bundle manifest: <absolute path and manifest/bundle digests>

Start baseline-only. Verify the exact assignment and checkout fingerprints,
then run only registered baseline-validation manifests and report their exact
byte fingerprints plus canonical diagnostics. Do not edit, commit, push,
reserve provider/AutoReview authority, emit gates, or call a Goal until the root
reports atomic baseline acceptance and Goal activation. If
this task is already terminal, report without resuming implementation. Never
create, read, update, complete, or block a Goal. Run each assigned manifest only
through its one bounded attempt; never launch directly, change its fixed policy,
or relaunch after release. Report attempt, timeout, output-limit, cancellation,
and cleanup evidence. The root alone renews the claim every 60 seconds and
authorizes cancellation after claim loss or monitor degradation. Work only in
the managed checkouts. Use fixed actions, persist the GitStack request receipt, and
pass it unchanged to the receipt-bound waiter under the root-issued 45-minute
deadline; if pending at deadline, post/report the persistent PR warning and
continue the remaining gates. Report arguments, readbacks, receipts, and
internal subagents.
Do not edit the run state, manage sibling tasks, widen scope, change delivery
strategy, merge, release, deploy, or perform post-merge closure. Continue until
every affected PR is ready to merge or report a concrete blocker.
```

## Report

Report one compact typed packet after each material milestone, attention request,
blocker, review-wait invocation, or terminal transition. Do not repeat unchanged
state or paste full command output; the root expands evidence only for a mismatch,
blocker, or independent terminal verification. Report task assignment evidence,
state, the complete delivery-keyed managed checkout map, changed files,
the exact task display title and observation evidence, task model, thinking
value, and profile decision reason, validation, delivery commits, exact PR
number/URL/revision, review/wait, CI availability and configured-CI results, current PR
lifecycle/conflict/mergeability state, required base-freshness, approval state,
merge-queue eligibility, and the observation tuple/time (or exact blocker),
prepared tracker closeout, internal subagents, blockers, drift, and next action.
When a knowledge delta exists,
report its actual `capture_outcome`, delta fingerprint, every verified named
destination, documentation-diff fingerprint, and relevant implementation
revision tuples, or the exact closeout blocker. Only the root validates and
applies lifecycle events to portfolio run state.
