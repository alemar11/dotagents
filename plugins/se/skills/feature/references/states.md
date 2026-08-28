# Feature Planning States

Feature owns a small transient planning graph. It has no workflow ledger,
checkpoint, task-bootstrap state, title state, review-round machine, or
persisted current node.

## Workflow nodes

| Node | Kind | Meaning |
| --- | --- | --- |
| `intake` | action | Resolve the source route, affected repositories, authority, and exact create or revision scope. |
| `analysis` | action | Gather repository and problem evidence, identify material decisions, and prepare bounded planning inputs. |
| `clarification` | decision | Present one consolidated material question batch and wait nonterminally for answers. |
| `plan` | action | Converge genuine Feature boundaries and draft the complete Plan Set, F-ACs, Macro registries, and dependency graphs. |
| `review` | validation | Review semantic quality and deterministic structural invariants, then revise, clarify, publish, or block. |
| `publish` | action | Freeze a local preview or publish and read back the semantic GitHub projection. |
| `complete` | terminal | The preview is frozen or the semantic hosted projection is verified. |
| `blocked` | terminal | No responsible edge remains because a required decision, source, authority, or write result is unavailable. |

## Transient plan values

| Field | Values | Meaning |
| --- | --- | --- |
| `source_route` | `new-source`, `existing-source` | Selects creation or smallest-patch maintenance through the same graph. |
| `run_mode` | `publish`, `preview` | Selects durable GitHub projection or a local non-durable result. Preview must be explicit. |
| `plan_status` | `draft`, `awaiting-input`, `ready`, `preview`, `published`, `blocked` | Reports the observed Plan Set outcome; it is not a persisted workflow state. |
| `question_status` | `open`, `resolved`, `assumption` | Records whether a material question waits, was answered, or was safely retained as an assumption. |
| `feature_status` | `ready`, `blocked` | Reports whether one Feature contract is usable for an implementation workflow. |
| `macro_status` | `ready`, `blocked` | Reports whether one Macro projection is usable planning context. |
| `source_disposition` | `consolidated`, `separated`, `revised`, `out-of-scope` | Records how one source maps into the final sibling Feature set. |
| `review_result` | `clean`, `revision-required`, `clarification-required`, `blocked` | Selects the Review transition without creating a review-round state machine. |
| `downstream_handoff_status` | `not-requested`, `verified`, `no-op`, `failed`, `unavailable`, `ambiguous` | Records whether an explicitly requested post-publication handoff is reconciled; only not-requested, verified, or no-op permits completion. |

## Publication observations

| Observation | Meaning |
| --- | --- |
| `verified` | The intended hosted identity and semantic projection were read back. |
| `no-op` | The current hosted artifact already matched the intended projection. |
| `failed` | A provider operation definitely failed and its impact is reported. |
| `unavailable` | An optional provider projection was unavailable. |
| `unknown` | An optional native projection could not be observed; the body-backed semantic graph remains authoritative. |
| `ambiguous` | A required issue create/update may have applied but cannot be reconciled; publication blocks without retrying blindly. |
| `not-applicable` | The observation does not apply to this source route or operation. |
| `preview` | The local non-durable projection was frozen without a hosted write. |

Plan Set, Feature, F-AC, Macro, issue, and dependency identities are durable
domain or provider facts, not workflow nodes. The task receipt is retained only
to wait for or resume the same planner; it is not plan correctness evidence.
