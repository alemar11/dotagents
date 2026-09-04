# Study State Contract

This reference is the canonical owner of Study's surface, capacity, Grilling,
App controller setup, App title, worker slot, worker execution, archival, and
overall outcome states.

All Study state is transient in the active controller context. Study owns no
persisted checkpoint or ledger. App task identity and lifecycle are external
App observations; CLI subagent identity and lifecycle are external CLI
observations. Requested settings, receipts, and observed settings remain
separate facts.

## Contents

- [Surface and transport](#surface-and-transport)
- [Capacity mode](#capacity-mode)
- [Grilling state](#grilling-state)
- [App controller setup state](#app-controller-setup-state)
- [App title state](#app-title-state)
- [Worker slot state](#worker-slot-state)
- [Worker execution state](#worker-execution-state)
- [App archival state](#app-archival-state)
- [Overall outcome](#overall-outcome)

## Surface and transport

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `study_surface` | `app-task`, `cli-session` | `app-task` continues in a separate visible App controller; `cli-session` keeps the invoking CLI session as controller. |
| `worker_transport` | `app-task`, `subagent`, `none` | Positive App plans use visible tasks, positive CLI plans use native subagents, and zero-worker plans use `none`. |

The shared
[Codex runtime surface contract](../../../references/codex-runtime-surface.md)
determines `study_surface`; it is not user preference or durable configuration.
Once selected, it does not change during the run. Transport failure never
selects another value.

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

## Grilling state

| Value | Meaning | Effect |
| --- | --- | --- |
| `not-started` | The active Study controller has not begun Grilling. | Initial state only. |
| `awaiting-answer` | Grilling has asked one current question and needs the user's answer. | Nonterminal; create no workers. |
| `refined` | The user confirmed the refined handoff. | Continue to worker planning. |
| `user-stopped` | The user ended Grilling before confirmation. | Continue from the best-supported handoff and preserve unconfirmed items. |
| `blocked` | Grilling or its Learn context dependency could not run responsibly. | Create no workers; overall outcome is `failed`. |

Question count, answers, the refined handoff, and unconfirmed items are run
data. A controller waiting for the next answer remains nonterminal even when
its last visible turn contains a question.

## App controller setup state

`app_controller_setup_state` applies only when `study_surface=app-task`.
Use `not-applicable` for every CLI run.

| Value | Meaning | Effect |
| --- | --- | --- |
| `not-started` | No App controller creation attempt has begun. | Initial state; a failed saved-project preflight may terminate from here. |
| `pending-setup` | The creation effect or stable identity remains uncertain. | Reconcile before any retry or worker creation. |
| `ready` | Stable identity, exact project and host, direct local environment, operational state, and Sol/medium profile were independently established. | Begin App Grilling and later worker planning. |
| `creation-failed` | Authoritative evidence proves no controller task exists after the allowed attempt. | Preserve evidence, create no workers, and fail Study. |
| `structural-verification-failed` | A real controller exists, but its project, host, direct local environment, or operational state is missing, mismatched, or unavailable. | Preserve it, create no workers, and fail Study. |
| `settings-drift` | A real controller exists, but observed model or reasoning differs from Sol/medium. | Preserve it, create no workers, and fail Study. |
| `settings-unavailable` | A real controller exists, but independent model or reasoning evidence is unavailable. | Preserve it, create no workers, and fail Study. |
| `unresolved-setup` | Bounded reconciliation cannot determine whether the controller exists. | Create no workers and fail Study without a replacement. |
| `not-applicable` | The current run uses `cli-session`. | Omit App controller setup fields from the CLI report. |

`pending-setup` is nonterminal. Resolve it to another setup value before
reporting an overall outcome. CLI controller profile evidence is informational
only because CLI intentionally inherits the current session profile.

## App title state

`app_title_state` is best-effort metadata for stable App controller and worker
tasks. It is `not-applicable` for CLI controllers and subagents.

| Value | Meaning | Effect |
| --- | --- | --- |
| `title-verified` | Authoritative readback exactly matches the canonical requested title. | Continue. |
| `title-unverified` | Title readback is missing or unavailable after the allowed request and fallback. | Warning unless the user required an exact title. |
| `title-drift` | Authoritative readback differs after the allowed request and fallback. | Warning unless the user required an exact title. |
| `not-applicable` | The run is on CLI, or no stable App task identity exists. | Never infer a title or use it as identity. |

Title state never authorizes task recreation, worker replacement, identity
reconstruction, or repeated renaming.

## Worker slot state

Reserve every planned slot before creation and never renumber, free, or reuse
it. The same state vocabulary applies to visible App worker tasks and CLI
subagents.

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `not-started` | No creation attempt has begun for the reserved slot. | `pending-setup`, `created`, `creation-failed`, `structural-verification-failed`, `settings-drift` |
| `pending-setup` | The creation effect or stable worker identity remains uncertain. | `created`, `creation-failed`, `structural-verification-failed`, `settings-drift`, `unresolved-setup` |
| `created` | A stable worker identity exists and structural verification passed. | Terminal slot state |
| `creation-failed` | Authoritative evidence proves no worker exists, including an unavailable selected transport. | Terminal slot state |
| `structural-verification-failed` | A real worker exists, but required App placement or CLI parent lineage cannot be established. | Terminal slot state |
| `settings-drift` | A real worker exists and observed model or reasoning differs from Luna/max. | Terminal slot state |
| `unresolved-setup` | Bounded reconciliation cannot determine whether a worker exists. | Terminal slot state |

Apply these rules:

- A definitive no-effect failure sets `creation-failed`; later reserved slots
  may proceed, but the failed slot is never retried or replaced.
- An uncertain effect sets `pending-setup`, stops later creation, and permits
  at most three bounded authoritative reconciliation observations.
- A provisional identity does not increment `created_worker_count`.
- A stable App task with only a title warning remains `created`.
- Structural failure or observed profile drift preserves the stable identity,
  stops later creation, and never creates a replacement.
- Failed reconciliation sets `unresolved-setup`; later slots stay
  `not-started` with reason `creation-halted-after-uncertain-slot`.
- Missing worker profile telemetry is recorded as unavailable evidence. It is
  not silently converted into either verified settings or observed drift.

## Worker execution state

Track every stable App task or CLI subagent in exactly one
`worker_execution_state`.

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

## App archival state

Archival applies only to App worker tasks after terminal evidence is captured.
It is never requested for the App controller. All archival fields are
`not-applicable` for CLI runs.

Per-worker `app_archival_request_state` values are:

| Value | Meaning |
| --- | --- |
| `accepted` | The request was accepted; this alone does not prove archived state. |
| `failed` | The request returned a definitive failure. |
| `unavailable` | The App cannot request archival for that worker. |
| `not-applicable` | The worker is a CLI subagent or is not eligible for archival. |

Aggregate fields are:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `worker_archival_requests` | `accepted`, `partial`, `failed`, `unavailable`, `not-applicable` | Aggregate of eligible App worker request receipts; CLI always uses `not-applicable`. |
| `independent_archival_verification` | `confirmed`, `unavailable`, `failed`, `not-applicable` | Independent result for requested App archival; CLI always uses `not-applicable`. |

Omission from a recent-task view is not independent archive proof.

## Overall outcome

| Value | Meaning |
| --- | --- |
| `completed` | The controller returned a usable synthesis and every planned slot completed with terminal evidence. A zero-worker plan may complete through controller analysis alone. |
| `partial` | The controller returned a usable synthesis, but at least one planned slot failed, drifted, remained unresolved, was abandoned, or lacked terminal evidence. App title warnings alone do not make a run partial. |
| `failed` | The controller could not return a usable synthesis. This takes precedence over partial worker results. |

`awaiting-answer`, `pending-setup`, `needs-attention`, and
`monitoring-unavailable` are nonterminal and must not be reported as an overall
outcome. Grilling `blocked` maps to `failed`. Any terminal App controller setup
failure maps to `failed`; a CLI run has no App controller setup gate.
