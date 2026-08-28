# Task Handoff

This is the root-level SE contract for assigning work to, observing, and
reporting a task after [Task Preflight](task-preflight.md) has passed. It is
shared by Feature and legacy Implement. It defines the handoff and
relay evidence, while the preflight reference owns the common gates and
authorization decisions.

## Contents

- [Handoff boundary](#handoff-boundary)
- [Prompt projection](#prompt-projection)
- [Controller observation and assigned-task bootstrap](#controller-observation-and-assigned-task-bootstrap)
- [Canonical title metadata](#canonical-title-metadata)
- [Title reconciliation](#title-reconciliation)
- [Role-profile request](#role-profile-request)
- [Role-profile observation](#role-profile-observation)
- [Execution-target observation](#execution-target-observation)
- [Observation record](#observation-record)
- [Update relay](#update-relay)
- [Failure and recovery evidence](#failure-and-recovery-evidence)
- [Final handoff result](#final-handoff-result)

## Handoff boundary

Create one handoff for one logical task assignment. It must point to the
validated preflight record and carry the invoking skill's own task profile and
topology. Do not invent a common profile or topology here.

For a required application-task role, create the handoff only for an
independently observable user-owned application task. A subordinate
delegation, optional support assignment, or other execution envelope cannot
receive, satisfy, or later inherit that required handoff.

The handoff must contain, or link to:

- the explicit user request and bounded objective;
- the source Feature Plan, source issue, or other durable input references;
- the role-specific target kind and allowed scope;
- for a repository-bound role, the frozen repository, remote, execution mode,
  base branch/SHA, intended head branch, worktree, and path envelope;
- for a control-plane role, the complete peer repository-observation set and
  explicit absence of a repository, checkout, worktree, or primary-repository
  binding;
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

## Prompt projection

Build every creation or resume prompt from the handoff fields as one flat
semantic assignment. Preserve the bounded objective, constraints, durable
source references, destination, requested role profile, validation contract,
and expected return evidence. Do not paste a parent prompt, conversation
transcript, or raw task/delegation transport envelope into a child prompt.

When source material arrives inside a transport wrapper, extract its semantic
payload and stable provenance, then discard the wrapper and any escaped wrapper
markup. Never nest one handoff envelope inside another or treat transport
metadata as user intent. This normalization must not drop a user constraint or
alter the assignment; retain any needed source message by reference instead of
embedding its raw envelope.

The projected prompt is internal control-plane content. It is not hosted
content, task identity, execution evidence, or durable plan authority.

## Controller observation and assigned-task bootstrap

The task controller owns the create or resume effect, independent post-effect
observation of the stable assigned-task identity and state, and binding of the
bootstrap result to that identity. The assigned task owns the authoritative
bootstrap self-check inside its first execution turn. These checks are
complementary:

1. before the effect, the controller completes Task Preflight and freezes the
   explicit profile request and destination;
2. after the effect, the controller independently observes the stable task
   identity, current state, and title;
3. before role-owned planning, orchestration, implementation, repository, or
   hosted work, the assigned task reads its own authoritative task-scoped
   execution context, compares its effective profile with the handoff, observes
   its actual role-specific execution target, and returns the structured
   bootstrap result defined below;
4. before normal monitoring or update relay, the controller verifies that the
   bootstrap evidence identity exactly equals the stable assigned-task
   identity and completes title reconciliation.

The controller does not duplicate the assigned task's authoritative profile
read. Role-owned work waits for the assigned-task bootstrap, while normal
controller monitoring and relay wait for exact identity binding, role-target
comparison, and title reconciliation.

The controller and assigned task may run under intentionally different model
or reasoning profiles. Only the assigned task's authoritatively self-observed
values are compared with the handoff request. A generic child message such as
"my profile matches" is not sufficient. The accepted bootstrap is a typed
result derived from the authoritative task-scoped source and includes the
source task identity, requested and observed values, and evidence reference.

For a required role, bootstrap binding is valid only for the independently
observed user-owned application-task identity created or resumed under the
declared topology. An identity or result from subordinate delegation, optional
support, or another execution envelope is invalid and cannot be promoted into
the required handoff.

The authoritative source must expose the identity of the task whose effective
values it reports. That evidence identity must exactly equal the stable
assigned-task identity observed by the controller. Evidence from a different
task is `task-identity-mismatch`. When exact-task evidence is present but its
model or reasoning differs from the request, use
`effective-profile-mismatch` instead. A missing evidence task identity remains
`unsupported-runtime` because no exact-task comparison is possible.

An assigned planner, orchestrator, Feature Worker, or optional task that has
already started from a valid handoff does not create or resume another task for
its own required role. It performs only the assigned-task bootstrap and then
enters its role-owned workflow. In the Implement hierarchy, a verified
orchestrator subsequently becomes the task controller for Feature Workers, and
each Feature Worker applies the same non-recursive bootstrap rule.

The bootstrap self-check reuses the handoff's request and existing workflow
outcomes. Its typed result is task handoff evidence, not an additional
workflow state, ledger column, replacement task, or second state machine.

## Canonical title metadata

Every task governed by this Feature and legacy Implement contract receives a
deterministic display-title request using the established SE Implement grammar:

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

Compute the canonical title before task creation and include this exact
plain-text line in the projected creation prompt:

```text
Canonical display title: <canonical display title>
```

This line is a best-effort first-render hint when the live creation capability
cannot initialize title metadata. It is never authoritative metadata, identity,
or verification evidence. Request the canonical title during task creation
when the live capability supports that effect, then independently read it back
after the stable task identity is known. Whether or not the prompt hint appears
to work, creation acceptance is never title verification and the bounded title
reconciliation below remains mandatory before normal monitoring or update
relay begins.

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
  prompt_hint_included: true
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
Authoritative post-effect bootstrap observation remains mandatory.

## Role-profile observation

Every application task created or resumed under a skill-owned profile must
carry a typed role observation. Resolve the exact requested model and reasoning
before the task effect. When a profile selects reasoning per assignment, such
as one Implement Feature Worker per Feature, freeze that resolved value in the
handoff before startup. Bind the observation to the handoff's explicit
`profile_request`; effective-profile readback never substitutes for that
pre-effect request evidence.

After the controller independently observes the stable task identity, the
assigned task reads its effective model and reasoning from its authoritative
task-scoped runtime view. A request payload, creation receipt, configured
default, generic conversation text, cached record, or inferred value is not
authoritative readback. Bind the observation to the same exact task by
recording the source task identity in the structured bootstrap result. If an
unexpected post-effect readback omits either value, retain that field as
`null` with the authoritative evidence reference before blocking; never
fabricate or silently omit it.

For a required role, both effective values must be present and exactly match
the resolved requested values before role-owned work, normal monitoring, or
update relay. A missing or unobservable value, an unstructured self-report, or
a missing evidence task identity is `blocked` with `blocker:
unsupported-runtime`. Present authoritative values bound to the exact assigned
task that differ from the request are `blocked` with `blocker:
effective-profile-mismatch`. A present evidence task identity that differs
from the controller-observed task is `blocked` with `blocker:
task-identity-mismatch`. Preserve the observed task identity and reconcile the
original effect; never create a replacement task merely to seek a matching
profile. For an optional role instantiated as its own application task, apply
the invoking skill's declared fallback and do not claim delegated work unless
the task identity and structured bootstrap result were both verified.

Apply this decision table to the assigned task's bootstrap gate and the
controller's identity binding.

| case_id | exact assigned-task evidence | effective values | comparison | controller identity binding | required result |
| --- | --- | --- | --- | --- | --- |
| exact-match | authoritative and identity-matched | present | exact match | exact | continue |
| observed-profile-differs | authoritative and identity-matched | present | model or reasoning differs | exact | `effective-profile-mismatch` |
| missing-effective-values | authoritative and identity-matched | missing or unobservable | unavailable | exact | `unsupported-runtime` |
| wrong-task-identity | authoritative but bound to another task | any | invalid for this assignment | different | `task-identity-mismatch` |
| missing-task-identity | authoritative source omits task identity | any | unavailable | unavailable | `unsupported-runtime` |
| unstructured-self-report | conversational claim only | any | not authoritative | exact or unavailable | `unsupported-runtime` |

The assigned task records the authoritative comparison in its bootstrap
result. The controller verifies only that the result is structured, references
the frozen request, and is bound to the exact stable task identity it observed.
Never substitute the controller's effective profile for the assigned task's
readback.

The role observation is evidence, not a new state machine. Do not add an
`accepted` or routing-status field: the invoking workflow retains its existing
`ready`, fallback, `complete`, and `blocked` outcomes. Do not add generic
sandbox or permission fields here. Repository, host, checkout, worktree, and
control-plane repository-set boundaries remain with their existing owners; a
skill that requires another execution-boundary fact must define its semantic
requirement itself.

## Execution-target observation

After the controller independently observes the stable task identity, the
assigned task inspects its actual execution target and compares it with the
target frozen by preflight. For `repository-bound`, observe the repository
identity, Git/worktree root, remote identity, execution mode, base branch/SHA,
intended head branch, path-envelope binding, and every stricter ref or HEAD fact
required by the skill-owned topology. For `control-plane`, verify that no Git
checkout or worktree is required and reconcile one authoritative observation
for every selected repository without selecting a primary repository.

The execution-target record describes where work can actually happen. A
request payload, creation receipt, display title, saved-project association,
or project-root metadata cannot substitute for Git and filesystem
observations. Application routing metadata is optional context only: do not
compare, refresh, retry, or block on it.

Apply these outcomes once to the same stable task:

1. complete matching observations permit the handoff to continue;
2. a missing required observation is `unsupported-runtime`;
3. a present target-kind, repository-set, repository, remote, checkout,
   worktree, branch, path-envelope, ref, base, or HEAD difference is
   `execution-target-mismatch`.

Preserve the same task identity for every blocked result. Never create a
replacement task or switch execution targets merely to seek matching evidence.

```yaml
execution_target_observation:
  request_ref: "<frozen preflight target>"
  target_kind: repository-bound
  repository_identity: "<observed repository>"
  repository_root: "<observed Git root>"
  worktree_root: "<observed isolated worktree>"
  remote_identity: "<observed remote>"
  execution_mode: isolated-worktree
  base_branch: "<observed selected branch>"
  base_sha: "<observed full SHA>"
  head_branch: "<frozen intended Worker branch>"
  path_envelope_ref: "<observed allowed write envelope>"
  comparison: exact-match
```

A control-plane observation uses the exclusive alternate shape:

```yaml
execution_target_observation:
  request_ref: "<frozen preflight target>"
  target_kind: control-plane
  execution_mode: projectless-control-plane
  repository_binding: none
  selected_repository_observations:
    - repository_identity: "<observed repository>"
      remote_identity: "<observed remote>"
      observation_ref: "<authoritative observation>"
  primary_repository: none
  comparison: exact-match
```

## Observation record

After creation or resume, append an authoritative observation with these
minimum fields:

```yaml
task_observation:
  requested_title: "<canonical display title>"
  observed_title: "<final read-back display title or null>"
  title_status: verified
  title_reconciliation_ref: "<bounded reconciliation evidence>"
  task_identity: "<exact observed task identity>"
  state: "<observed operational state>"
  identity_independently_observed: true
  assigned_task_bootstrap:
    task_profile_ref: "<skill-owned profile>"
    role: "<profile role>"
    assignment_ref: "<planner, orchestration, Feature, or other stable scope>"
    profile_request_ref: "<explicit profile-request evidence>"
    evidence_task_identity: "<task identity exposed by the authoritative source>"
    evidence_ref: "<authoritative task-scoped runtime readback>"
    source_read_by: assigned-task
    role_observation:
      requested_model: "<assignment-resolved model>"
      requested_reasoning: "<assignment-resolved reasoning>"
      observed_model: "<authoritative effective model or null>"
      observed_reasoning: "<authoritative effective reasoning or null>"
    execution_target_ref: "<assigned-task target observation>"
  controller_identity_bound: true
```

The observation must be compared with the preflight target and the resolved
skill-owned profile, and its
`assigned_task_bootstrap.profile_request_ref` must prove the complete resolved
profile was actively requested. A missing explicit request, ambient
inheritance, or a mismatch in effective model, effective reasoning, task
identity, role-specific execution target, or state is a blocker until reconciled.
Require `assigned_task_bootstrap.evidence_task_identity` to equal the enclosing
`task_observation.task_identity`; a different identity is not evidence about
the assigned task. The independently observed task identity and the assigned
task's authoritative bootstrap readback are execution evidence; titles and
other display metadata are not.

Application routing metadata is outside this minimum observation and has no
effect on bootstrap or execution-target success.

## Update relay

Do not begin normal monitoring or relay a partial update until the assigned
task bootstrap is bound to the stable task identity, its required role and
execution-target observations match, and title reconciliation has produced
either `verified`, `title-unverified`, or `title-drift`. The title warning
outcomes do not suspend otherwise valid work.

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

Monitoring is change-driven. Retain one observation lineage per stable task.
A timeout, silence, or observation identical to the last accepted identity,
state, and evidence fingerprint remains pending evidence; it must not produce
a heartbeat, status-only or "continue" message, duplicate request, task
resumption, overlapping observation, or immediate no-work cycle. Prefer
event-driven observation. When repeated observation is the only supported
mechanism, lengthen the interval after unchanged results within the caller's
authority and deadline, reset it after a material change, and fairly
interleave independent lineages.

Relay once for a new bootstrap result, state transition, actionable evidence
fingerprint, authority decision, execution-target change, or terminal report.
Coalesce facts observed together for the same task. One identity-bound request
for a missing terminal report is allowed; reconcile its effect before any
repeat. This policy adds no persisted state or runtime mode.

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
Reconciliation may repeat only the original application-task effect after
authoritative `not-applied` evidence. It never authorizes a different execution
topology or promotion of an optional assignment into the required role.

Apply the same read-before-retry rule to an ambiguous title adjustment, but do
not retry that adjustment. Preserve the task and finalize its title status from
the authoritative evidence that remains available.

## Final handoff result

The final relay must preserve the exact task identity and include:

- the final independently observed task identity and state plus the assigned
  task's authoritative profile and execution-target evidence;
- the explicit profile-request evidence and prohibition on ambient
  inheritance;
- the final typed assigned-task bootstrap, role observation, controller
  identity binding, and authoritative effective-profile evidence;
- the resulting `unsupported-runtime`, `effective-profile-mismatch`,
  `task-identity-mismatch`, or `execution-target-mismatch` blocker when a
  required gate does not pass;
- the assigned-task bootstrap self-check outcome;
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
