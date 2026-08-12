# Implement State Model

This reference is the canonical human-readable state model for `se:implement`.
The workflow registry in `SKILL.md` remains the structural source of truth for
nodes and edges. This reference owns the plain-language meaning of those nodes,
persisted status/checkpoint values, external dispositions, runtime-only modes,
and output labels.

## How to read state

These namespaces are related but not interchangeable:

| Namespace | Question it answers | Persistence |
| --- | --- | --- |
| Workflow node | What is the orchestrator doing now? | Not necessarily persisted |
| Status | Who owns the next action, or is this object finished? | Run or assignment row |
| Checkpoint | What was the last durable recovery boundary? | Run or assignment row |
| Feature-claim state | Does this run still own the Feature? | Feature-claim row |
| Operation result | Did one reserved side effect occur? | Operation row |
| Provider disposition | Does the exact PR HEAD satisfy hosted delivery policy? | External observation |
| Runtime-only mode | What is live in the application or transient control plane? | Not ledger state |
| Output label | How is verified delivery reported to the user? | Final report |

Use `status @ checkpoint` when showing one persisted pair. The left side is the
status and the right side is the checkpoint. For example:

```text
delivery-pending @ candidate-published
delivery-ready @ final-verify
```

A checkpoint is historical recovery evidence. It never proves that a Worker,
worktree, path claim, PR, review, check, or stack relationship is still current.
Re-read live state before another side effect or dependent Worker bootstrap.

## Canonical lifecycle

The normal assignment path is:

```text
active @ worker-bootstrap
  -> active @ native-review
  -> delivery-pending @ candidate-published
  -> delivery-ready @ final-verify
```

After every assignment reaches `delivery-ready @ final-verify`, the run moves
through `active @ release-claims` and ends at `complete @ complete`.

The bounded alternate paths are:

- `deferred @ plan-question` when the user owns the next assignment decision;
- `blocked @ <last-durable-checkpoint>` when required evidence, capability,
  identity, or reconciliation is unavailable;
- `active @ candidate-published` while the same Worker is resumed to repair or
  rebase a previously published candidate.

Do not use `reviewing` or `plan-question` as assignment statuses. Pre-publication
native review is an active assignment at checkpoint `native-review`; a hosted
finding repair is active at checkpoint `candidate-published`; a plan question
is a deferred assignment at checkpoint `plan-question`.

## Workflow nodes

The workflow has 23 nodes. Node scope identifies whether the node coordinates
the whole run, one assignment, or the current invocation.

| Node | Scope | Description |
| --- | --- | --- |
| `intake` | Run | Accept one or more exact caller-supplied parent Feature issue refs for implementation or resume. |
| `source-preflight` | Run | Resolve only the supplied parent issues, verify each parent Feature semantic contract and Feature dependencies, and classify Macro projections as complete, partial, or absent without GitHub label or Issue Type metadata. |
| `runtime-preflight` | Run | Verify repositories, destinations, required roles, required G-owned workflows, and each selected or default starting branch's refreshability. |
| `prepare-run` | Run | Derive assignments, refreshed base snapshots, execution units, path envelopes, dependencies, and delivery topology. |
| `schedule` | Run | Select the next runnable assignment, published-PR observation, or aggregate action. |
| `delivery-gate` | Run | Decide which unfinished assignments are dependency-ready and safe to start from one current exact base snapshot. |
| `worker-bootstrap` | Assignment | Create or resume the Feature Worker, accept an initial detached or attached checkout at the verified exact base, then establish and bind its Feature branch before content writes. |
| `implement-validate` | Assignment | Derive technical units and T-AC, implement and validate the Feature, or run complete final validation for a published repair; an unchanged published HEAD may proceed directly to final verification. |
| `plan-question` | Assignment | Present one semantic conflict that cannot be resolved without changing outcome, scope, F-AC, or Feature dependencies. |
| `candidate` | Assignment | Verify a clean committed candidate HEAD and its acceptance evidence; route an unpublished candidate to native review and a published repair directly to PR update. |
| `native-review` | Assignment | Run exact-HEAD native review in the owning Feature Worker before first PR publication. |
| `review-decision` | Assignment | Before first publication, send a native-clean candidate to publication or return native findings for repair. |
| `publish-pr` | Assignment | Push the exact candidate; create the draft PR after native review, or update the verified existing PR directly for a hosted repair. |
| `stack-reconcile` | Assignment | Verify the immediate parent, base, ancestry, stack order, and link for a stacked PR. |
| `candidate-published` | Assignment | Verify that PR publication and any required stack link match the exact candidate HEAD. |
| `delivery-monitor` | Run | Observe ready transition, authoritative hosted review, CI, and stack drift for published assignments. |
| `final-verify` | Assignment | Verify exact-HEAD F-AC/T-AC, review, CI, topology, Macro projection reporting, and source-derived closure-intent evidence. |
| `assignment-blocked` | Assignment | Record a non-authority blocker while independent assignments continue. |
| `assignment-deferred` | Assignment | Record a user-authority wait while independent assignments continue. |
| `release-claims` | Run | Atomically release all Feature claims after every assignment is delivery-ready and operations are resolved. |
| `deferred` | Invocation | Stop this invocation because all remaining work requires user authority; the run is resumable. |
| `complete` | Run | Finish immutably after assignments are ready, claims are released, and operations are resolved. |
| `blocked` | Invocation | Stop this invocation because required evidence or capability is unavailable; the run is resumable. |

## Run state

### Run statuses

| Status | Description |
| --- | --- |
| `active` | The orchestrator may schedule, monitor, reserve effects, or reconcile the run. |
| `deferred` | This invocation ended because all remaining work requires explicit user authority; preserve claims and resume later. |
| `blocked` | This invocation ended because required evidence, capability, identity, or reconciliation is unavailable; preserve claims and resume after the condition changes. |
| `complete` | The run is immutable: every assignment is delivery-ready, claims are released, and operations are resolved. |

### Run checkpoints

| Checkpoint | Description |
| --- | --- |
| `prepare-run` | The run exists and orchestration preparation is the last durable boundary. |
| `schedule` | The run has reconciled current assignments and may choose its next action. |
| `release-claims` | Every assignment is `delivery-ready @ final-verify`; claim release is the next aggregate action. |
| `complete` | Claims were released, operations were resolved, and aggregate completion was recorded. |

### Canonical run pairs

| Pair | Meaning |
| --- | --- |
| `active @ prepare-run` | Initial durable run state. |
| `active @ schedule` | Normal orchestration and monitoring state. |
| `active @ release-claims` | The run is ready to release its complete Feature claim set. |
| `deferred @ deferred` | The invocation paused because all remaining work requires user authority. |
| `blocked @ blocked` | The invocation stopped because all remaining work requires an external recovery condition. |
| `complete @ complete` | Immutable successful terminal state. |

Only `complete` is permanently terminal. `deferred` and `blocked` are terminal
outcomes for the current invocation but remain resumable run statuses.

## Assignment state

### Assignment statuses

| Status | Description |
| --- | --- |
| `active` | The Feature Worker or orchestrator owns an implementation, review, publication, repair, or rebase action. |
| `deferred` | The assignment awaits explicit user authority; independent assignments may continue. |
| `blocked` | The assignment cannot progress because required non-user evidence or capability is unavailable; independent assignments may continue. |
| `delivery-pending` | The exact candidate is published, the Worker is inactive but resumable, and the orchestrator owns hosted monitoring. |
| `delivery-ready` | Final exact-HEAD verification passed; the assignment may participate in aggregate claim release. |

### Assignment checkpoints

| Checkpoint | Description |
| --- | --- |
| `worker-bootstrap` | Worker identity, destination, worktree, established Feature branch, refreshed base branch, and exact base SHA are the last durable recovery boundary; the earlier task bootstrap may observe detached HEAD at that SHA. |
| `native-review` | A committed candidate exists and pre-publication exact-HEAD native review is the last durable checkpoint; an applied `first-pr-publication` operation overrides its review-transport meaning while stack reconciliation is still pending. |
| `plan-question` | One bounded product decision is recorded outside the ledger and awaits user authority. |
| `candidate-published` | Publication readback and any required stack-link readback matched the exact candidate HEAD when checked. |
| `final-verify` | Acceptance, review, CI, topology, minimal durable PR-body content, and registry-derived closure intent passed for the exact final HEAD; `closingIssuesReferences` is diagnostic only. |

### Canonical assignment pairs

| Pair | Meaning |
| --- | --- |
| `active @ worker-bootstrap` | The Worker owns implementation and validation. |
| `active @ native-review` | Before first publication, the Worker owns native review, native-finding repair, or publication preparation. If `first-pr-publication` is already `applied`, this pair is only the coarse pre-stack durable checkpoint: hosted review is authoritative and native review must not restart. |
| `active @ candidate-published` | A hosted finding repair or rebase resumed from the last published boundary after reacquiring the path claim; native review does not restart. |
| `deferred @ plan-question` | The user owns the next product decision. |
| `blocked @ <last-durable-checkpoint>` | A non-user blocker prevents progress; preserve the last trustworthy recovery boundary. |
| `delivery-pending @ candidate-published` | Publication is verified; the orchestrator owns monitoring and the Worker does not poll. |
| `delivery-ready @ final-verify` | The exact final HEAD satisfies the complete Implement delivery contract. |

`candidate-published` is also the same-repository child-development trigger. It
unlocks child bootstrap only when no applicable CI check on that exact parent
HEAD is confirmed failing. Pending CI remains non-blocking; a confirmed failure
may be exempt only by G-owned diagnosis that verifies it as exclusively
infrastructure or flaky and unrelated to candidate correctness. The checkpoint
does not assert hosted review, CI, mergeability, provider readiness, Feature
completion, or merge. Any relevant HEAD, base, or stack-link drift invalidates
the dependent evidence and requires live reconciliation.

## Feature-claim states

| State | Description |
| --- | --- |
| `active` | This run exclusively owns the canonical Feature ref. |
| `released` | A successfully completed run released the Feature for future ownership. |

Deferred and blocked runs retain active claims. Release the complete claim set
only from `active @ release-claims`, after every assignment is
`delivery-ready @ final-verify` and every operation is resolved.

## Operation results

| Result | Description | Completion effect |
| --- | --- | --- |
| `pending` | The effect is reserved but its outcome is not reconciled. Use this for a temporary inability to proceed. | Blocks claim release and completion. |
| `applied` | The effect occurred and its receipt plus authoritative readback prove it. | Resolved and immutable. |
| `not-applied` | Authoritative readback proves that the effect did not occur. | Resolved and immutable. |
| `unknown` | An attempt may have occurred but its outcome is ambiguous; preserve receipt and readback evidence. | Blocks completion and may be refined once. |
| `blocked` | The effect is definitively inapplicable for this exact action and subject, authoritative readback proves non-application, and the reservation must not be retried. | Resolved and immutable. |

Do not use operation result `blocked` for a temporary prerequisite, unavailable
path claim, pending authority, or retryable provider condition. Leave that
operation `pending` and resume the same reservation after the condition changes.

## Provider dispositions

Provider dispositions are optional exact-HEAD observations returned by
`$g:github-delivery-status`. They are never run statuses, assignment statuses,
or operation results, and Implement never requires them for completion.

| Disposition | Description | Implement interpretation |
| --- | --- | --- |
| `ready` | Optional provider policy gates are observed satisfied for the exact PR HEAD. | Informational only; never a completion gate. |
| `ready-with-manual-action` | Optional provider evidence is satisfied except for a manual branch action. | Informational only; never a completion gate. |
| `pending` | Optional hosted policy evidence is incomplete. | Report diagnostically; do not block an otherwise verified PR. |
| `blocked` | Optional hosted policy currently prevents provider readiness. | Report diagnostically; do not confuse it with an Implement blocker. |
| `conflicting` | Optional provider observation reports a merge conflict. | Reconcile only when implementation or stack evidence must change. |
| `unknown` | Optional provider evidence is missing, stale, ambiguous, or incomplete. | Report diagnostically; never infer merge readiness. |

## Runtime-only modes

These values describe live application or transient control-plane state and are
not stored as ledger statuses.

| Domain | Mode | Description |
| --- | --- | --- |
| Feature Worker | active | The Worker may execute only while its exact path envelope is held. |
| Feature Worker | inactive but resumable | The Worker is preserved after candidate publication, performs no writes, and never polls its PR. |
| Path claim | held | The assignment exclusively owns its normalized write envelope. |
| Path claim | released | The assignment has no write authority; reacquire before repair or rebase. |
| Delegation | `delegated-support` | A bounded helper task and usable result were independently observed. |
| Delegation | `serial-fallback` | The Feature Worker performed the same support work itself. |
| Delegation | `unavailable` | The runtime could not provide optional delegation. |
| Delegation | `unknown` | Delegation evidence was insufficient and no helper was claimed. |

## Output labels

Output labels summarize verified delivery. They are not persisted assignment
statuses and never imply merge or post-merge closure.

| Output | Description |
| --- | --- |
| `standalone-ready` | A standalone PR is `delivery-ready @ final-verify` on its exact HEAD. |
| `stack-ready` | A stacked PR is `delivery-ready @ final-verify`, and every lower parent in its selected chain is current and delivery-ready. |
| `complete` | Every eligible Feature has one verified PR-ready output and aggregate reconciliation succeeded. |
| `deferred` | All remaining work awaits explicit user authority. |
| `blocked` | Required evidence, capability, identity, authority, or reconciliation remains unavailable. |

## Recovery rules

- Treat ledger state as a recovery index, never as proof of live external state.
- Re-read the authoritative plan, Worker, worktree, repository, PR, exact HEAD,
  review, checks, and stack relationship on resume. Optional provider
  diagnostics may be retained but never replace these required observations.
- Reacquire the exact path envelope before resuming Worker writes.
- Preserve `delivery-pending @ candidate-published` while monitoring remains
  clean and the exact publication evidence is current.
- Before verified first-PR publication readback, a candidate HEAD change
  repeats validation and native review. Once the assignment-bound
  `first-pr-publication` operation for the canonical Feature ref is `applied`
  with a receipt and authoritative PR identity/HEAD readback, every later candidate
  repeats affected validation, publication readback, hosted review, CI, and
  final verification without native review, even when stack reconciliation has
  not yet established `candidate-published`; complete validation is required
  on the exact final HEAD.
- A PR-body-only change invalidates only body readback. A base, parent, or
  stack-link change invalidates only the affected integration and descendant
  evidence. An interrupted hosted monitor resumes the same review lineage
  without a duplicate request.
- Persist `delivery-ready @ final-verify` only after all final requirements pass
  for the same exact HEAD.
- Retain Feature claims for deferred or blocked runs; release them only on the
  successful aggregate path.
