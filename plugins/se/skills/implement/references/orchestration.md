# Implement Orchestration

This reference owns Feature Plan Set scheduling, textual-plan interpretation,
Feature Worker dialogue, user plan questions, and delivery-topology routing.
Use [states.md](states.md) for the canonical meaning of workflow nodes,
persisted status/checkpoint pairs, runtime-only modes, and terminal invocation
outcomes.

Before any hosted publication or user-facing hosted relay, apply the shared
[hosted-content-safety.md](../../../references/hosted-content-safety.md)
contract to the exact final content. G owns transport and readback.

## Control plane

The orchestrator coordinates one run containing one or more caller-supplied
GitHub parent Feature issue refs and the authoritative Feature Plan Sets and
Macro projections resolved from them. Each selected Feature member retains its
Feature ID, repository binding, one Feature
assignment, one observed Macro projection state, one Feature Worker, and one PR
output. The orchestrator derives technical execution units and T-AC criteria
from the Feature semantic contract plus any available verified Macro context
before scheduling; the Plan Set does not contain the runtime execution graph.

PR delivery readiness is established from exact PR publication, current CI,
hosted review feedback, and stack evidence. The orchestrator is the sole
delivery-monitoring and aggregate lifecycle owner. Feature Workers never poll
their own PRs while inactive. Branch protection and rulesets are outside the
Implement completion contract.

Run independent Features concurrently when their repositories, derived path
envelopes, real cross-Feature code dependencies, Feature-level `blocked_by`
context, and observed runtime capacity are safe. A same-repository dependent
may enter a later execution wave as soon as its immediate parent is
`candidate-published` and no applicable CI check on that exact parent HEAD is
confirmed failing. Pending CI remains non-blocking. A confirmed failure blocks
the child unless G-owned diagnosis verifies it as exclusively infrastructure or
flaky and unrelated to candidate correctness; parent delivery readiness is not
a worker-bootstrap gate. Serialize unsafe overlap and cross-repository outcome
dependencies. Do not create synthetic dependencies, impose a fixed worker cap,
or stop independent Features because one assignment is blocked, deferred, or
delivery-pending.

Before any Feature Worker starts, claim the complete sorted Feature set in one
ledger transaction. A conflicting active claim blocks startup without partial
claims or a competing orchestrator. Release all claims atomically after
terminal reconciliation.

## Application-task control hierarchy

Apply the shared
[task handoff](../../../references/task-handoff.md) at both levels of the
Implement hierarchy. The invoking task controller creates or resumes the one
orchestrator in the invoking ChatGPT application project, independently
observes its project-visible stable task identity, state, and title, and
verifies that the orchestrator's structured bootstrap result is bound to that
identity. The orchestrator's first turn is assigned-task bootstrap: it
self-checks authoritative task-scoped execution evidence before ledger,
repository, Worker, or hosted effects and never creates another orchestrator
for the same run.

Creation and resume are mutually exclusive per role identity. A fresh run
creates one new orchestrator and one new Worker per selected Feature. A
validated resume reuses only the exact previously bound project-visible task.
Create a not-yet-created role only after authoritative evidence proves no prior
creation effect was applied. If a retained role identity is missing or cannot
be verified, stop with `unsupported-runtime` and do not create a replacement.

After that bootstrap, the orchestrator becomes the task controller for every
Feature Worker. It freezes each Worker request, creates or resumes the Worker
in the application project for that Worker's target repository, independently
observes the project-visible stable Worker identity, and binds the Worker's
structured bootstrap result to it before accepting normal updates. The Feature
Worker reads its own authoritative task-scoped context and performs its
bootstrap self-check before implementation or worktree content writes. It does
not create or resume another Feature Worker. A Worker's profile may
intentionally differ from the orchestrator's; compare the Worker only with its
assignment-specific request.

Both controller edges are required application-task handoffs, not subordinate
delegation. Failure to establish either project-visible edge follows the shared
`unsupported-runtime` fail-closed path. Optional support may begin only below a
verified Feature Worker and can never be promoted into either required role.

An unstructured Worker self-report is not bootstrap evidence. A missing or
unobservable authoritative child profile follows the shared
`unsupported-runtime` rules, while a present authoritative exact-Worker
profile that differs from the request is `effective-profile-mismatch`. A
present evidence identity bound to another task is `task-identity-mismatch`,
and a present Git execution-target difference is
`execution-target-mismatch`. All blocked outcomes preserve and reconcile the
same Worker without replacement. The orchestrator verifies the bootstrap
identity binding but does not duplicate the Worker's raw profile read. It
compares the Worker's independently observed Git execution target with the
frozen handoff. These bootstrap checks add no ledger state and do not change
the runtime workflow graph.

## Starting-branch selection and freshness

Treat `starting_branch` as an optional caller-owned selection scoped to one
target repository. One unqualified selection is valid only for a
single-repository run. For multiple repositories, require repository-qualified
selections for every override; a repository without an override uses its own
authoritative provider default branch. Resolve the selection during
runtime-preflight and reject a missing, ambiguous, inaccessible, or
wrong-repository branch. Never fall back silently to the provider default,
current checkout, or another local branch after the caller supplied a value.

Before every standalone or root Feature Worker bootstrap wave, refresh the
selected branch from its authoritative upstream through the G-owned branch
transport and read back its full remote tip SHA. The source ref supplied for
the application-managed worktree starting state must resolve to that tip. A fetch-only
receipt, stale remote-tracking ref, current checkout HEAD, or branch name
without exact-SHA readback is insufficient. Updating the caller's active
checkout is not required. Any local branch update used for bootstrap must be
fast-forward-only and preserve unrelated or dirty checkout state; never merge,
rebase, force-update, discard user changes, or change branches to manufacture
freshness. When an exact refreshed starting ref cannot be established safely,
block before creating a Feature Worker.

Freeze the refreshed branch as the wave's `base_branch` and full `base_sha`.
Every standalone or root assignment for the same repository in that wave must
start from that exact snapshot. Re-read the authoritative branch tip
immediately before each worktree creation. If it changed, stop the remaining
bootstraps, refresh the snapshot, and recompute the unstarted wave; never mix
two starting SHAs inside one bootstrap wave. After worktree creation, verify
that its initial HEAD resolves to the frozen `base_sha` before the Worker may
write repository content. The initial checkout may be detached or attached;
detached HEAD at the exact frozen SHA is the normal valid state for an
application-managed isolated worktree. Do not require the selected
`base_branch` to be checked out, and do not require a Feature `head_branch` to
exist during the assigned-task bootstrap. A repository, remote, worktree, or
SHA mismatch blocks that assignment without treating the task or worktree
receipt as implementation progress.

After the assigned-task identity, profile, and initial execution target match,
the Feature Worker creates or checks out its deterministic `head_branch`
through the G-owned branch workflow from the unchanged `base_sha`. It then
reads back the branch and exact HEAD before any repository content write. Only
that post-bootstrap branch readback may establish the durable
`active @ worker-bootstrap` assignment checkpoint. On recovery from that
checkpoint, the recorded `head_branch` is required and a detached or different
checkout is drift that must be reconciled. Apply the same sequence to a
stacked child: its initial detached HEAD may equal the verified immediate
parent candidate SHA, after which the child creates its own `head_branch`.

The selected starting branch applies to standalone assignments and the root
of every same-repository stack. A stacked child instead starts from its
verified immediate parent's `candidate-published` branch and exact candidate
SHA. That parent base overrides the repository selection only for the child;
it does not change the selected landing branch at the root of the stack.

## Macro plan interpretation and execution units

The orchestrator resolves only the exact caller-supplied parent issue refs,
then reads the authoritative Feature Plan Set manifest, hosted sibling
registry, each selected parent Feature semantic contract, and any reachable
local Macro Task children before deriving a transient technical execution unit
set. It verifies set identity/revision, Feature membership, outcome, scope,
non-goals, F-AC identities and high-water evidence, and Feature-level
`blocked_by`. Sibling entries provide consistency and dependency evidence but
never expand the selected implementation set. Record Macro projection
availability as `complete`, `partial`, or `absent`. Validate every reachable
local child and quarantine missing, extra, duplicate, cross-parent, cyclic, or
mismatched Task projections from execution and closure intent. Those defects
do not block a worker when the parent Feature semantic contract is sufficient;
they block only when they also make that contract or Feature-level dependency
topology ambiguous. Never create or repair hosted Task projections. GitHub
labels and native Issue Types are outside this workflow and must not be read,
searched, inferred, validated, mutated, or used as gates.

When native GitHub issue dependencies are observable, compare `blockedBy` and
reciprocal `blocking` with the body-backed Feature and Macro graphs. Treat the
native relation as diagnostic projection evidence only. A missing, failed,
unavailable, unknown, extra, or stale provider edge is reported without
blocking or changing scheduling, stack intent, execution units, or closure.
Never infer a semantic edge from provider metadata and never repair a native
dependency during Implement.

Feature-level `blocked_by` relations are planning-owned hard outcome
dependencies and may cross repositories. Repository identity controls their
deterministic delivery projection: every same-repository edge is mandatory
stack intent and every cross-repository edge is scheduling-only. Neither form
creates technical execution-unit edges; the orchestrator still derives real
implementation prerequisites independently. Macro `blocked_by` relations are
planning context within one parent Feature and never create worker or PR
boundaries. The orchestrator may combine, reorder, or internalize them while
preserving every available Macro Task outcome and Feature criterion.

Derive deterministic `T-AC-NN` criteria for the assignment and preserve their
identities across candidate revisions. Every T-AC must map to one or more
current F-AC identities and may only make their technical proof more specific.
It cannot replace, weaken, delete, or reinterpret an F-AC or change outcome,
scope, non-goals, or Feature dependencies. Every F-AC needs direct exact-HEAD
evidence or at least one mapped T-AC; every T-AC needs exact-HEAD evidence.

If an upstream Feature named by `blocked_by` is missing, unverified, or outside
the selected implementation scope, keep the dependent assignment blocked or
deferred; never silently implement it as if the relation were absent. A
same-repository dependent becomes worker-runnable only from a verified
`candidate-published` parent branch and exact HEAD whose applicable current-head
CI has no confirmed failure, except for a failure verified by G-owned diagnosis
as exclusively infrastructure or flaky and unrelated to candidate correctness.
CI that is still pending does not block the child. A cross-repository dependent
remains ordered by the verified upstream outcome and keeps a standalone PR.

Each derived unit must have:

- one observable technical outcome;
- repository and path scope;
- implementation and validation intent;
- Feature-criterion mapping;
- deterministic T-AC criteria and their F-AC mapping;
- real implementation prerequisites;
- evidence needed from the Feature Worker.

Use the smallest useful technical vertical units. Keep implementation and validation
layers together when they serve one outcome. Do not split a unit merely by
database, API, UI, test, documentation, or tracker layer unless that layer is
independently valuable.

Dependency edges mean real implementation prerequisites. Path overlap,
capacity, preferred order, Feature-level delivery projection, and
cross-repository prerequisites remain separate scheduling or topology facts
and never become technical execution-unit edges automatically.

The orchestrator owns this translation and may ask the Feature Worker to
refine technical units and T-AC criteria during implementation. It must
preserve every F-AC and every available Macro Task outcome, but it may derive
missing execution coverage directly from the parent Feature contract. It must
not rewrite or publish the Feature Plan or its Macro Task registry.

## User plan questions

Implement resolves missing execution decomposition, ordinary technical
ambiguity, and acceptance specificity autonomously. Enter `plan-question` for
the affected assignment only when no semantic-preserving implementation is
possible: F-AC contradict each other or the outcome, satisfying the contract
requires changing outcome or scope, Feature dependencies are contradictory or
cyclic, or a selected Feature is blocked by an unselected or unfulfilled
Feature. Present the bounded conflict to the user with its evidence and impact.
Persist `deferred @ plan-question` without claiming that the ledger stores the
question body or a separate plan-question identity. Keep independent Features
moving.

Do not create a separate Feature planner task automatically. If the user's
answer requires changing the published Feature Plan Set, report an explicit
se:feature maintenance request as the recovery action and preserve the
worker's useful implementation evidence where safe. Technical implementation
ambiguity remains inside Implement and never becomes a Feature question.

## Execution and delivery topology

For every Feature member, bootstrap exactly one Feature Worker. The worker
executes its derived units in deterministic prerequisite order inside one
isolated worktree. During implementation, commit frequently at coherent
unit-of-work boundaries. It may use optional bounded support assignments when
live delegation and usable worker capacity are observed; otherwise it
continues
serially. Parallelism is only between Features whose paths, repositories,
dependencies, Feature-level scheduling context, and live capacity are safe.

Derive standalone or stacked delivery separately from execution order:

- standalone: no same-repository Feature-level `blocked_by` parent exists;
- stacked: one same-repository immediate parent is selected from the hosted
  relation set and its verified `candidate-published` branch and exact HEAD are
  the integration base.

Serialization caused only by path overlap, capacity, or preferred order
remains standalone. For same-repository fan-in, select one immediate parent
only when its candidate already contains every other required same-repository
prerequisite HEAD. Otherwise block the dependent assignment for explicit Plan
Set reconciliation; never invent an ordering edge or silently choose a base.

Before bootstrapping a stacked child, reread the parent PR, branch, full HEAD,
`candidate-published` checkpoint, publication readback, and stack capability.
Observe applicable CI on that exact parent HEAD. A confirmed failing check keeps
the child out of the runnable wave unless G-owned diagnosis binds the failure to
that check run and verifies it as exclusively infrastructure or flaky and
unrelated to candidate correctness. Pending CI is allowed. The parent may remain
`delivery-pending`; a stale or ambiguous candidate keeps only that child out of
the runnable wave. Never silently degrade to standalone.

If a parent changes after a child starts, invalidate the descendant's
integration, hosted review, CI, and readiness evidence. Return the parent to its
worker, then rebase, revalidate, republish, and hosted-review descendants bottom
to top without restarting native review. The
orchestrator coordinates this sequence but never edits or rebases worker code.

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
repaired invariants and equivalent paths. Do not reflexively
start another critic for every repair; reassess only when the repair materially
changes the design or introduces a different risk class.

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
and worktree readback that accounts for every residual write. An
attempt that remains active may be disregarded only after proving that it is
isolated from the candidate worktree and every validation-relevant output,
cache, lock, device, database, and external state. Finish every source write,
then re-observe the assignment's frozen base and prerequisite HEAD vector. A
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

## Candidate publication and central delivery monitoring

After pre-publication native review and first publication, or after a hosted
repair updates the existing PR without native review, the orchestrator verifies
repository, PR, branch, full candidate HEAD, draft state, the minimal durable SE-owned PR body,
registry-derived closure intent in that body, and any required stack link. If
available, it records GitHub's
`closingIssuesReferences` as optional provider diagnostics; that field never
blocks publication. Only the remaining exact-head and topology readback
establishes `candidate-published`.
Checkpoint the assignment as `status=delivery-pending` and
`checkpoint=candidate-published`, release its transient active path claim, and
mark the Feature Worker inactive but resumable. This checkpoint is the only
same-repository child-development checkpoint, but a confirmed applicable
current-head CI failure still blocks child bootstrap unless it has the bounded
G-owned infrastructure-or-flaky diagnosis described above. Pending CI remains
non-blocking. This is not delivery completion.

Return to `schedule` after every candidate publication. Run the scheduler
immediately only for runnable work or materially new evidence; when all work is
pending, retain the current observations under the shared change-driven
monitoring policy. Interleave delivery-pending PR lineages fairly. The
orchestrator combines G-normalized review, CI, exact-head, and parent/base
evidence and never asks inactive Workers to poll. An unchanged pending
observation does not trigger a no-work scheduling cycle. A clean review and CI
observation enters final verification when complete validation is already
current. When a published repair has only focused validation, resume the same
Worker through `implement-validate` for complete validation on that exact
HEAD. An unchanged result proceeds directly to `final-verify`; a changed
candidate returns through publication and hosted review.

For an actionable finding, evidence mismatch, or parent drift, preserve the
exact PR, head, provider artifact, and observation fingerprint. Reacquire the
Worker's path envelope before resumption, then contact the same Worker with
only that bounded evidence. If the path claim is unavailable, keep the repair
pending without permitting overlapping writes. Because the verified PR already
exists, hosted review remains authoritative: a new candidate repeats affected
validation, publication readback, `candidate-published`, and central monitoring
without native review. Preserve unaffected Feature, Worker, PR, operation, and
topology evidence instead of restarting the assignment globally.

## Optional Feature Worker support

The Feature Worker is the parent owner of one Feature member, its observed
Macro projection state and available local Task context, worktree, integration branch, candidate HEAD,
acceptance matrix, pre-publication native review, hosted-finding repairs, and
PR. Macro Tasks are planning
projections, not worker or PR boundaries.
Optional support assignments are subordinate to that lifecycle and are not
additional Feature assignments. The parent may select these bounded
responsibilities:

- `code-analyst` for read-only repository, impact, and dependency analysis;
- `execution-assistant` for one explicitly bounded execution unit;
- `validation-assistant` for focused checks and validation evidence;
- `critic-reviewer` for the conditional read-only pre-candidate challenge and
  later independent design or regression challenges when applicable.

The parent supplies each helper with the current Feature ID, Plan Set revision,
available local Macro Task context, execution-unit scope, exclusive path
envelope, and validation intent. Helpers
return evidence or a scoped change proposal; they never edit or publish the
Feature Plan, never access the SQLite ledger, never mutate GitHub, never create
Feature Workers or planner tasks, and never own final delivery evidence. An
execution assistant may write only within an exclusive envelope or isolated
helper context. The
Feature Worker integrates the result and owns the final candidate commit.
Before first publication it follows pre-candidate convergence, complete
candidate-bound validation, and mandatory native review. After
`candidate-published` it follows the hosted repair loop: focused validation,
publication, hosted re-review, then complete validation on the exact final HEAD.

Do not run overlapping writes in the same worktree. When a selected support
responsibility cannot use delegation because it is unavailable, unknown, or
has zero capacity, the Feature Worker performs that responsibility; these
conditions do not block the Feature Worker. After reconciling every selected
responsibility, record exactly one effective mode using the task-profile
precedence: `delegated-support` when any usable helper result was integrated,
otherwise `serial-fallback` when the Feature Worker performed the selected
support, and otherwise the applicable no-support `unavailable` or `unknown`
mode. The orchestrator reports that mode but does not treat configured
delegation or capacity as proof that a helper started.

## Feature Worker dialogue

The orchestrator may exchange only bounded control-plane messages:

- verified bootstrap and plan revision;
- execution-unit or coarse milestone request;
- evidence-only mismatch or reconciliation request;
- actionable hosted-review or parent-drift resumption request;
- plan-question decision request;
- terminal-state request.

Every message is edge-triggered by a new bootstrap result, state transition,
actionable evidence fingerprint, authority decision, exact-HEAD or topology
change, or missing terminal report. Do not repeat a milestone, terminal,
status-only, heartbeat, or "continue" request without a material intervening
change and reconciliation of the prior message effect.

It must not prescribe code, files, commands, tests, review fixes, or design.
The Feature Worker owns implementation semantics, conflict resolution,
validation, candidate evidence, pre-publication native review, hosted-finding
repairs, and fixes.

The orchestrator is the only creator of implementation assignments and
Feature Worker tasks. A Feature Worker never creates another Feature Worker or
planner task. It may create subordinate support assignments only when the
optional delegation preflight is available; those assignments remain outside
the implementation ledger and never replace the parent Feature Worker.

## Ledger boundary

The orchestrator alone reads and writes the SQLite WAL ledger. Feature Workers
return bounded evidence through the task handoff and never access ledger state.
Store only durable claims, assignment identity, checkpoints, exact candidate
heads, user-authority waits, and idempotent side-effect reservations. Do not
store plans, prompts, messages, execution-unit bodies, findings, or routine
worker state.

`delivery-pending @ candidate-published` is one coarse status/checkpoint pair,
not two sequential states or a second delivery engine. The ledger never proves
that a Worker is inactive, that a PR remains current, or that a path envelope
is free; recover each fact from the application, repository, provider, and
transient control plane.

On resume, reread the authoritative plan, repository execution target, current
base and full HEAD, worker identity, and hosted delivery state before another
side effect. Ledger text never proves external state.
