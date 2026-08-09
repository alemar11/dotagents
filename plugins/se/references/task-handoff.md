# Task Handoff

This is the root-level SE contract for assigning work to, observing, and
reporting a task after [Task Preflight](task-preflight.md) has passed. It is
shared by Feature and Implement. It defines the handoff and
relay evidence, while the preflight reference owns the common gates and
authorization decisions.

## Contents

- [Handoff boundary](#handoff-boundary)
- [Canonical title metadata](#canonical-title-metadata)
- [Title reconciliation](#title-reconciliation)
- [Role-profile request](#role-profile-request)
- [Role-profile observation](#role-profile-observation)
- [Project identity reconciliation](#project-identity-reconciliation)
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
- the exact requested project identity selected from the preflight's live
  inventory, plus its repository-compatibility evidence;
- a reference to the skill-owned task profile and the role assigned to this
  handoff;
- the exact requested model and reasoning resolved for this assignment;
- evidence that the complete resolved profile will be actively requested and
  ambient inheritance is forbidden;
- expected partial-update and final-report behavior;
- validation and terminal-readiness expectations;
- the preflight record, including its separate authorization decisions.

Do not copy a task identity into the handoff from conversation text or a
display title. The application supplies the identity, and the invoking session
records it only after independent observation.

## Canonical title metadata

Every task created by SE receives a deterministic display-title request using
the established SE Implement grammar:

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

For every titled SE task, complete this bounded subprotocol:

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

## Role-profile request

Treat the skill-owned model and reasoning as required task-effect inputs, not
preferences or defaults. The explicit Feature or Implement invocation selects
the profile declared for every required role and for any optional role
instantiated as its own application task. Before creation or resume, actively
request both resolved values and freeze semantic request evidence in the
handoff. Never omit either value to inherit the invoking session, application,
project, host, or provider default.

Use this interface-independent record shape for the request evidence:

```yaml
profile_request:
  requested_model: "<assignment-resolved model>"
  requested_reasoning: "<assignment-resolved reasoning>"
  request_mode: explicit
  ambient_inheritance: forbidden
```

These are handoff evidence fields, not application-operation parameter names.
If the live runtime cannot actively request both resolved values, stop before
the task effect. A task created through ambient inheritance is not a valid
profile request even when its later effective readback happens to match.
Authoritative post-effect observation remains independently mandatory.

## Role-profile observation

Every application task created or resumed under a skill-owned profile must
carry a typed role observation. Resolve the exact requested model and reasoning
before the task effect. When a profile selects reasoning per assignment, such
as one Implement Feature Worker per Feature, freeze that resolved value in the
handoff before startup. Bind the observation to the handoff's explicit
`profile_request`; effective-profile readback never substitutes for that
pre-effect request evidence.

After stable task identity is independently observed, read the effective model
and reasoning from the authoritative runtime view. A request payload, creation
receipt, configured default, conversation text, cached record, or inferred
value is not authoritative readback. Bind the observation to the same exact
task by nesting it in the task observation below. If an unexpected post-effect
readback omits either value, retain that field as `null` with the authoritative
evidence reference before blocking; never fabricate or silently omit it.

For a required role, both effective values must be present and exactly match
the resolved requested values before normal monitoring or update relay. A
missing, unobservable, or mismatched value is `blocked` with `blocker:
unsupported-runtime`. Preserve the observed task identity and reconcile the
original effect; never create a replacement task merely to seek a matching
profile. For an optional role instantiated as its own application task, apply
the invoking skill's declared fallback and do not claim delegated work unless
the task and its effective profile were both observed.

The role observation is evidence, not a new state machine. Do not add an
`accepted` or routing-status field: the invoking workflow retains its existing
`ready`, fallback, `complete`, and `blocked` outcomes. Do not add generic
sandbox or permission fields here. Repository, project, host, checkout, and
worktree boundaries remain with their existing owners; a skill that requires
another execution-boundary fact must define its semantic requirement itself.

## Project identity reconciliation

After the stable task identity is independently observed, read the effective
project identity from the authoritative application view and compare it with
the exact project identity frozen by preflight. Project selection evidence and
task-project observation are distinct: a request payload, creation receipt,
working directory, checkout or worktree path, display title, or conversation
text cannot prove the effective binding.

Apply this bounded decision sequence to the same stable task:

1. an exact observed match permits the handoff to continue;
2. a present but different identity is a destination mismatch and blocks
   normal monitoring or update relay;
3. a missing or unobservable identity permits exactly one bounded second
   authoritative readback of that same task plus one refresh of the live
   project inventory;
4. if the second readback matches, continue and retain both observations;
5. if the expected project is absent or no longer repository-compatible in the
   refreshed inventory, remain `blocked` and tell the user to add or configure
   the exact repository as a saved project in the ChatGPT/Codex application;
6. if the expected project remains present and compatible but the effective
   identity is still missing, remain `blocked` with
   `blocker: unsupported-runtime` because the runtime cannot prove the binding;
7. if the second readback exposes a different identity, remain blocked on the
   destination mismatch.

The bounded second readback is observation, not task creation recovery. Never
create a replacement task, repeat the create effect, switch projects, or
continue projectless to obtain different evidence. Preserve the same task
identity and report the smallest actionable recovery input.

```yaml
project_reconciliation:
  task_identity: "<stable observed task identity>"
  requested_project_identity: "<inventory-backed preflight project>"
  initial_observed_project_identity: null
  bounded_reread_attempted: true
  final_observed_project_identity: null
  refreshed_inventory_contains_requested: true
  project_inventory_evidence_ref: "<refreshed live inventory observation>"
  task_observation_evidence_refs:
    - "<initial authoritative task observation>"
    - "<bounded authoritative task re-read>"
  independently_observed: true
```

## Observation record

After creation or resume, append an authoritative observation with these
minimum fields:

```yaml
task_observation:
  task_profile_ref: "<skill-owned profile>"
  role: "<profile role>"
  assignment_ref: "<planner, orchestration, Feature, or other stable scope>"
  profile_request_ref: "<explicit profile-request evidence>"
  role_observation:
    requested_model: "<assignment-resolved model>"
    requested_reasoning: "<assignment-resolved reasoning>"
    observed_model: "<authoritative effective model or null>"
    observed_reasoning: "<authoritative effective reasoning or null>"
    evidence_ref: "<authoritative runtime readback>"
    independently_observed: true
  requested_title: "<canonical display title>"
  observed_title: "<final read-back display title or null>"
  title_status: verified
  title_reconciliation_ref: "<bounded reconciliation evidence>"
  task_identity: "<exact observed task identity>"
  repository_identity: "<exact observed repository>"
  requested_project_identity: "<inventory-backed preflight project>"
  project_identity: "<exact effective project readback or null>"
  project_identity_evidence_ref: "<authoritative task readback>"
  project_reconciliation_ref: "<bounded same-task evidence>"
  project_root: "<exact observed repository-compatible path>"
  host_identity: "<exact observed host>"
  state: "<observed operational state>"
  independently_observed: true
```

The observation must be compared with the preflight target and the resolved
skill-owned profile, and its `profile_request_ref` must prove the complete
resolved profile was actively requested. A missing explicit request, ambient
inheritance, or a mismatch in effective model, effective reasoning, task
identity, project, host, repository, or state is a blocker until reconciled.
The task identity and authoritative role readback are execution evidence;
titles and other display metadata are not.

A null project readback is not an exact match. Complete the project identity
subprotocol above before selecting its setup-remediation or
`unsupported-runtime` blocker. Do not infer the result from another field.

## Update relay

Do not begin normal monitoring or relay a partial update until the effective
project identity exactly matches the preflight target, the required role
observation matches, and title reconciliation has produced either `verified`,
`title-unverified`, or `title-drift`. The title warning outcomes do not suspend
otherwise valid work.

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

The one bounded project re-read defined above never authorizes another create
or resume effect. Preserve the original task even when the project remains
unobservable, and report the resulting setup or runtime blocker.

## Final handoff result

The final relay must preserve the exact task identity and include:

- the final independently observed task, project, host, repository, and state;
- the requested-versus-observed project identity, refreshed-inventory evidence
  when used, and the resulting setup or runtime blocker when they do not match;
- the explicit profile-request evidence and prohibition on ambient
  inheritance;
- the final typed role observation and authoritative effective-profile
  evidence;
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
