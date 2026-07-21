# Baseline Validation And Immutable Scope

## One-Grant Contract

This contract is global and wanted: every normal Implement Feature run obtains
one informed initial grant for the complete declared implementation scope, and
baseline validation happens before source mutation. The grant binds the exact
bundle bytes, repository deliveries, allowed paths, validation plan, and fixed
workflow through `execution_scope_fingerprint`. It never authorizes a later
path, command, adapter, tool identity, or policy change.

Complete read-only intake, delivery preflight, command classification, and
validation-plan derivation before asking. If any authored validation command has
no closed deterministic read-only adapter, or a required implementation path is
not declared, return `planning-required` without CLAIM or mutation. Do not run
an authored mutating command to discover whether it is safe.

After the grant, any source, manifest, tool, argv, adapter, policy, checkout,
branch, revision, tree, or scope drift returns `authorization-stale` before
implementation. After implementation starts, an undeclared changed or newly
required path is a scope violation and the task becomes `needs-owner`. Never ask
a second permission question, recapture a baseline, or widen `allowed_paths`.

## Baseline-Only Phase

CLAIM and REGISTER may create internal ownership/state after authorization.
Workers may then be created only to bind their App-managed checkout, title,
assignment, and complete checkout map and to run registered
`baseline-validation` manifests. They remain in `created` and may not edit
source, commit, push, reserve GitStack provider mutations, reserve or call
AutoReview, emit terminal gates, or perform tracker mutation. No external root
Goal exists in this phase; ledger Goal `pending` is internal pre-creation state.

Every managed checkout binds repository, checkout, Git top-level, branch,
baseline revision, tree, clean-status fingerprint, isolation evidence, and the
execution-scope fingerprint. A baseline manifest uses only the closed adapter
selected during intake and must prove the command caused no Git-visible checkout
change. Unpathable, ambiguous, duplicate, noncanonical, or unstable diagnostics
fail closed.

## Atomic Acceptance

The root submits exactly one `baseline-accepted` CAS containing
every registered `(task_key, delivery_key, validation_key)` tuple. The CAS binds
the current generation, state and claim fingerprints, execution-scope
fingerprint, exact manifest and receipt byte SHA-256 values, checkout identity,
authored/projected argv, adapter/policy, tool identities, fixed execution-policy
fingerprint, and the complete sorted
diagnostic set with each file's content SHA-256. Missing, duplicate, stale, or
partially valid rows reject the entire event and authorize no mutation.

Each baseline command has one fixed 60-minute monotonic attempt. Timeout, output
limit, interruption, or cleanup failure prevents atomic acceptance and routes
to the existing typed preimplementation stop; no baseline attempt is
automatically relaunched.

Only after that event accepts every task may the root create and record its one
lifecycle Goal and allow workers to enter `implementing`.

## Existing Debt And Non-Regression

`clean-required` accepts no baseline diagnostics. The only debt exception is
`unchanged-outside-scope`: a closed adapter may record pre-existing
diagnostics outside the delivery's allowed paths. Final validation passes only
when every such canonical diagnostic and file-content fingerprint is unchanged,
all in-scope diagnostics are gone, and adapter, tool/version, authored argv,
projected argv, and policy identities still match. Tool or command drift
invalidates the authorization/baseline; it is never recaptured during the run.

Before `scope`, record canonical changed paths for the current
revision, require no untracked paths, require every change inside registered
scope, and require AutoReview's review scope to equal that exact set.

## Preimplementation Stop

When baseline preparation or acceptance cannot complete, first stop every
baseline-only task and obtain complete typed task-stop evidence. Record one
checkout disposition per delivery: `not-bound` when binding never completed,
`present-clean` when the original checkout still matches its complete baseline
identity, or `removed` when the path and worktree registration are gone and the
local target branch is absent or baseline-equal. Apply
`preimplementation-aborted` before archiving any remaining task whose checkout
is still present. An already archived task is acceptable only when its checkout
disposition remains independently provable; the disposition is evidence, not
permission to recreate it. Only after the event is accepted may the root call
`set_thread_archived` for any remaining tasks, release the claim, and archive
the ledger. It proves Goal state is still pending and that no delivery revision,
provider/AutoReview authority, review, gate, source mutation, or partial
baseline acceptance exists. Each
present checkout must match its full baseline identity; each removed checkout
must have no remaining worktree registration or advanced target branch. Release
with the typed `preimplementation-abort` receipt and archive with the same
reason/evidence. Never synthesize Goal state.

## Fresh Start Orchestration

A fresh start is orchestration, not a ledger state. The ordinary imperative
implementation invocation automatically selects it without another owner
question only when one complete recovery pass proves all of these facts:

- the current root owns the identified active claim and supported ledger for
  the exact accepted bundle and execution scope;
- Goal and implementation baseline remain pending and the typed abort proves
  there is no implementation, delivery, command, provider, review, gate,
  handoff, tracker, or source-mutation evidence;
- the run is control-plane-unrecoverable because a recorded managed checkout is
  absent and unregistered, or a recorded task is conclusively
  `archived`, `failed`, or `unavailable` after the complete App retry contract;
- the cause is lost task/checkout infrastructure, not deterministic baseline,
  planning, authorization, source, tool, adapter, policy, or scope failure; and
- this invocation has not already performed an automatic fresh start.

An overlapping claim owned by another root remains a takeover case and never
authorizes an automatic fresh start.

Then perform exactly one sequence: retire the old run through
`preimplementation-aborted`, archive remaining tasks, release its claim,
archive and verify its ledger, and re-enter the normal bootstrap with new claim,
ledger, task, and checkout identities. Never reset state in place, reuse the
retired task, or describe the old run as restarted. If the fresh baseline fails,
stop normally; never start over again automatically in the same invocation.

A still-recoverable eligible run continues by default. Only an explicit owner
request to `start over` selects retirement instead. Ambiguous task, checkout,
mutation, ownership, bundle, or scope evidence always blocks; explicit wording
does not override it. The composition is unavailable after Goal activation,
baseline acceptance, any implementation-phase task, delivery revision, command
journal entry, provider operation, review, gate, handoff, or tracker mutation.
Such a run requires its existing recovery path or owner intervention.
