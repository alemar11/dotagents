# Task Handoff

This is the root-level SE2 contract for assigning work to, observing, and
reporting a task after [Task Preflight](task-preflight.md) has passed. It is
shared by Feature and Implement. It defines the handoff and
relay evidence, while the preflight reference owns the common gates and
authorization decisions.

## Contents

- [Handoff boundary](#handoff-boundary)
- [Canonical title metadata](#canonical-title-metadata)
- [Title reconciliation](#title-reconciliation)
- [Observation record](#observation-record)
- [Update relay](#update-relay)
- [Failure and recovery evidence](#failure-and-recovery-evidence)
- [Final handoff result](#final-handoff-result)

## Handoff boundary

Create one handoff for one logical task assignment. It must point to the
validated preflight record and carry the invoking skill's own task profile and
topology. Do not invent a common profile or topology here.

The handoff must contain, or link to:

- the explicit user request and bounded objective;
- the source Feature Plan, source issue, or other durable input references;
- the exact repository destination and allowed scope;
- a reference to the skill-owned task profile and the role assigned to this
  handoff;
- expected partial-update and final-report behavior;
- validation and terminal-readiness expectations;
- the preflight record, including its separate authorization decisions.

Do not copy a task identity into the handoff from conversation text or a
display title. The application supplies the identity, and the invoking session
records it only after independent observation.

## Canonical title metadata

Every task created by SE2 receives a deterministic display-title request using
the established SE2 Implement grammar:

```text
<emoji> <role or workflow> · <scope or outcome>
```

Apply these shared rules to the Feature planner task, the Implement
orchestrator, and every Implement Feature Worker:

- begin with exactly one contextual emoji, followed by one space;
- keep the role, scope, or outcome short, concrete, and deterministic;
- derive the emoji and wording deterministically from the active skill role and
  either an immutable selected scope or a bounded Feature outcome; never
  choose them randomly;
- use the skill-owned profile template for the role's content, while retaining
  the shared grammar and the existing `📚` planner, `🤖` orchestrator, and
  `🛠️` Feature Worker convention;
- for an Implement orchestrator, use `1 Feature` for one selected Feature and
  `<feature_count> Features` for multiple selected Features. Freeze that count
  from the authoritative run scope; do not derive it from worker count,
  completion progress, or serial versus parallel execution;
- treat the title as display metadata only. It is never task identity,
  authorization, state, claim, branch, or recovery evidence.

Request the canonical title during task creation when the live capability is
available, then independently read it back after the stable task identity is
known. Creation acceptance is never title verification. Resolve the title
reconciliation below before normal monitoring or update relay begins.

## Title reconciliation

For every titled SE2 task, complete this bounded subprotocol:

1. preserve the stable task identity from authoritative observation;
2. compare the first independently observed title with the exact requested
   title;
3. when they match, record `verified` without another title effect;
4. when the title is missing or different and adjustment is available and
   authorized, first retain evidence that no prior adjustment was attempted,
   reserve the effect durably when the invoking workflow has durable recovery,
   and then adjust that same stable task to the requested title exactly once;
5. independently read the title back after the adjustment;
6. record `verified`, `title-unverified`, or `title-drift` before entering
   normal monitoring or relaying updates.

An unavailable capability, rejected adjustment, ambiguous effect, failed
readback, or lost attempt record never authorizes another task or a second
title adjustment. Reconcile an ambiguous adjustment by authoritative readback
and retain the original task identity. Title failure is warning evidence
rather than a task-topology blocker, but it must never be skipped or silently
reported as success.

Keep one reconciliation record per stable task. Retain it in session state for
a non-durable workflow. When the invoking workflow already owns durable
side-effect recovery, reserve the adjustment there before applying it and bind
the reservation to the stable task identity alone. Retain the exact requested
title as effect evidence, never as identity or as part of the idempotency key.
Do not add persistence solely for title metadata.

```yaml
title_reconciliation:
  requested_title: "<canonical display title>"
  initial_observed_title: null
  adjustment_authorization: granted-for-declared-title
  adjustment_capability: available
  prior_attempt_evidence: no-prior-attempt
  recovery_record: transient
  adjustment_attempted: true
  final_observed_title: "<canonical display title or null>"
  title_status: verified
  evidence_refs:
    - "<initial and final authoritative observations>"
```

On resume, reuse the retained reconciliation record or the invoking workflow's
durable effect reservation, then independently read the current title. A
pending, unknown, applied, or otherwise attempted adjustment is never begun
again. If retained evidence cannot prove that no prior attempt occurred, do
not adjust: preserve the task and finalize `verified` when authoritative
readback already matches, otherwise record `title-unverified` or `title-drift`.

## Observation record

After creation or resume, append an authoritative observation with these
minimum fields:

```yaml
task_observation:
  task_profile_ref: "<skill-owned profile>"
  role: "<profile role>"
  requested_title: "<canonical display title>"
  observed_title: "<final read-back display title or null>"
  title_status: verified
  title_reconciliation_ref: "<bounded reconciliation evidence>"
  task_identity: "<exact observed task identity>"
  repository_identity: "<exact observed repository>"
  project_identity: "<exact observed project>"
  project_root: "<exact observed repository-compatible path>"
  host_identity: "<exact observed host>"
  state: "<observed operational state>"
  independently_observed: true
```

The observation must be compared with the preflight target. A mismatch in task
identity, project, host, repository, or state is a blocker until reconciled.
The task identity is stable evidence; titles and other display metadata are
not.

## Update relay

Do not begin normal monitoring or relay a partial update until title
reconciliation has produced either `verified`, `title-unverified`, or
`title-drift`. The warning outcomes do not suspend otherwise valid work.

Relay updates without changing their meaning or presenting a partial update as
final. Each relayed update must identify the observed task and distinguish its
kind:

```yaml
update:
  task_identity: "<observed task identity>"
  kind: partial
  state: "<observed state>"
  content_ref: "<update evidence>"
  relayed: true
```

Use `kind: final` only when the task is independently observed in its terminal
state and the final report contains the evidence required by the invoking
skill. A missing, stale, or unverified final update leaves the handoff
`blocked`; it is not a successful completion.

## Failure and recovery evidence

When a create, resume, or monitoring operation times out or errors, retain the
original handoff and add reconciliation evidence before taking another action:

```yaml
reconciliation:
  attempted: true
  prior_effect: not-applied
  retry_decision: allowed
  evidence_refs:
    - "<authoritative observation>"
```

The allowed `prior_effect` values are `applied`, `not-applied`, and `unknown`.
The allowed `retry_decision` values are `allowed`, `forbidden`, and `blocked`.
An `unknown` effect can never justify a retry. If the application or monitor
cannot provide reconciliation, report `retry_decision: blocked` and stop.

Apply the same read-before-retry rule to an ambiguous title adjustment, but do
not retry that adjustment. Preserve the task and finalize its title status from
the authoritative evidence that remains available.

## Final handoff result

The final relay must preserve the exact task identity and include:

- the final independently observed task, project, host, repository, and state;
- the final title-reconciliation status and any display-metadata warning;
- the Feature Plan outcome and validation evidence;
- any repository or documentation changes actually made by the task;
- the preflight authorization record by reference;
- reconciliation evidence for every interrupted or retried operation;
- an explicit `outcome` of `complete` or `blocked`.

Task creation and monitoring evidence does not broaden GitHub mutation scope.
Any GitHub issue change must still be within the invoking skill's explicit
request and satisfy its own read-after-write verification contract; no second
user confirmation is required for that in-scope write.
