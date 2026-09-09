# Explore State Contract

This reference owns Explore's transient capacity, Grilling Session, subagent
slot, subagent execution, and overall outcome states. The invoking task or
session is always the controller; there is no controller-creation lifecycle.

Explore owns no persisted checkpoint or ledger. Subagent identities and
lifecycles are external runtime observations. Requested settings, receipts,
and observed settings remain separate facts.

## Worker transport

`worker_transport` is `none` for a zero-worker plan and `subagent` for every
positive plan. Transport failure never authorizes visible tasks, external
worker processes, or a replacement controller.

## Capacity mode

These counts are run facts rather than workflow states:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `original_requested_count` | `unspecified` or a nonnegative integer | The user's worker request before normalization. |
| `planned_worker_count` | integer from `0` through `5` | The fixed number of reserved slots after applying the cap. |
| `created_worker_count` | integer from `0` through `5` | Reserved slots bound to stable worker identities. |
| `full_capacity_mode` | `yes`, `no` | `yes` exactly when `planned_worker_count=5`. |
| `full_capacity_source` | `exact-request`, `capped-request`, `controller-selected`, `not-applicable` | Why five was planned; use `not-applicable` when full-capacity mode is `no`. |

`exact-request` means the user requested five, `capped-request` means a larger
request was normalized to five, and `controller-selected` means an unspecified
request justified five.

## Grilling Session state

Grilling Session remains `not-started` during the initial direct exploration.
Exploration findings are transient evidence, not a separate workflow state or
a confirmed scope. Once evidence supports informed questions, begin the
interview: `not-started` transitions to `awaiting-answer` or `blocked`. Each
answer may lead to another `awaiting-answer`, `refined`, `user-stopped`, or
`blocked`. No worker planning or creation occurs before `refined` or
`user-stopped`.

| Value | Meaning | Effect |
| --- | --- | --- |
| `not-started` | The active Explore controller has not begun Grilling Session. | Initial state only. |
| `awaiting-answer` | Grilling Session has asked one current question and needs the user's answer. | Nonterminal; create no workers. |
| `refined` | The user confirmed the refined scope. | Continue to worker planning. |
| `user-stopped` | The user ended Grilling Session before confirmation. | Continue from the best-supported scope and preserve unconfirmed items. |
| `blocked` | Grilling Session or its Learn context dependency could not run responsibly. | Create no workers; overall outcome is `failed`. |

Question count, answers, the refined scope, and unconfirmed items are run
data. A controller waiting for the next answer remains nonterminal even when
its last visible turn contains a question.

## Worker slot state

Reserve every planned slot before creation and never renumber, free, or reuse
it. The same state vocabulary applies to native subagents in the current task or session.

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `not-started` | No creation attempt has begun for the reserved slot. | `pending-setup`, `created`, `creation-failed`, `structural-verification-failed`, `settings-drift` |
| `pending-setup` | The creation effect or stable worker identity remains uncertain. | `created`, `creation-failed`, `structural-verification-failed`, `settings-drift`, `unresolved-setup` |
| `created` | A stable worker identity exists and structural verification passed. | Terminal slot state |
| `creation-failed` | Authoritative evidence proves no worker exists, including an unavailable selected transport. | Terminal slot state |
| `structural-verification-failed` | A real subagent exists, but its active controller lineage cannot be established. | Terminal slot state |
| `settings-drift` | A real worker exists and observed model or reasoning differs from the requested [research role](../../../references/subagents/evidence-researcher.md) profile. | Terminal slot state |
| `unresolved-setup` | Bounded reconciliation cannot determine whether a worker exists. | Terminal slot state |

Apply these rules:

- A definitive no-effect failure sets `creation-failed`; later reserved slots
  may proceed, but the failed slot is never retried or replaced.
- An uncertain effect sets `pending-setup`, stops later creation, and permits
  at most three bounded authoritative reconciliation observations.
- A provisional identity does not increment `created_worker_count`.
- A stable subagent with unavailable profile telemetry may remain `created`.
- Structural failure or observed profile drift preserves the stable identity,
  stops later creation, and never creates a replacement.
- Failed reconciliation sets `unresolved-setup`; later slots stay
  `not-started` with reason `creation-halted-after-uncertain-slot`.
- Missing worker profile telemetry is recorded as unavailable evidence. It is
  not silently converted into either verified settings or observed drift.

## Worker execution state

Track every stable subagent in exactly one `worker_execution_state`.

| Value | Meaning | Terminal |
| --- | --- | --- |
| `created-awaiting-turn` | Stable identity exists, but no execution status is yet observable. | No |
| `active` | The worker is running. | No |
| `completed` | The worker finished successfully and its controller can capture the result. | Yes |
| `needs-attention` | Authoritative runtime evidence reports an actionable user request. | No |
| `monitoring-unavailable` | Current state cannot be established through available authoritative observation. | No |
| `failed` | Execution ended with an error. | Yes |
| `abandoned` | Recovery is proven unavailable, or the user explicitly abandons a worker needing attention. | Yes |

Preserve the observed attention reason and never infer `needs-attention` from
prose alone. Preserve the last known state and raw error for
`monitoring-unavailable`; missing telemetry is never completion evidence.
Resume only after authoritative observation recovers. Only the user may direct
abandonment of a worker that requires attention.

## Overall outcome

| Value | Meaning |
| --- | --- |
| `completed` | The controller returned a usable synthesis and every planned slot completed with terminal evidence. A zero-worker plan may complete through controller analysis alone. |
| `partial` | The controller returned a usable synthesis, but at least one planned slot failed, drifted, remained unresolved, was abandoned, or lacked terminal evidence. |
| `failed` | The controller could not return a usable synthesis. This takes precedence over partial worker results. |

`awaiting-answer`, `pending-setup`, `needs-attention`, and
`monitoring-unavailable` are nonterminal and must not be reported as an overall
outcome. Grilling Session `blocked` maps to `failed`.
