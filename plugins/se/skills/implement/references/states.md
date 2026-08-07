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

Do not use `reviewing` or `plan-question` as assignment statuses. Review is an
active assignment at checkpoint `native-review`; a plan question is a deferred
assignment at checkpoint `plan-question`.

## Workflow nodes

The workflow has 23 nodes. Node scope identifies whether the node coordinates
the whole run, one assignment, or the current invocation.

| Node | Scope | Description |
| --- | --- | --- |
| `intake` | Run | Accept an explicit implementation or resume request for published Feature Plan Sets. |
| `source-preflight` | Run | Verify the hosted Plan Sets, Feature members, Macro Tasks, registries, and relations. |
| `runtime-preflight` | Run | Verify repositories, destinations, required roles, and required G-owned workflows. |
| `prepare-run` | Run | Derive assignments, execution units, path envelopes, dependencies, and delivery topology. |
| `schedule` | Run | Select the next runnable assignment, published-PR observation, or aggregate action. |
| `delivery-gate` | Run | Decide which unfinished assignments are dependency-ready and safe to start. |
| `worker-bootstrap` | Assignment | Create or resume the Feature Worker and bind its destination, worktree, branch, and base. |
| `implement-validate` | Assignment | Implement and validate the complete Feature outcome or surface one bounded product question. |
| `plan-question` | Assignment | Present one product decision that requires explicit user authority. |
| `candidate` | Assignment | Verify a clean committed candidate HEAD and its acceptance evidence. |
| `native-review` | Assignment | Run exact-HEAD native review in the owning Feature Worker. |
| `review-decision` | Assignment | Send a clean candidate to publication or return actionable findings for repair. |
| `publish-pr` | Assignment | Push the exact candidate and create or update its draft pull request. |
| `stack-reconcile` | Assignment | Verify the immediate parent, base, ancestry, stack order, and link for a stacked PR. |
| `candidate-published` | Assignment | Verify that PR publication and any required stack link match the exact candidate HEAD. |
| `delivery-monitor` | Run | Observe ready transition, hosted review, CI, provider disposition, and stack drift for published assignments. |
| `final-verify` | Assignment | Verify all exact-HEAD acceptance, review, CI, topology, closing-reference, and provider evidence. |
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
| `worker-bootstrap` | Worker identity, destination, worktree, branch, and base are the last durable recovery boundary. |
| `native-review` | A committed candidate exists and exact-HEAD native review is the last durable recovery boundary. |
| `plan-question` | One bounded product decision is recorded outside the ledger and awaits user authority. |
| `candidate-published` | Publication readback and any required stack-link readback matched the exact candidate HEAD when checked. |
| `final-verify` | Acceptance, review, CI, topology, closing references, and provider disposition passed for the exact final HEAD. |

### Canonical assignment pairs

| Pair | Meaning |
| --- | --- |
| `active @ worker-bootstrap` | The Worker owns implementation and validation. |
| `active @ native-review` | The Worker owns review, review repair, or publication preparation. |
| `active @ candidate-published` | A repair or rebase resumed from the last published boundary after reacquiring the path claim. |
| `deferred @ plan-question` | The user owns the next product decision. |
| `blocked @ <last-durable-checkpoint>` | A non-user blocker prevents progress; preserve the last trustworthy recovery boundary. |
| `delivery-pending @ candidate-published` | Publication is verified; the orchestrator owns monitoring and the Worker does not poll. |
| `delivery-ready @ final-verify` | The exact final HEAD satisfies the complete Implement delivery contract. |

`candidate-published` is also the same-repository child-development trigger. It
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

Provider dispositions are exact-HEAD observations returned by
`$g:github-delivery-status`. They are never run statuses, assignment statuses,
or operation results.

| Disposition | Description | Implement interpretation |
| --- | --- | --- |
| `ready` | Required hosted gates are observed satisfied for the exact PR HEAD. | Eligible for `delivery-ready @ final-verify`; `merge_boundary=none`. |
| `ready-with-manual-action` | Required evidence is satisfied, but G attributes the remaining boundary to a restricted manual branch action. | Eligible for `delivery-ready @ final-verify`; `merge_boundary=manual`. |
| `pending` | Known hosted work or evidence is incomplete. | Continue bounded orchestrator monitoring. |
| `blocked` | Hosted policy, review, or checks currently prevent readiness. | Monitor or report the attributed blocker; do not confuse it with an assignment or operation state. |
| `conflicting` | The PR cannot currently merge cleanly. | Resume the owning Worker only when implementation evidence must change. |
| `unknown` | Hosted evidence is missing, stale, ambiguous, or incomplete. | Reconcile; never infer readiness. |

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
| `merge_boundary=none` | The accepted provider disposition is `ready`. |
| `merge_boundary=manual` | The accepted provider disposition is `ready-with-manual-action`; the remaining manual action stays outside Implement authority. |
| `complete` | Every eligible Feature has one verified PR-ready output and aggregate reconciliation succeeded. |
| `deferred` | All remaining work awaits explicit user authority. |
| `blocked` | Required evidence, capability, identity, authority, or reconciliation remains unavailable. |

## Recovery rules

- Treat ledger state as a recovery index, never as proof of live external state.
- Re-read the authoritative plan, Worker, worktree, repository, PR, exact HEAD,
  review, checks, provider disposition, and stack relationship on resume.
- Reacquire the exact path envelope before resuming Worker writes.
- Preserve `delivery-pending @ candidate-published` while monitoring remains
  clean and the exact publication evidence is current.
- Any candidate HEAD change repeats validation, native review, publication
  readback, `delivery-pending @ candidate-published`, monitoring, and final
  verification.
- Persist `delivery-ready @ final-verify` only after all final requirements pass
  for the same exact HEAD.
- Retain Feature claims for deferred or blocked runs; release them only on the
  successful aggregate path.
