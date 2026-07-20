# Typed Next-Action Controller

This file owns post-registration routing. The root runs only:

```text
scripts/ledger-cache --json controller next --ledger <absolute-ledger> --root-id <root-id> --expected-claim-fingerprint <64hex>
```

The read-only projection is bound to the active root claim, ledger generation,
state fingerprint, task observation, delivery revision, and App-managed
checkout. A released claim or changed binding fails closed. Repeating the
command against unchanged state is byte-for-byte read-only.

The controller never launches a task or model, performs a provider mutation,
selects merge/enqueue/deploy work, or grants Goal/worktree authority. Its
template is selection data, not launch authority.

## Controller 2.0.0 envelope

Every response has exactly `ok`, `command`, `controller_schema_version`,
`tool_version`, `ledger_schema_version`, `ledger`, `portfolio_key`, `root_id`,
`binding`, `decision`, `phase`, `target`, `action`, `action_owner`,
`packet_template`, `allowed_transitions`, `completion_criterion`, `blockers`,
`required_contracts`, and `projection_fingerprint`.

Non-owner actions retain their closed execution template. A GitStack or
AutoReview action has only:

- `schema_version=2.0.0` and `packet_kind=owned-operation`;
- `executor=visible-task`;
- `operation={owner,name,contract_version}`;
- immutable `authority_binding`;
- zero or more generic start, result, or follow-up evidence descriptors; and
- `accepted_result={schema,operation}`.

It contains no provider receipt fields, model-attempt fields, command line,
prompt, body, transport, owner result schema, or ledger event list. Those
registries belong only to the owning tool. `allowed_transitions` for an owned
action consists only of `{outcome,next_phase}` rows from the closed
`owner + operation + outcome` mapper.

## Owned action registry

| Rank | Controller action | Owned operation | Outcomes and next phase |
|---:|---|---|---|
| 2 | `execute-gitstack-mutation-reconciliation` | GitStack `reconcile-mutation` | recovered effect -> original next phase; missing, conflicting, or ambiguous -> owner |
| 3 | `reconcile-autoreview-operation` | AutoReview `reconcile-attempt` | terminal clean -> gates; verification clean -> AutoReview; findings -> review fix; interrupted -> recovery; consumed failure -> owner |
| 4 | `execute-gitstack-terminal-reconciliation` | GitStack `reconcile-terminal` | verified clean -> gates; verified findings -> review fix |
| 5 | `resume-gitstack-wait` | GitStack `wait` | original-deadline clean/findings/pending/failure mapping; never a new waiter |
| 81 | `execute-autoreview-phase` | AutoReview `run-phase` | terminal clean -> gates; verification clean -> AutoReview; findings -> review fix; failure -> owner |
| 90 | `execute-gitstack-request` | GitStack `request` | created or recognized -> wait |
| 92 | `execute-gitstack-wait` | GitStack `wait` | clean -> gates; findings -> review fix; deadline pending -> warning; correlation failure -> reconciliation; provider failure -> owner |
| 93 | `execute-gitstack-warning` | GitStack `warning` | posted or recognized -> gates |
| 94 | `execute-gitstack-reply` | GitStack `reply` | posted or recognized -> resolution |
| 95 | `execute-gitstack-resolve` | GitStack `resolve` | resolved or already resolved -> gates |

Baseline, scheduling, worker-phase, gate, seal, handoff, Goal, verification, and
archive actions keep their existing ownership and ordering. Recovery ranks
before baseline, closeout, delivery operations, and worker phases. Tasks sort
by source id then task key; deliveries sort by delivery key.

## Started and result boundary

Preparation and owner validation are read-only. Immediately before a physical
mutation, waiter, or model launch, the owner calls:

```text
scripts/ledger-cache --json operation start --owner <gitstack|autoreview> --request-file <absolute-json> --ledger <absolute-ledger>
```

The installation-owned bridge reruns the owner validator, requires exact live
controller equality, revalidates claim/CAS/task/revision/checkout authority,
and atomically appends one `owned-operation-started` receipt. A second start
fails with `reconcile-required`; only `operation read-start` may recover the
receipt. Reconciliation never launches or reposts.

After process loss, `operation read-request` returns the opaque original owner
request named by an exact generic start descriptor. Completed follow-ups use
`operation read-result`: it accepts only a current live controller envelope
that names the exact source result fingerprint, then returns the opaque owner
result, owner projection, and immutable source binding. A finding result may
remain bound to its prior revision while the current controller authorizes a
reply on the fixed revision; the bridge never interprets owner fields.

`operation record-result` calls the owner's request-correlated result validator,
requires the exact started receipt and current live binding, and appends one
opaque owner result plus normalized orchestration fields. The same result is
idempotent. A different result for the same start fails closed. GitStack
terminal reconciliation may append a separately started superseding result
only when its owner-validated prior result is already present with identical
lineage; history is never rewritten.

Unknown owners, operations, schemas, outcomes, or outcome mappings fail closed.
Owner results cannot select arbitrary ledger events. Schema 15.0.0 rejects the
retired provider-mutation, review-wait, AutoReview reservation, attempt, and
observation event routes.

The immutable GitStack deadline remains exactly 45 minutes. Deadline-pending
routes only to the one persistent warning operation; only its recorded result
produces `timeout-accepted`. Provider failure never starts a second waiter.
AutoReview keeps one logical phase, primary launch plus at most one invalid-
output repair, and reconciliation after any launch never launches again.
