# Implement States

Implement owns a small transient workflow graph. It has no persisted run
status, assignment status, checkpoint, effect journal, or delivery-state
machine. On resume, the orchestrator re-enters the graph through `intake`,
re-establishes ownership at `claim-repositories`, and derives the continuation
at `reconcile` from externally owned evidence.

## Workflow nodes

| Node | Kind | Meaning |
| --- | --- | --- |
| `intake` | action | Resolve the exact selected Feature set, its body-backed dependencies, repositories, and visible home. |
| `claim-repositories` | action | Atomically acquire or reuse repository ownership and bind one correlated visible orchestrator. |
| `reconcile` | validation | Reconstruct current truth from Feature, Git, candidate-review, pull-request, hosted-review/CI, and task owners before another effect. |
| `schedule` | decision | Compute the ready frontier and choose serial or bounded concurrent work. |
| `deliver-feature` | action | Run one verified worker lane through implementation, validation, and a stable local commit; after clean candidate review, resume the same lane for standalone or stacked pull-request publication, ready transition, and exact-HEAD hosted review and CI convergence. Several ready lanes may occupy this node concurrently. |
| `review-candidate` | validation | Run a fresh independent read-only adversarial review of one complete locally committed Feature delta with the required fixed profile. Several independently scheduled candidates may occupy this node concurrently. |
| `release-claims` | action | Release the exact whole repository group only for an authorized handoff or abandonment after quiescence is proved. |
| `complete` | terminal | Every selected Feature has a current exact-HEAD pull request that is ready rather than draft, its authoritative Feature contract and current intended base match the immutable contract identity and full base SHA reviewed locally, it has clean independent candidate review and terminal clean G-normalized hosted Codex review for that same HEAD, and it passes required validation and CI with no unresolved blocker, or is proved already incorporated into its integration base; alternatively, an explicitly requested ownership release completed. |
| `deferred` | terminal | A material semantic decision or additional user authority is required. |
| `blocked` | terminal | No safe transition remains because required capability, identity, ownership, evidence, or reconciliation is unavailable. |

Workflow position is transient. None of these node IDs is stored in the
repository registry, task metadata, branch names, or pull requests.

## Transient selected-Feature disposition

| Disposition | Meaning |
| --- | --- |
| `delivery-required` | The selected Feature still requires its own implementation delta and a current exact-HEAD pull request that is ready rather than draft, whose authoritative Feature contract and intended base match the immutable contract identity and full base SHA reviewed locally, that has clean independent candidate review and terminal clean G-normalized hosted Codex review for that same HEAD, and that satisfies required validation and CI. |
| `already-incorporated` | Current exact evidence proves the selected Feature's complete acceptance outcome is already present in its integration base. |

An unmet dependency remains `delivery-required`; it never makes a selected
Feature disappear from completion. If a selected Feature has no exclusive
delta but is not proved already incorporated, defer for user direction rather
than creating an empty pull request or excluding it as ineligible.

## Transient candidate-review dispositions

| `candidate_review_disposition` | Meaning |
| --- | --- |
| `clean` | The independent reviewer found no material issue blocking publication of the exact reviewed Feature contract, base, and candidate HEAD. |
| `findings` | One or more material findings require repair or an evidence-backed rebuttal accepted by a fresh review. |
| `indeterminate` | Exact target, reviewer execution, or evidence was insufficient for a trustworthy verdict. |

These values are transient reviewer results, not workflow nodes or persisted
claim state. Their meanings are canonical here; the operational review contract
only produces and consumes them. Any content, ancestry, base, or full-HEAD
change invalidates them.

## Persisted repository-claim facts

| State | Representation | Meaning |
| --- | --- | --- |
| `provisional` | A claim row whose `orchestrator_task_id` is null. | The immutable repository set is reserved, but task creation has not yet been reconciled and bound. |
| `bound` | A claim row whose `orchestrator_task_id` is present. | One observed orchestrator task owns the complete repository set. |
| unclaimed | No row for the repository. | No Implement orchestrator owns the repository on this host. This is absence, not a stored state. |

Every row in one `claim_token` group has the same `home_project_key` and the
same provisional or bound task value.

## Transient command dispositions

| Disposition | Meaning |
| --- | --- |
| `acquired` | The complete unclaimed repository set was inserted provisionally. |
| `reuse-bound` | The requested repositories already belong to the same bound claim; reuse that orchestrator. |
| `reconcile-provisional` | The requested repositories already belong to the same provisional claim; determine whether task creation happened before retrying. |
| `bound` | The complete provisional claim was attached to the independently observed invoking or separately created orchestrator task. |
| `already-bound` | An idempotent bind observed that the same task already owns the complete claim. |
| `released` | The complete claim group was removed after an authorized bound release or fenced provisional abandonment. |

These dispositions are command results, not persisted states. Errors such as a
foreign claim, mixed ownership, repository-set expansion, binding conflict, or
corrupt registry also are not states.

## Transient diagnostic observations

| Observation | Meaning |
| --- | --- |
| `status=absent` | `doctor` observed no registry file and did not create one. |
| `status=ok` | `doctor` verified the existing registry and its claim count. |
| `database_state=absent` | `inspect` observed no registry file and returned no claims without creating one. |

These observations report the database at command time. They are not persisted
workflow state and do not authorize creation, binding, release, or repair.

## External observations

Task activity, worktree cleanliness, Feature dependencies, branches, commits,
candidate-review results, pull requests, hosted-review results, CI results, and
merge state are observed from their current owners. Candidate review is valid
only for its immutable Feature-contract and candidate snapshots, exact base,
and full HEAD. A draft PR, a generic `not-requested`
hosted-review observation, and absence of comments or review threads are
non-terminal external evidence; completion requires a ready PR plus clean
candidate review bound to the current Feature contract, intended base, and full
HEAD plus a clean hosted review bound to that HEAD. Candidate-review
results, ready-transition receipts, explicit re-review receipts, and hosted
review observations must never be projected into this registry.
