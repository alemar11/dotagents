# Task Preflight

This is the root-level SE contract for any workflow that creates, resumes, or
monitors a task in the ChatGPT/Codex application. Feature and Implement skills
must load it before attempting a task handoff. It defines required outcomes and
evidence; it does not define an application interface.

## Contents

- [Scope and ownership](#scope-and-ownership)
- [Required preflight gates](#required-preflight-gates)
- [Canonical preflight record](#canonical-preflight-record)
- [Fail-closed rule](#fail-closed-rule)

## Scope and ownership

The contract owns the common gates for task creation and observation:

- explicit invocation;
- live application capabilities;
- authoritative assigned-task bootstrap for effective model and reasoning;
- independent stable task identity and state observation;
- deterministic display-title capability and bounded correction authority;
- partial and final update relay;
- Git execution-target verification;
- recovery after an ambiguous effect;
- optional runtime capabilities declared by the invoking skill.

The invoking skill owns its task profile and topology. This contract contains
no model, reasoning, worker, or topology default. GitHub issue planning and
publication remain governed by the invoking skill's own contract.

The invoking skill also owns the requested model and reasoning values for each
role and resolves any assignment-specific choice before task creation or
resume. This contract owns the live capability gate for actively requesting
those values and receiving an authoritative bootstrap result from the assigned
task; [Task Handoff](task-handoff.md) owns the typed task-owned observation,
comparison, and controller identity binding.

The same ownership split applies to the execution target. This preflight owns
freezing the expected repository, execution mode, remote, and any
topology-required checkout or base facts. Task Handoff owns the assigned task's
post-effect observation and comparison against that target. The controller may
request an application destination when creating or resuming a task, but
saved-project association, visibility, and project-root metadata are not task,
bootstrap, or Git execution evidence and never participate in a gate.

The `task controller` is the session that creates or resumes one assigned
application task, independently observes its stable identity and state, and
binds the task-owned bootstrap result to that exact identity. The `assigned
task` is the planner, orchestrator, Feature Worker, or separately instantiated
optional role named by the handoff. The task controller's own effective model
and reasoning are not assignment evidence and must never be compared with the
assigned role's requested profile. The two profiles may differ intentionally.

Preflight runs in the task controller before the effect and verifies that the
runtime can request the assigned profile, observe the resulting stable task
identity, and relay the assigned task's bootstrap result. It does not perform
the value comparison before the assigned task exists. Task Handoff owns the
assigned task's authoritative bootstrap comparison and the controller's
post-effect identity binding.

An explicit invocation of a task-managed Feature or Implement workflow is the
user's explicit request for the required user-owned application tasks declared
by that workflow. It grants `task_creation_authorization` for exactly those
roles without a second permission prompt unless the user explicitly forbids
task creation. It also selects the exact required role profiles. For every
required role, and for every optional role instantiated as its own application
task, the task controller must actively request the resolved model and
reasoning on creation and resume. Omitting either value and relying on an
ambient, inherited, configured, or provider-default profile is prohibited,
even when the resulting effective values happen to match. This selection
authorizes only the roles and profiles declared by the invoked skill; it does
not permit another task, model, reasoning value, or execution topology.

The invoking skill must pass a reference to its complete task profile and the
roles required by the selected topology. The preflight verifies the live
runtime for every supplied role; it does not select, rewrite, downgrade, or
replace a role. For a multi-role profile, every role's explicit request and
assigned-task bootstrap path must be supported before the first role starts.

## Required preflight gates

### 1. Explicit invocation

The user must explicitly request the workflow that creates or monitors a task.
Do not infer permission from a feature description, a title, a previous task,
or the fact that the current session can access the application. An implicit or
ambiguous request is `blocked` before any task effect.

For a task-managed Feature or Implement workflow, its explicit invocation is
that request. Record task creation as `granted` for only the required roles in
the declared topology and do not ask for a second confirmation. An explicit
user prohibition overrides the workflow request and blocks the required
topology.

### 2. Live application capabilities

Verify the current application runtime immediately before the first task
effect. The live capability check must establish all capabilities required by
the requested topology:

- create or resume a task;
- independently observe the stable task identity and state after the effect;
- let the exact assigned task read its authoritative task-scoped execution
  context and compare its effective model and reasoning with the handoff;
- receive a structured bootstrap result whose evidence task identity can be
  bound to the independently observed stable task identity;
- let the assigned task inspect and compare its actual Git execution target;
- receive partial updates and a final update;
- relay those updates to the invoking session.

Only an independently observable user-owned application task can satisfy a
required application-task role. A subordinate in-task delegation, optional
support assignment, or other non-application execution envelope never
satisfies or substitutes for a required role.

An authoritative task-scoped execution context satisfies effective-profile
readback when it is accessible to the exact assigned task, identifies that
same task, and supplies the values used in its structured bootstrap result.
The controller does not need direct access to that raw source; it must
independently observe the stable task identity and require the bootstrap
evidence identity to match it exactly. A generic conversational self-report is
not a structured bootstrap result.

Documentation, cached metadata, an earlier receipt, or a static validator is
not evidence that a live capability is available. If creation, observation, or
monitoring cannot be verified, fail closed before creating or retrying a task.

Before recording a required role as verified, establish that the current
runtime can accept an active request for the complete resolved profile,
observe the resulting stable task identity, and relay the exact assigned
task's authoritative bootstrap result. A request payload, configured default,
creation receipt, unstructured conversation text, or locally inferred value is
not effective-profile evidence. `roles_verified: true` means every required
role supports that request and bootstrap path; it does not claim that a task
has already been created or that its effective profile has matched. The
handoff supplies that proof after stable task identity observation.

If the runtime can create a task only by inheriting one or both required
profile values, the fixed-profile capability gate has not passed. Stop before
the task effect instead of creating a task and checking which defaults it
received afterward.

Application routing metadata is separate from task identity and Git
execution-target verification. The controller independently observes the
resulting task's stable identity and state, and the assigned task verifies the
target that can affect work: repository identity, checkout or worktree,
remote, and any base facts required by the skill-owned topology. Do not
compare, refresh, or retry application project metadata as part of either
verification.

The profile capability check is equally strict for required roles. If any
required role is not supported by the live runtime, or the exact assigned task
cannot later read its effective profile authoritatively and return the bound
bootstrap evidence, the result is `blocked` with `blocker:
unsupported-runtime`. There is no automatic model, reasoning, or
required-topology fallback. A skill may declare optional roles or optional
capabilities with an explicit parent or serial fallback. Those facts must be
recorded and must not be reported as delegated work unless a worker was
actually started and its bootstrap identity was verified.

### Optional runtime capabilities

When the invoking skill declares them, inspect delegation and goal capability
once before the first optional effect. Record delegation as available,
unavailable, or unknown, and record any observed worker capacity separately
from workers that actually started. Delegation unavailability selects the
skill-owned fallback and does not block a required parent task.

Goal tools are also optional. When unavailable, preserve the skill's objective
in its task or run report and continue. A resumable user-input wait must not be
converted into a blocked goal merely because the goal runtime has no explicit
unblock operation.

For every role whose profile declares a deterministic display title, also
inspect the live capability to request that title, observe it independently,
correct it after the stable task identity is known, and preserve enough
attempt evidence to prevent replay after recovery. Record unavailable title
initialization, correction, or recovery evidence as a display-metadata
limitation. It does not block an otherwise verifiable task topology, but it
must not be omitted from the preflight or later reported as verified.
The handoff's best-effort plain-text title hint does not make title
initialization available and cannot satisfy title observation or correction.

### 3. Verifiable destination

Resolve one exact Git execution destination for every task before creation.
Independently verify:

- `repository_identity` and `remote_identity`;
- the required execution mode, such as the exact local checkout or an isolated
  worktree;
- any exact checkout, starting ref, base SHA, or path-envelope constraint owned
  by the invoking topology.

Freeze these facts before the task effect. In a multi-repository run, verify
each repository target separately. A repository name copied from the request,
a display title, or application project metadata alone is insufficient.

An application destination may be requested as routing intent, but its
association or display metadata is outside the frozen target and is never
compared during bootstrap.

The assigned task later observes the corresponding actual Git facts. A present
difference is `execution-target-mismatch`. If the runtime cannot expose a
required target fact at all, use `unsupported-runtime`. An absent saved-project
identity or project-root field has no effect on either classification.

### 4. Task identity and assigned-task bootstrap

After creating or resuming a task, the controller independently observes the
stable `task_identity` and current `state` from the authoritative application
view. The assigned task then performs the bootstrap self-check defined by Task
Handoff and returns its typed effective-role and destination observations
before beginning role-owned work. A display title, caller-supplied identifier,
echoed request profile, or unstructured conversational claim is not identity
or effective-profile evidence.

The task controller owns creation/resume, stable identity observation, and
binding of the structured bootstrap result. The assigned task owns the
authoritative read of its own task-scoped execution context and every
requested-versus-observed comparison. The controller does not duplicate that
profile read. The assigned task also observes the actual Git execution target;
the controller compares that structured observation with the frozen target.

The assigned task compares its effective model and reasoning with the
assignment-specific values resolved from the skill-owned profile and returns
that typed observation in the bootstrap result. Never compare the task
controller's own profile with the assigned role. A missing or unobservable
exact-task observation for a required role is `blocked` with `blocker:
unsupported-runtime`; an authoritative exact-task observation whose effective
model or reasoning differs from the request is `blocked` with `blocker:
effective-profile-mismatch`. Both stop before normal monitoring or update
relay. Preserve and reconcile the observed task identity; do not create a
replacement. For an optional role, use only the invoking skill's declared
parent or serial fallback and do not claim delegated work.

A missing authoritative evidence task identity is `unsupported-runtime`; a
present evidence identity that differs from the controller-observed task is
`task-identity-mismatch`. A missing required execution-target observation is
`unsupported-runtime`; present repository, remote, checkout, worktree,
or base values that differ from the frozen target are
`execution-target-mismatch`. Project metadata never participates in these
comparisons.

A matching effective readback does not repair a missing explicit profile
request. Require both the pre-effect request evidence owned by the handoff and
the post-effect effective-profile observation for the same task.

The same identity-and-bootstrap boundary applies after a resume, a host
change, a monitoring gap, or a final update. Do not report a task as running
or complete from an unverified receipt or an unbound bootstrap result.

### 5. Separate authorization scopes

Record these decisions independently:

- `task_creation_authorization`: permission to create or resume the task in
  the application;
- `title_adjustment_authorization`: permission to correct the same declared
  deterministic title at most once after the stable task identity is observed;
- `github_mutation_scope`: the exact requested GitHub issue, branch,
  pull-request, review, relation, label, or comment mutations in scope for the
  explicit invoking SE request. These writes are implicitly authorized by the
  invocation; no second confirmation is required.

Task creation and GitHub mutation remain separate scopes even when the same
explicit invocation independently grants both. Task authority never broadens
GitHub mutation scope, and GitHub authority never supplies task authority. The
invoking skill's declared topology bounds task authority; the selected issues
and delivery contract bound GitHub authority. The workflow must still verify
exact repository, operation, identity, and read-after-write evidence. Keep
bounded title-adjustment authority separately visible as described below.

When an explicit invocation authorizes creation of a task whose skill-owned
profile declares a canonical title, the bounded correction of that same title
is part of the requested task initialization unless the user explicitly
forbids renaming. Record that authority separately because correction is a
distinct application effect. It never authorizes arbitrary or later lifecycle
renames.

The same explicit invocation authorizes the task controller to request the
exact model and reasoning declared by the skill-owned profile. This is part of
the bounded task-creation or resume authority, not permission to select a
different profile or rely on ambient inheritance.

### 6. Reconciliation before retry

An error, timeout, disconnected monitor, or incomplete receipt is an
ambiguous effect, not proof that no task was created. Before any retry:

1. re-observe the original destination and the current application state;
2. search for the exact task effect using independently observed identity and
   scope;
3. record whether the prior effect was `applied`, `not-applied`, or
   `unknown`;
4. retry only when authoritative evidence proves `not-applied` and the live
   runtime permits a new attempt.

If reconciliation cannot distinguish those outcomes, keep the run blocked and
do not create a replacement task.

## Canonical preflight record

The following field names are the common minimum record. Values are examples;
the invoking skill may add run-specific evidence without changing their
meaning.

```yaml
preflight:
  invocation:
    explicit: true
  profile:
    reference: "<skill-owned task profile>"
    request_mode: explicit
    ambient_inheritance: forbidden
    roles_verified: true
  capabilities:
    create_task: available
    observe_task_identity: available
    request_explicit_role_profile: available
    assigned_task_bootstrap: available
    receive_bootstrap_result: available
    observe_execution_target: available
    monitor_task: available
    relay_partial_updates: available
    relay_final_update: available
    request_display_title: available
    adjust_display_title: available
  optional_capabilities:
    delegation: available
    observed_worker_capacity: null
    goals: available
    effective_mode: parallel-analysis
  target:
    repository_identity: "<independently observed repository>"
    remote_identity: "<independently observed remote>"
    execution_mode: "<exact-local-checkout or isolated-worktree>"
    checkout_constraint: "<topology-owned checkout requirement>"
    starting_ref: "<required ref or null>"
    base_sha: "<required full SHA or null>"
    independently_verified: true
  authorization:
    task_creation: granted
    title_adjustment: granted-for-declared-title
    github_mutation_scope: implicit-for-declared-request
  outcome: ready
```

For a blocked preflight, retain the observations that are available and record
the exact missing capability, authorization, destination proof, or recovery
evidence. Do not replace it with a fabricated task identity or a successful
status.

## Fail-closed rule

If the ChatGPT/Codex application, live task creation, independent stable task
identity observation, assigned-task authoritative bootstrap, or
monitoring/relay path is unavailable, the outcome is `blocked`. The skill must
return the smallest recovery input and stop before the affected role-owned
effect. It must not claim that a task is being monitored or completed until
the required live evidence is available.

If a required application task cannot be created, resumed, independently
observed by stable identity and state, or monitored, use `blocker:
unsupported-runtime`. Do not launch, continue, relabel, or promote a
subordinate delegation, optional support assignment, or other execution
envelope as the missing role. Reconciliation may retry only the original
application-task effect after authoritative `not-applied` evidence; it never
authorizes another execution topology.

The same fail-closed rule applies when the exact resolved model and reasoning
cannot be actively requested. Never omit a required profile value to obtain a
task receipt and never treat a coincidentally matching inherited profile as a
valid task initialization.

`unsupported-runtime` means that the required request, stable task identity,
authoritative assigned-task bootstrap capability, or required target
observation is unavailable, or that the exact task's required values remain
missing or unobservable. It does not describe a successful readback of
different effective values; that case is `effective-profile-mismatch`. A
present bootstrap evidence identity that differs from the controller-observed
assigned task is `task-identity-mismatch`, and a present execution-target
difference is `execution-target-mismatch`.

Saved-project association and project-root metadata are optional diagnostics
only. Do not infer, compare, refresh, retry, or block on them, and never use
them as a substitute for stable task identity or Git execution evidence.

A difference between the task controller's profile and the assigned role's
requested profile is not a mismatch. Only the exact assigned task's
authoritatively self-observed profile participates in the comparison.

A missing title-request or title-adjustment capability alone is not a topology
blocker because a title is display metadata. Continue only after recording the
limitation for the handoff's mandatory title-reconciliation outcome; never
convert missing title evidence into successful verification.

Lost or ambiguous title-attempt evidence also never blocks otherwise valid
task work, but it forbids another adjustment. Read the current title,
preserve the stable task identity, and report the resulting title warning.
