# GitHub Review Threads State Contract

This reference is the canonical owner of feedback, request-binding, review,
recovery, operation-result, reconciliation, and resolution states. Review
observations and feedback dispositions are transient. G reservation markers
and the operation journal are persisted per-user recovery state; typed receipt
and result files are caller-persisted artifacts. Pull-request HEAD, comments,
reviews, threads, reactions, and resolution are external GitHub state.

## Contents

- [Feedback disposition](#feedback-disposition)
- [Request binding](#request-binding)
- [Automated review state](#automated-review-state)
- [Recovery disposition](#recovery-disposition)
- [Owned operation result](#owned-operation-result)
- [Mutation reconciliation evidence](#mutation-reconciliation-evidence)
- [Direct request status](#direct-request-status)
- [Direct warning-comment status](#direct-warning-comment-status)
- [Direct reply status](#direct-reply-status)
- [Direct edit-comment status](#direct-edit-comment-status)
- [Direct submit-review status](#direct-submit-review-status)
- [Resolution status](#resolution-status)

## Feedback disposition

| Value | Meaning |
| --- | --- |
| `actionable` | A current-head change or evidence response is required and belongs to the selected scope. |
| `already-addressed` | Current code and proof already satisfy the feedback. |
| `informational` | The comment requires no code or provider-state change. |
| `obsolete` | The comment no longer applies to the current head or current contract. |
| `needs-user-decision` | Competing valid outcomes require caller-owned product or scope direction. |

## Request binding

| Value | Meaning |
| --- | --- |
| `absent` | No request lineage is expected or observed. |
| `recognized` | The exact typed request receipt and provider artifact correlate. |
| `unbound` | Provider text exists without the required typed identity binding. |
| `invalid` | A typed marker or receipt is malformed or contradicts the target. |
| `unknown` | The provider evidence cannot establish a binding safely. |
| `ambiguous` | Multiple plausible or conflicting request artifacts prevent unique correlation. |

## Automated review state

| Value | Meaning | Terminal | Exit |
| --- | --- | --- | --- |
| `not-requested` | No qualifying review request or ready-transition lineage is established. | No | `2` |
| `acknowledged` | The provider acknowledged the exact request but has no terminal result. | No | `2` |
| `pending` | The exact review is still in progress. | No | `2` |
| `clean` | Terminal evidence proves no findings for the exact head and lineage. | Yes | `0` |
| `findings` | Terminal evidence reports findings for the exact head and lineage. | Yes | `1` |
| `stale` | The PR head drifted or provider terminal evidence names a different head. | Yes | `3` |
| `ambiguous` | Conflicting terminal outcomes or overlapping evidence prevent safe selection. | Yes | `4` |
| `error` | Provider-authored terminal failure evidence exists for the requested head. | Yes | `4` |

An API, authentication, configuration, or correlation error uses the normal G
error envelope rather than inventing another review state. Exit `64` is invalid
arguments and exit `124` is a bounded-wait timeout; the last review state stays
in the JSON envelope.

## Recovery disposition

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `recovery` | `needs-owner` | Exact read-only reconciliation could not prove one unique prior provider artifact; never retry the mutation automatically. |

## Owned operation result

Every `g-review-operation-result:v1` uses one closed `status` plus one outcome
allowed for its operation.

| Status | Meaning |
| --- | --- |
| `completed` | The operation reached an admitted terminal result. |
| `failed` | A definite terminal failure prevents admission. |
| `ambiguous` | Conflicting or unreadable evidence prevents a unique result. |
| `blocked` | Required evidence is missing and owner action is required. |

| Operation | Allowed outcomes |
| --- | --- |
| `request` | `created`, `recognized-existing` |
| `wait` | `clean`, `findings`, `pending-at-deadline`, `request-correlation-failure`, `provider-failure` |
| `ready-check` | `clean`, `findings`, `pending`, `stale`, `ambiguous`, `provider-failure` |
| `ready-wait` | `clean`, `findings`, `pending-at-deadline`, `stale`, `ambiguous`, `provider-failure` |
| `warning` | `posted`, `recognized-existing` |
| `reply` | `posted`, `recognized-existing` |
| `resolve` | `resolved`, `already-resolved` |
| `reconcile-mutation` | `completed-from-readback`, `missing`, `conflicting`, `ambiguous` |
| `reconcile-terminal` | `clean-verified`, `findings-verified` |

The shipped validator owns the exact legal status/outcome pair and must admit
every result before caller state changes. In particular,
`pending-at-deadline` is `completed`, request/provider failures are `failed`,
mutation `missing` is `blocked`, mutation `conflicting`/`ambiguous` are
`ambiguous`, and both terminal reconciliation outcomes are `completed`.

## Mutation reconciliation evidence

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `marker_state` | `absent`, `exact`, `conflicting` | Whether the one-use journal marker is missing, uniquely matches, or conflicts. |
| `provider_artifact_state` | `missing`, `unique`, `conflicting`, `ambiguous`, `unreadable` | Result of the one bounded exact provider readback. |

Legal reconciliation outcomes are:

| Outcome | Evidence pair |
| --- | --- |
| `completed-from-readback` | `exact` marker plus `unique` provider artifact |
| `missing` | `absent` or `exact` marker plus `missing` provider artifact |
| `conflicting` | `conflicting` marker plus `missing` artifact, or `exact` marker plus `conflicting` artifact |
| `ambiguous` | `exact` marker plus `ambiguous` or `unreadable` artifact |

A marker alone never proves provider success. Only `unique` provider evidence
may carry a recovered typed result.

## Direct request status

The direct `reviews request` command uses these result statuses:

| Value | Meaning |
| --- | --- |
| `dry-run` | Exact request, target, and reservation proof succeeded without a provider mutation. |
| `reused` | One existing exact request owned by the authenticated actor was proven and reused without mutation. |
| `posted` | The authorized request was posted and the provider response plus exact readback proved it. |
| `recovered` | A consumed or ambiguous prior request attempt was proven successful by exact readback without retry. |

Only `reused`, `posted`, and `recovered` carry a complete persistable request
receipt. These direct statuses project to the managed `request` outcomes
`recognized-existing` or `created`; they are not those outcomes themselves.

## Direct warning-comment status

The direct timeout-warning `reviews comment` command uses these statuses:

| Value | Meaning |
| --- | --- |
| `dry-run` | Exact input, target, and reservation proof succeeded without a provider mutation. |
| `posted` | The authorized warning comment was posted and exact readback proved it. |
| `recovered` | A consumed or ambiguous prior warning attempt was proven successful by exact readback without retry. |

These direct statuses project to the managed `warning` outcomes `posted` or
`recognized-existing`.

## Direct reply status

The direct `reviews reply` command uses these statuses. Only `replied` and
`recovered` appear in a persisted `g-review-thread-reply:v1` receipt.

| Value | Meaning | Receipt emitted |
| --- | --- | --- |
| `dry-run` | Exact input and target proof succeeded without a provider mutation. | No |
| `replied` | The authorized reply mutation completed and exact readback proved the new reply. | Yes |
| `recovered` | A consumed prior reply attempt was proven successful by exact readback without retry. | Yes |

These direct-command statuses are distinct from the managed operation's
canonical `reply` outcomes `posted` and `recognized-existing`.

## Direct edit-comment status

The direct `reviews edit-comment` command uses these statuses:

| Value | Meaning |
| --- | --- |
| `dry-run` | Exact target and replacement-text proof succeeded without a provider mutation. |
| `reused` | The existing comment already had the exact requested body; no mutation was needed. |
| `edited` | The authorized edit was applied and exact readback proved the result. |
| `recovered` | An ambiguous edit response was proven successful by one exact readback without retry. |

## Direct submit-review status

The direct `reviews submit-review` command uses these statuses:

| Value | Meaning |
| --- | --- |
| `dry-run` | Exact target, event, and body proof succeeded without a provider mutation. |
| `submitted` | The authorized review was submitted and exact readback proved its event, head, actor, and body. |
| `recovered` | An ambiguous submission response was proven successful by one exact readback without retry. |

## Resolution status

| Value | Meaning |
| --- | --- |
| `dry-run` | Dry-run proof succeeded; no mutation was attempted. |
| `resolved` | The mutation was attempted and exact readback proves resolution. |
| `recovered` | A consumed prior attempt was proven successful by exact readback without retry. |
| `already-resolved` | The thread was already resolved and the full exact-target proof succeeded; no authorship claim is made. |

`resolved` sets `mutation_attempted=true` and
`mutation_may_have_applied=false`. `recovered` also sets
`mutation_attempted=true`; it sets `mutation_may_have_applied=false` when the
current invocation's ambiguous write is proven by exact readback, and `true`
when a previously consumed reservation is reconciled without retry because the
prior attempt may have applied. `dry-run` and `already-resolved` set both flags
to false. An uncertain post-attempt failure reports
`mutation_may_have_applied=true` in error details and forbids retry.
