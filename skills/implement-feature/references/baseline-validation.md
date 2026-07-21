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
baseline-only task and obtain complete terminal-or-idle task-stop evidence;
stopped does not mean archived. While every original App-managed checkout still
exists, apply `preimplementation-aborted`. Only after that event is accepted may
the root call `set_thread_archived` for those tasks, release the claim, and
archive the ledger. It proves Goal state is still pending, no delivery revision,
provider/AutoReview authority, review, gate, source mutation, or partial
baseline acceptance exists, and each checkout still has its baseline revision
and a status fingerprint proving no Git-visible changes. Release with the typed
`preimplementation-abort` receipt and
archive with the same reason/evidence. Never synthesize Goal state.
