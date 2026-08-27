# Implement Worker Execution

This reference owns Feature Worker implementation and validation, optional
support, pre-candidate convergence, hosted-finding repair, and role-local
completion inside `implement-validate`. The orchestrator owns projecting the
canonical Worker handoff; the received handoff is self-contained for the Worker
and the sender-side orchestration contract is not a Worker phase dependency.
Use
[review-delivery.md](review-delivery.md) only after a committed candidate reaches
exact-HEAD native review or publication.
Use [states.md](states.md) for the canonical meaning of workflow nodes,
persisted status/checkpoint pairs, runtime-only modes, and terminal outcomes.

## Worker handoff and phase ownership

Consume and validate the received flat semantic Worker handoff. Resolve its
canonical source and current-phase references, then compare the requested
profile and Git target under the shared task-handoff contract. Do not load the
sender-side orchestration reference to validate the handoff. The initial
handoff contains the requested bootstrap-result contract, not post-creation
evidence. Return the authoritative bootstrap result from this Worker's first
turn; the orchestrator binds it to the independently observed Worker identity
before role-owned work.

On resume, accept only the changed exact-HEAD, authority, finding, topology, or
other material evidence plus the identifiers that bind it to the retained
assignment. Do not require the orchestrator to resend stable source contracts
or the previous prompt.

After accepting the handoff, the Feature Worker owns every safe local action in
its current phase until an existing semantic boundary is reached. It observes
the completion and result of its own implementation, validation, support, and
review work, interprets that result, and repairs or continues when the next
action remains inside its authority. Starting work, ending a command without
interpreting it, or waiting for a generic `continue` message is not a phase
boundary.

The Worker may complete its role-owned phase only at a registered node boundary:

- complete candidate-bound validation enters `candidate`; before first
  publication the same Worker continues through native review under the
  verified local-only boundary owned by review-delivery without a generic
  continuation message;
- a clean exact-HEAD native result completes `review-decision` and enters
  `publish-pr` for orchestrator-owned reservation and authorization;
- after first publication, a validated repair candidate enters `candidate`, or
  unchanged complete validation enters `final-verify`;
- a material semantic conflict enters `plan-question`;
- a required non-user evidence or capability failure enters
  `assignment-blocked`; or
- a run-wide unrecoverable failure enters `blocked`.

A user-authority question returns through `plan-question`; only the orchestrator
may subsequently enter `assignment-deferred`. When an external effect remains
pending and no safe local work remains, the Worker may hand back one typed
pending result bound to the exact operation, candidate, and observation lineage.
That handback retains the current node and phase ownership: it adds no workflow
or ledger state, is not a terminal result, and resumes the same Worker only when
the effect completes or another material delta creates local work. It never
requires a generic continuation request. The shared
[task handoff](../../../references/task-handoff.md) remains the canonical owner
of change-driven observation and update relay; this reference only narrows the
Worker's valid phase exits.

The Worker invokes publication or update only after the orchestrator reserves
and authorizes that exact effect. It uses the verified Worker worktree, observes
and interprets the G-owned result, and returns its typed receipt and readback.
It never reads or writes the ledger or treats its candidate report as
publication authority. The orchestrator remains the sole owner of reservation,
ledger mutation, provider reconciliation, hosted monitoring, and aggregate
completion.

## Pre-candidate convergence

Before first publication, keep the initial implementation inside
`implement-validate` until the Feature Worker has stabilized one coherent
pre-candidate draft. This is transient Worker behavior under the existing
`active @ worker-bootstrap` pair. It adds no workflow node, checkpoint, ledger
field, task role, or review authority, and it does not run for a verified
published repair governed by hosted review.

First integrate all planned writes and write-capable support results, then hold
the source tree stable while inspecting it. Run the cheapest deterministic
static or focused checks that exercise the changed surface and can expose an
obvious implementation, configuration, or test-harness failure. These checks
provide early feedback; they do not replace complete Feature validation.

Derive the need for an early critic from the current F-AC/T-AC mapping and
observable change risk. Use one bounded early challenge pass when the draft
materially involves parser, protocol, schema, arbitrary-input, aggregate-bound,
authorization, privacy, security, credential, lifecycle, retry, recovery,
idempotency, cancellation, concurrency, distributed-state, migration,
compatibility, cross-runtime, Unicode, platform, destination, packaging, or
linkage behavior, or when one invariant governs several equivalent paths. Do
not trigger the pass from Worker reasoning level, diff size, or available
helper capacity alone. When none of these risks applies, skip the critic rather
than adding a redundant review. Reuse the assignment's existing F-AC/T-AC
matrix as the invariant checklist; do not create another checklist registry or
persist critic state.

When the pass applies, keep it read-only and advisory. Prefer the existing
`critic-reviewer` support responsibility when optional delegation and usable
capacity are observed; otherwise the Feature Worker performs the same challenge
serially. Supply the stable draft, Feature contract, F-AC/T-AC mapping,
applicable risks, equivalent paths, and current check evidence. Require one
completed bounded finding set for that pass, consolidated and deduplicated by
violated invariant, affected equivalent paths, and missing regression evidence.
The result is not a claim of exhaustive findings and is not native-review or
candidate evidence. Partial helper relays do not trigger piecemeal repairs. If
no usable completed helper result is observed, fall back to the Worker's serial
challenge without blocking the assignment.

The Feature Worker triages the whole consolidated set before repairing every
actionable instance coherently, then runs focused gap-driven checks for the
repaired invariants and equivalent paths. Do not reflexively start another
critic for every repair; reassess only when the repair materially changes the
design or introduces a different risk class.

Before complete validation, reconcile every support attempt against observed
reality. For every helper independently observed as dispatched, either consume
one usable completed result or reject its output. When an actually launched
helper produces no usable result, the Feature Worker performs the equivalent
support work; never use `unavailable` or `unknown` to reconcile that attempt.
After all attempts are reconciled, record the single effective mode using the
task-profile precedence. A mixed helper set remains `delegated-support` when
any usable result was integrated; `serial-fallback` applies only when none was
integrated and the Feature Worker performed a selected support responsibility.
A rejected read-only attempt cannot block the Worker. Every unconsumed current
or future helper result is irrevocably outside the candidate; choosing to
integrate it later returns to `implement-validate`, creates a new HEAD, and
invalidates candidate-bound evidence. A write-capable attempt may cross the
stable barrier only after independently observed completion or cancellation
and worktree readback that accounts for every residual write. An attempt that
remains active may be disregarded only after proving that it is isolated from
the candidate worktree and every validation-relevant output, cache, lock,
device, database, and external state. Finish every source write, then
re-observe the assignment's frozen base and prerequisite HEAD vector. A
mismatched prerequisite or actual parent, base, or topology drift that has
superseded the Worker's ancestry must follow the existing reconciliation path
before spending the complete validation or native-review cycle. An advance of
the selected starting branch after the bootstrap snapshot for a standalone or
stack-root assignment, or pending hosted review or CI without concrete
assignment drift, is not itself a reason to wait.

After that stable barrier, commit and freeze the coherent source tree, verify
the worktree is clean and pinned to its full SHA, then run complete Feature
validation against that unchanged candidate. One complete pass is the normal
target, not a limit: a failed check, source change, or actual base,
prerequisite, or topology drift invalidates the affected evidence and requires
repair, a new commit, and a new complete pass before first publication.
Validation work may run concurrently only when every participant observes the
same frozen candidate and uses isolated outputs, caches, locks, and external
state. Otherwise serialize it. Bind the complete validation evidence to that
full candidate SHA before entering `candidate`.

## Optional Feature Worker support

The Feature Worker is the parent owner of one Feature member, its observed
Macro projection state and available local Task context, worktree, integration
branch, candidate HEAD, acceptance matrix, pre-publication native review,
hosted-finding repairs, and PR. Macro Tasks are planning projections, not
worker or PR boundaries. Optional support assignments are subordinate to that
lifecycle and are not additional Feature assignments. The parent may select:

- `code-analyst` for read-only repository, impact, and dependency analysis;
- `execution-assistant` for one explicitly bounded execution unit;
- `validation-assistant` for focused checks and validation evidence;
- `critic-reviewer` for the conditional read-only pre-candidate challenge and
  later independent design or regression challenges when applicable.

The parent supplies each helper with the current Feature ID, Plan Set revision,
available local Macro Task context, execution-unit scope, exclusive path
envelope, and validation intent. Helpers return evidence or a scoped change
proposal; they never edit or publish the Feature Plan, access the SQLite
ledger, mutate GitHub, create Feature Workers or planner tasks, or own final
delivery evidence. An execution assistant may write only within an exclusive
envelope or isolated helper context. The Feature Worker integrates the result
and owns the final candidate commit.

Before first publication, follow pre-candidate convergence, complete
candidate-bound validation, and mandatory local-only native review. After an actionable
hosted finding, treat it as evidence of a violated invariant rather than a
line-edit instruction. Repair every equivalent path governed by that invariant,
remain inside the Feature contract, and add or update focused regression
evidence without speculatively broadening scope. Freeze the repaired candidate
after focused validation and return it through `candidate`; after the
orchestrator reserves and authorizes the exact update, publish it under
review-delivery without native review. Hosted re-review remains orchestrator
monitored. When resumed for final validation, complete validation must pass on
the same published HEAD; a code change returns through `candidate`, while an
unchanged result enters `final-verify`.

Do not run overlapping writes in the same worktree. Use the delegation mode
precedence in [task-profile.md](task-profile.md); configured delegation or
observed capacity alone never proves that a helper started.
