# Task Handoff

This is the root-level SE2 contract for assigning work to, observing, and
reporting a task after [Task Preflight](task-preflight.md) has passed. It is
shared by Feature and Implement. It defines the handoff and
relay evidence, while the preflight reference owns the common gates and
authorization decisions.

## Contents

- [Handoff boundary](#handoff-boundary)
- [Canonical title metadata](#canonical-title-metadata)
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
- the source Feature/Task or other durable input references;
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
the established `se:implement` grammar:

```text
<emoji> <outcome specific>
```

Apply these shared rules to the Feature planner task, the Implement
orchestrator, and every Implement worker:

- begin with exactly one contextual emoji, followed by one space;
- keep the outcome short, concrete, and result-oriented;
- derive the emoji and wording deterministically from the active skill role and
  bounded Feature/Task outcome; never choose them randomly;
- use the skill-owned profile template for the role's content, while retaining
  the shared grammar and the existing `🤖` planner/controller and `🛠️` worker
  convention;
- treat the title as display metadata only. It is never task identity,
  authorization, state, claim, branch, or recovery evidence.

Request the canonical title during task creation when the live capability is
available, then independently read it back. If initialization is unavailable
or the observed title is missing or different, use a separately authorized
title adjustment at most once for that stable task and read it back again when
possible. Record `title-unverified` or `title-drift` as best-effort warning
evidence. Never create a duplicate task, retry creation, or recover an
ambiguous effect from a title match.

## Observation record

After creation or resume, append an authoritative observation with these
minimum fields:

```yaml
task_observation:
  task_profile_ref: "<skill-owned profile>"
  role: "<profile role>"
  requested_title: "<canonical display title>"
  observed_title: "<read-back display title or null>"
  title_status: verified
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

## Final handoff result

The final relay must preserve the exact task identity and include:

- the final independently observed task, project, host, repository, and state;
- the Feature/Task outcome and validation evidence;
- any repository or documentation changes actually made by the task;
- the preflight authorization record by reference;
- reconciliation evidence for every interrupted or retried operation;
- an explicit `outcome` of `complete` or `blocked`.

Task creation and monitoring evidence never grants GitHub mutation authority.
Any GitHub issue change must still satisfy the invoking skill's explicit
publication boundary and its own read-after-write verification contract.
