# Study State Contract

This reference is the canonical owner of Study's capacity, setup, title,
settings, task, archival, and overall outcome states. The parent and
orchestrator keep these labels transiently in task context; Study does not
persist a ledger. Real App task identity, project, host, environment, model,
reasoning, turn status, and archival state are external observations.

## Contents

- [Capacity mode](#capacity-mode)
- [Grilling state](#grilling-state)
- [Orchestrator setup state](#orchestrator-setup-state)
- [Title state](#title-state)
- [Worker slot state](#worker-slot-state)
- [Task workflow state](#task-workflow-state)
- [Archival state](#archival-state)
- [Overall outcome](#overall-outcome)

## Capacity mode

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `full_capacity_mode` | `yes`, `no` | `yes` exactly when `planned_worker_count=5`; otherwise `no`. |
| `full_capacity_source` | `exact-request`, `capped-request`, `orchestrator-selected`, `not-applicable` | Records why full capacity was selected; use `not-applicable` when `full_capacity_mode=no`. |

The source is `exact-request` for an explicit five-worker request,
`capped-request` when a larger request is normalized to five, and
`orchestrator-selected` when an unspecified request justifies five workers.

## Grilling state

The visible orchestrator completes this mandatory phase before worker planning.

| Value | Meaning | Effect |
| --- | --- | --- |
| `not-started` | The orchestrator has not begun Grilling. | Initial state only. |
| `awaiting-answer` | Grilling asked exactly one current question and needs the owning user's answer. | Nonterminal; create no workers. |
| `refined` | The user confirmed the refined handoff. | Continue to scope analysis and worker planning. |
| `user-stopped` | The user ended Grilling before confirmation. | Continue from the best-supported handoff and preserve unconfirmed items. |
| `blocked` | Grilling or its Learn context dependency could not run responsibly. | Create no workers and report overall outcome `failed`. |

Question count, answers, the refined handoff, and unconfirmed items are run data
rather than state fields. A task waiting for the next interview answer remains
nonterminal even when its last visible response contains a question.

## Orchestrator setup state

Track the orchestrator separately because it has no worker slot.

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `not-started` | No orchestrator creation attempt has begun. | `pending-setup`, `ready`, `creation-failed`, `structural-verification-failed`, `settings-drift`, `settings-unavailable` |
| `pending-setup` | The response is provisional or server-side creation remains uncertain. | `ready`, `creation-failed`, `structural-verification-failed`, `settings-drift`, `settings-unavailable`, `unresolved-setup` |
| `ready` | A stable orchestrator identity, exact project and host, local execution environment, observable operational state, and requested Sol/medium profile were independently verified. | Terminal setup state; begin worker planning. |
| `creation-failed` | Authoritative reconciliation proves that no orchestrator task exists after the allowed attempt. | Terminal setup state; overall outcome is `failed`. |
| `structural-verification-failed` | A real orchestrator exists, but its project, host, local execution environment, or operational state is missing, mismatched, or unavailable. | Terminal setup state; preserve it, create no workers, and report overall outcome `failed`. |
| `settings-drift` | A real orchestrator exists but its observed model or reasoning differs from the required profile. | Terminal setup state; preserve it, create no workers, and report overall outcome `failed`. |
| `settings-unavailable` | A stable real orchestrator and exact project exist, but independent model or reasoning telemetry is unavailable. | Terminal setup state; preserve it, create no workers, and report overall outcome `failed`. |
| `unresolved-setup` | Bounded reconciliation cannot determine whether an orchestrator task exists. | Terminal setup state; create no workers and report overall outcome `failed`. |

`pending-setup` is nonterminal and cannot be converted directly into an overall
outcome. Continue bounded reconciliation until it reaches another setup state;
never create a replacement from the pending state.

## Title state

Title state is best-effort telemetry and never task identity.

| Value | Meaning | Effect |
| --- | --- | --- |
| `title-verified` | Authoritative readback exactly matches the requested canonical title. | Continue. |
| `title-unverified` | Title readback is missing or unavailable after the one allowed initialization/fallback attempt. | Warning only unless the user explicitly required an exact title. |
| `title-drift` | Authoritative readback differs from the requested canonical title after the one allowed initialization/fallback attempt. | Warning only unless the user explicitly required an exact title. |
| `not-applicable` | No stable task identity existed for title verification. | Report with the setup failure; never use it for a real task. |

Never retry creation, replace a real task, or reconstruct identity from title
state.

## Worker slot state

Reserve each planned slot before creation and never renumber, free, or reuse it
during the run.

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `not-started` | No creation attempt has begun for the reserved slot. | `pending-setup`, `created`, `creation-failed`, `structural-verification-failed`, `settings-drift` |
| `pending-setup` | The response is provisional or server-side creation remains uncertain. | `created`, `creation-failed`, `structural-verification-failed`, `settings-drift`, `unresolved-setup` |
| `created` | A stable real task identity exists and structural verification passed. | Terminal slot state |
| `creation-failed` | Authoritative evidence proves that no task exists after the attempt. | Terminal slot state |
| `structural-verification-failed` | A real worker exists, but its project, host, local execution environment, or operational state is missing, mismatched, or unavailable. | Terminal slot state |
| `settings-drift` | A real task exists but observed model or reasoning differs from the required profile. | Terminal slot state |
| `unresolved-setup` | Bounded reconciliation cannot determine whether a task exists. | Terminal slot state |

Apply these transition rules:

- A definitive creation error proving no task exists sets `creation-failed`.
  Continue with later planned slots but never retry that slot.
- A timeout, transport error, or response with neither a stable identity nor
  certain server state sets `pending-setup` and stops later creation.
- A provisional identity does not count as a created worker. Use up to three
  bounded authoritative snapshots and correlate only through explicit identity
  evidence, never title, prompt preview, or timing.
- A verified real task with `title-unverified` or `title-drift` keeps slot state
  `created`; a title warning alone never authorizes retry or replacement.
- A real task whose project, host, local execution environment, or operational
  state cannot be verified sets `structural-verification-failed`. Preserve its
  identity, create no replacement, and stop later creation.
- Observed profile mismatch sets `settings-drift`. Preserve the task identity,
  create no replacement, and make the run partial unless the orchestrator
  itself failed profile verification before any worker was created.
- Failed reconciliation sets `unresolved-setup`; keep every later slot
  `not-started` with reason `creation-halted-after-uncertain-slot` and create no
  replacement.

## Task workflow state

Track every real task in exactly one workflow state.

| Value | Meaning | Terminal |
| --- | --- | --- |
| `created-awaiting-turn` | A real identity exists but no turn status is observable. | No |
| `active` | The latest turn is in progress. | No |
| `completed` | The latest turn completed without error and the task is idle. | Yes |
| `needs-attention` | Structured task telemetry reports an explicit actionable request. | No |
| `monitoring-unavailable` | Neither waiting nor authoritative reads can establish current state. | No |
| `failed` | The latest turn ended with an error. | Yes |
| `abandoned` | Recovery is proven unavailable, or the owning user explicitly abandons a task needing attention. | Yes |

Preserve the observed attention reason and never infer `needs-attention` from
prose alone. Preserve the last known state and raw errors for
`monitoring-unavailable`, notify the parent, and pause. Maintain separate
progress and inspection positions according to the live capability that
produced each one; never interchange them. An incoming parent message may
interrupt a wait without invalidating the last confirmed progress position.
Deduplicate by stable revision or event identity, not prose. Missing telemetry
is never success evidence.

Resume only after authoritative observation recovers. If recovery is proven
impossible, only the owning user may explicitly direct abandonment.

## Archival state

Archival is separate from slot and task state. Request it only for workers in
`completed`, `failed`, or explicitly `abandoned` after terminal evidence is
captured. Structured final state, reason, error, and last telemetry substitute
for a missing memo from a failed or abandoned worker.

Per-worker archival request results are:

| Value | Meaning |
| --- | --- |
| `accepted` | The archival request was accepted; this is not independent proof of archived state. |
| `failed` | The archival request returned a definitive failure. |
| `unavailable` | The runtime cannot request archival for that worker. |

The final report derives these aggregate fields without replacing the
per-worker receipts:

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `worker_archival_requests` | `accepted`, `partial`, `failed`, `unavailable`, `not-applicable` | `accepted` means every eligible worker request was accepted; `partial` means per-worker results are mixed or an eligible worker lacks a result; `failed` means every eligible worker request definitively failed; `unavailable` means eligible workers existed but no request could be attempted; `not-applicable` means the run created no workers eligible for archival. |
| `independent_archival_verification` | `confirmed`, `unavailable`, `failed`, `not-applicable` | `confirmed` means authoritative observation verified every requested archival; `unavailable` means at least one archival request existed but independent state could not be observed; `failed` means authoritative observation disproved at least one requested archival; `not-applicable` means no worker archival request was applicable. |

Record bounded post-request verification separately when authoritative archive
state is observable. Omission from a recent-task view is not proof. Keep the
orchestrator unarchived.

## Overall outcome

| Value | Meaning |
| --- | --- |
| `completed` | Every planned slot produced a completed worker and every final memo was captured. Report archival state separately. |
| `partial` | The orchestrator returned a usable synthesis, but a planned slot is failed, abandoned, structural-verification-failed, settings-drift, unresolved, or missing, or terminal evidence could not be captured. Title warnings alone do not make a run partial. |
| `failed` | The orchestrator could not return a usable synthesis. This takes precedence over `partial` even when some worker results exist. |

`needs-attention` and `monitoring-unavailable` are interim task states and must
never be presented as the authoritative overall outcome. Orchestrator
`creation-failed`, `structural-verification-failed`, `settings-drift`,
`settings-unavailable`, and `unresolved-setup` map to `failed`; orchestrator
`pending-setup` must be reconciled before any overall outcome is reported. If
required preflight fails before creation begins, setup remains `not-started`
and the terminal overall outcome is `failed`; otherwise `not-started` is only
the initial nonterminal setup state.

Grilling `not-started` and `awaiting-answer` are also nonterminal and cannot
produce an overall Study outcome. Grilling `blocked` maps to `failed` before
worker creation; `refined` and `user-stopped` allow Study to continue.
